import cv2
import numpy as np
import math
import json

def cartesian_to_polar(x, y):
    """Convert Cartesian coordinates (x, y) to polar (rho, theta)."""
    rho = math.sqrt(x**2 + y**2)
    theta = math.atan2(-y, x) * 180 / math.pi  # Convert to degrees
    return {"rho": rho, "theta": theta}

def extract_edges(image_path):
    """Extract edges from the image using Canny edge detection."""
    # Load the image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at {image_path} could not be loaded.")
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    
    # Perform Canny edge detection
    edges = cv2.Canny(blurred, 100, 200)
    
    return edges

def extract_contours(edges):
    """Extract contours from the edge-detected image."""
    # Find contours from the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Simplify the contours to a set of points (you can filter by area if needed)
    contour_points = []
    for contour in contours:
        for point in contour:
            contour_points.append(tuple(point[0]))
    
    return contour_points

def create_toolpath(contour_points):
    """Create a toolpath with lines from the contour points."""
    toolpath = []
    visited_points = set()  # Set to track visited points
    
    for i in range(1, len(contour_points)):
        start_point = contour_points[i - 1]
        end_point = contour_points[i]
        
        # If the end point has already been visited, skip to the next unvisited feature
        if end_point in visited_points:
            continue
        
        # Convert points to polar coordinates
        start_polar = cartesian_to_polar(start_point[0], start_point[1])
        end_polar = cartesian_to_polar(end_point[0], end_point[1])
        
        # Create a line segment
        toolpath.append({
            "type": "line",
            "start": start_polar,
            "end": end_polar
        })
        
        # Mark the points as visited
        visited_points.add(start_point)
        visited_points.add(end_point)
    
    # After finishing a feature, backtrack along the same path to avoid overwriting
    for point in reversed(list(visited_points)):
        if point not in contour_points:  # Ensure we backtrack along the path
            continue
        # Backtrack by appending the same points in reverse order
        toolpath.append({
            "type": "line",
            "start": cartesian_to_polar(point[0], point[1]),
            "end": cartesian_to_polar(point[0], point[1])
        })

    return toolpath

def save_toolpath(toolpath, filepath="toolpath.TP"):
    """Save the toolpath to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(toolpath, f, indent=4)

def main():
    # Parameters for the image
    image_path = 'input_image.jpg'  # Update this with your image path

    # Extract edges from the image
    edges = extract_edges(image_path)

    # Extract contour points from the edges
    contour_points = extract_contours(edges)

    # Create the toolpath from the contour points
    toolpath = create_toolpath(contour_points)

    # Save the toolpath to a JSON file
    save_toolpath(toolpath)

if __name__ == "__main__":
    main()
