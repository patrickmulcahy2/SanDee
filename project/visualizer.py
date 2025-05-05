import os
import json
import math
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend

import matplotlib.pyplot as plt


def polar_to_cartesian(rho, theta_deg):
    theta = math.radians(theta_deg)
    return rho * math.cos(theta), rho * math.sin(theta)

def draw_line(start, end, step_size=0.5):
    x0, y0 = polar_to_cartesian(start["rho"], start["theta"])
    x1, y1 = polar_to_cartesian(end["rho"], end["theta"])
    dx, dy = x1 - x0, y1 - y0
    distance = math.hypot(dx, dy)
    steps = max(1, int(distance / step_size))
    return [(x0 + dx * i / steps, y0 + dy * i / steps) for i in range(steps + 1)]

def draw_arc(start, end, radius, direction, step_size=0.5):
    x0, y0 = polar_to_cartesian(start["rho"], start["theta"])
    x1, y1 = polar_to_cartesian(end["rho"], end["theta"])

    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    chord_len = math.hypot(dx, dy)

    if radius < chord_len / 2:
        raise ValueError("Radius too small for arc between given points")

    h = math.sqrt(radius**2 - (chord_len / 2)**2)
    norm_dx, norm_dy = -dy / chord_len, dx / chord_len

    cx1 = mx + h * norm_dx
    cy1 = my + h * norm_dy
    cx2 = mx - h * norm_dx
    cy2 = my - h * norm_dy

    def is_ccw(cx, cy):
        a0 = math.atan2(y0 - cx, x0 - cy)
        a1 = math.atan2(y1 - cx, x1 - cy)
        return ((a1 - a0 + 2 * math.pi) % (2 * math.pi)) < math.pi

    ccw1 = is_ccw(cx1, cy1)
    cx, cy = (cx1, cy1) if (ccw1 and direction == "CCW") or (not ccw1 and direction == "CW") else (cx2, cy2)

    start_angle = math.atan2(y0 - cy, x0 - cx)
    end_angle = math.atan2(y1 - cy, x1 - cx)

    if direction == "CCW":
        angle_diff = (end_angle - start_angle) % (2 * math.pi)
        sign = 1
    else:
        angle_diff = (start_angle - end_angle) % (2 * math.pi)
        sign = -1

    arc_length = radius * angle_diff
    steps = max(1, int(arc_length / step_size))

    return [
        (
            cx + radius * math.cos(start_angle + sign * angle_diff * i / steps),
            cy + radius * math.sin(start_angle + sign * angle_diff * i / steps)
        )
        for i in range(steps + 1)
    ]

def generate_toolpath_image(filepath):
    with open(filepath, 'r') as f:
        toolpath = json.load(f)

    all_points = []

    for instruction in toolpath:
        if instruction["type"] == "line":
            points = draw_line(instruction["start"], instruction["end"])
        elif instruction["type"] == "arc":
            points = draw_arc(instruction["start"], instruction["end"],
                              instruction["radius"], instruction["direction"])
        else:
            print(f"Unknown instruction: {instruction}")
            continue
        all_points.extend(points)

    x_vals, y_vals = zip(*all_points)
    plt.figure(figsize=(6, 6))
    plt.plot(x_vals, y_vals, 'b-')
    plt.scatter(x_vals[0], y_vals[0], c='green', label='Start')
    plt.scatter(x_vals[-1], y_vals[-1], c='red', label='End')
    plt.axis('equal')
    plt.title(f"Toolpath Visualization")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.grid(True)

    # Save image
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    output_path = os.path.join(os.path.dirname(filepath), base_name + ".png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    return output_path

# Optional CLI usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python visualize_toolpath.py <toolpath_file.TP>")
        sys.exit(1)
    image_path = generate_toolpath_image(sys.argv[1])
    print(f"Image saved to: {image_path}")
