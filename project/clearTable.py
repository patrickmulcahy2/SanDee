import os
import json
import math

from .config import BASE_DIR, settingsData
from .parseToolpath import follow_path
from .utils import cartesian_to_polar, circle_height_to_width

output_dir = os.path.join(BASE_DIR, "toolpaths")
os.makedirs(output_dir, exist_ok=True)

CLEARING_FILEPATH_SPIRAL = os.path.join(output_dir, "clear-table_spiral.TP")
CLEARING_FILEPATH_HORIZONTAL = os.path.join(output_dir, "clear-table_horizontal.TP")


def clearTable():
    if settingsData["clearingType"] == "Spiral":
        generatedToolpath = generate_spiral_toolpath()
        filepath = CLEARING_FILEPATH_SPIRAL
    elif settingsData["clearingType"] == "Horizontal":
        generatedToolpath = generate_horizontal_toolpath()
        filepath = CLEARING_FILEPATH_HORIZONTAL
    else:
        print(f"Invalid clearing type: {settingsData['clearingType']}")
        return 

    save_toolpath_to_file(generatedToolpath, filepath)
    print(filepath)
    follow_path(filepath)
def generate_spiral_toolpath():
    max_rho = settingsData["rhoMax"]
    spiral_stepover = settingsData["clearingStepover"]
    theta_increment = 15  # degrees per arc segment
    rho_decrement = spiral_stepover / (360/15)

    toolpath = []
    current_rho = max_rho
    current_theta = 0
    rotation_angle = 0

    #Continue spiralling until within 0.05" of center 
    while current_rho > 0.05:
        next_theta = (current_theta + theta_increment) % 360
        rotation_angle += theta_increment

        next_rho = current_rho - rho_decrement

        arc_end = {"rho": next_rho, "theta": next_theta}

        toolpath.append({
            "type": "arc",
            "start": {"rho": current_rho, "theta": current_theta},
            "end": arc_end,
            "radius": (current_rho + next_rho) / 2,  #Average radius of two rhos
            "direction": "CCW"
        })
        
        current_theta = next_theta
        current_rho = next_rho

    return toolpath

def generate_horizontal_toolpath():
    max_rho = settingsData["rhoMax"]
    horizontal_stepover = settingsData["clearingStepover"]

    toolpath = []

    y_curr = max_rho - 0.5*horizontal_stepover
    x_half_width = circle_height_to_width(max_rho, y_curr) / 2
    curr_polarity = 1

    while y_curr > -(max_rho-(0.5*horizontal_stepover)):
        if curr_polarity == 1:
            x_start = -x_half_width
            x_end = x_half_width
        else:
            x_start = x_half_width
            x_end = -x_half_width

        rho_start, theta_start = cartesian_to_polar(x_start, y_curr)
        rho_end, theta_end = cartesian_to_polar(x_end, y_curr)


        toolpath.append({
            "type": "line",
            "start": {"rho": rho_start, "theta": theta_start},
            "end": {"rho": rho_end, "theta": theta_end},
        })

        y_curr -= horizontal_stepover
        x_half_width =  circle_height_to_width(max_rho, y_curr) / 2
        curr_polarity *= -1

    return toolpath


def cartesian_to_polar(x, y):
    rho = math.sqrt(x**2 + y**2)  # Radius (distance from the origin)
    thetaRads = math.atan2(y, x)  # Angle in radians
    theta = math.degrees(thetaRads)
    return rho, theta

def save_toolpath_to_file(toolpath, filepath):
    with open(filepath, "w") as f:
        json.dump(toolpath, f, indent=4)

    print(f"Toolpath saved to {filepath}")