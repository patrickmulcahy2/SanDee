import math
import time
import json

from .config import socketio, reqPosition, settingsData, system_states, userInputs
from .utils import polar_to_cartesian, cartesian_to_polar
from .led_control import completion_flash

def follow_path(toolpath_filepath):
    try:
        with open(toolpath_filepath, 'r') as f:
            path_list = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading toolpath: {e}")
        return

    if not isinstance(path_list, list):
        raise ValueError(f"Expected a list of instructions, got {type(path_list)} instead.")

    total_instructions = len(path_list)

    for i, instruction in enumerate(path_list):

        system_states.statusPercent = int((i / total_instructions) * 100)

        check_pause()

        if check_cancel():
            break
            
        if isinstance(instruction, dict):
            if instruction["type"] == "line":
                move_straight(instruction["start"], instruction["end"])
            elif instruction["type"] == "arc":
                move_arc(instruction["start"], instruction["end"], instruction["radius"], instruction["direction"])
        else:
            print(f"Skipping invalid instruction: {instruction}")

    print(f"Completed toolpath from: {toolpath_filepath}")
    
    system_states.statusPercent = 100
    system_states.pauseStatus = False
    system_states.patterningStatus = False
    system_states.clearingStatus = False
    completion_flash() 

def feedrate_pauser(delta_rho, delta_theta, step_size):
    feedrate = userInputs["feedrate"]
    feedrateMax_rho = settingsData["feedrateMax_rho"]        #inches per second
    feedrateMax_theta = settingsData["feedrateMax_theta"]* 360 / 60 #degrees per second

    # Time needed to stay within each feedrate limit
    time_rho = delta_rho / feedrateMax_rho if feedrateMax_rho else 0
    time_theta = delta_theta / feedrateMax_theta if feedrateMax_theta else 0 
    time_vector = step_size / feedrate if feedrate else 0

    # Choose the maximum required time to respect all limits
    sleep_time = max(time_vector, time_rho, time_theta)
    socketio.sleep(sleep_time)

def check_pause():
    while system_states.pauseStatus:
        socketio.sleep(0.25)

def check_cancel():
    if not system_states.clearingStatus and not system_states.patterningStatus:
        print("Patern Cancelled!")
        return True
    else: 
        return False


def move_straight(start, end):
    step_size = settingsData["maxStepover"]

    x0, y0 = polar_to_cartesian(start["rho"], start["theta"])
    x1, y1 = polar_to_cartesian(end["rho"], end["theta"])

    dx = x1 - x0
    dy = y1 - y0
    distance = math.hypot(dx, dy)
    steps = max(1, int(distance / step_size))

    for i in range(1, steps + 1):
        xi = x0 + dx * i / steps
        yi = y0 + dy * i / steps
        rho, theta = cartesian_to_polar(xi, yi)

        # Compute deltas for this step
        delta_rho = abs(rho - reqPosition["rhoReq"])
        delta_theta = angular_diff(theta, reqPosition["thetaReq"])

        reqPosition["rhoReq"] = rho
        reqPosition["thetaReq"] = theta

        feedrate_pauser(delta_rho, delta_theta, step_size)

    # Snap to endpoint
    reqPosition["rhoReq"] = end["rho"]
    reqPosition["thetaReq"] = end["theta"]

def angular_diff(a1, a2):
    return abs((a1 - a2 + math.pi) % (2 * math.pi) - math.pi)

def move_arc(start, end, radius, direction):
    step_size = settingsData["maxStepover"]

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

    direction = direction.strip().upper()
    if direction not in {"CW", "CCW"}:
        raise ValueError("Invalid direction: must be 'CW' or 'CCW'")

    def is_ccw(center_x, center_y):
        a0 = math.atan2(y0 - center_y, x0 - center_x)
        a1 = math.atan2(y1 - center_y, x1 - center_x)
        return ((a1 - a0 + 2 * math.pi) % (2 * math.pi)) < math.pi

    ccw1 = is_ccw(cx1, cy1)
    cx, cy = (cx1, cy1) if (ccw1 and direction == "CCW") or (not ccw1 and direction == "CW") else (cx2, cy2)

    start_angle = math.atan2(y0 - cy, x0 - cx)
    end_angle = math.atan2(y1 - cy, x1 - cx)

    if direction == "CCW":
        angle_diff = (end_angle - start_angle) % (2 * math.pi)
    else:
        angle_diff = (start_angle - end_angle) % (2 * math.pi)

    arc_length = radius * angle_diff
    steps = max(1, int(arc_length / step_size))

    for i in range(1, steps + 1):
        angle = start_angle + (angle_diff * i / steps) * (1 if direction == "CCW" else -1)
        xi = cx + radius * math.cos(angle)
        yi = cy + radius * math.sin(angle)
        rho, theta = cartesian_to_polar(xi, yi)

        # Compute deltas for this step
        delta_rho = abs(rho - reqPosition["rhoReq"])
        delta_theta = angular_diff(theta, reqPosition["thetaReq"])

        reqPosition["rhoReq"] = rho
        reqPosition["thetaReq"] = theta

        feedrate_pauser(delta_rho, delta_theta, step_size)

    # Snap to endpoint
    reqPosition["rhoReq"] = end["rho"]
    reqPosition["thetaReq"] = end["theta"]



