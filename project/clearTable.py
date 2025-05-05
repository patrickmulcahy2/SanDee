import os
import json
import math

from .config import BASE_DIR, settingsData
from .parseToolpath import follow_path

output_dir = os.path.join(BASE_DIR, "toolpaths")
os.makedirs(output_dir, exist_ok=True)

CLEARING_FILEPATH = os.path.join(output_dir, "clear-table.TP")

def clearTable():
    generatedToolpath = generate_spiral_toolpath()
    save_toolpath_to_file(generatedToolpath)
    print(CLEARING_FILEPATH)
    follow_path(CLEARING_FILEPATH)

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


def save_toolpath_to_file(toolpath):
    with open(CLEARING_FILEPATH, "w") as f:
        json.dump(toolpath, f, indent=4)

    print(f"Toolpath saved to {CLEARING_FILEPATH}")