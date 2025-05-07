import os
import json
import math

from flask import render_template, request, redirect, url_for, session, jsonify

from .config import settingsData, settingsPID, app, socketio, BASE_DIR, settingsData


# Path to the toolpath files
output_dir = os.path.join(BASE_DIR, "toolpaths")
os.makedirs(output_dir, exist_ok=True)

raw_path = []
current_path = []

current_path_TP = []

mirror_X = False
mirror_Y = False
circular_pattern = 0
smoothing_magnitude = 0
end_snap = "Origin"
start_snap = "Origin"


################################################
########## SETTINGS SOCKET HANDLERS ############
################################################
def init_toolpathCreator_handlers():
    @socketio.on('request_path')
    def request_path():
        socketio.emit("plot_path", current_path)

    @socketio.on('new_path_sent')
    def new_path(path):
        global raw_path
        raw_path = raw_path + path
        applyModifiers()

    @socketio.on('mirror_x')
    def mirror_x(boolean):
        global mirror_X
        mirror_X = boolean
        applyModifiers()

    @socketio.on('mirror_y')
    def mirror_y(boolean):
        global mirror_Y
        mirror_Y = boolean
        applyModifiers()

    @socketio.on('pattern_path')
    def pattern_path(value):
        global circular_pattern
        circular_pattern = value
        applyModifiers()

    @socketio.on('smooth_path')
    def smooth_path(value):
        global smoothing_magnitude
        smoothing_magnitude = value
        applyModifiers()

    @socketio.on('snap_path')
    def snap_path(snap_direction_emit, snap_edge_emit):
        global end_snap, start_snap
        if snap_edge_emit == "rho-start-toggle":
            start_snap = snap_direction_emit
        elif snap_edge_emit == "rho-end-toggle":
            end_snap = snap_direction_emit
        applyModifiers()


    @socketio.on('clear_canvas')
    def clear_canvas():
        global current_path, raw_path, current_path_TP
        raw_path = []
        current_path = []
        current_path_TP = []


    @socketio.on('save_path')
    def save_path(filename):
        # Ensure the filename has a .TP extension
        if not filename.lower().endswith('.tp'):
            filename += '.TP'

        filepath = os.path.join(output_dir, filename)

        normalize_path()
        convert_to_TP()

        with open(filepath, "w") as f:
            json.dump(current_path_TP, f, indent=4)

        print(f"Toolpath saved to {filepath}")


# Handlers for path modifiers 
def smooth():
    global current_path

    if smoothing_magnitude <= 0 or len(current_path) < 3:
        return

    # Convert smoothing magnitude (0–100) into window size (e.g., 1–25)
    window = max(1, int((smoothing_magnitude / 100) * 25))

    # Convert polar to cartesian
    cartesian_path = [
        (p["rho"] * math.cos(math.radians(p["theta"])), p["rho"] * math.sin(math.radians(p["theta"])))
        for p in current_path
    ]

    smoothed_path = []
    for i in range(len(cartesian_path)):
        x_sum = 0
        y_sum = 0
        count = 0

        # Apply centered moving average
        for j in range(-window, window + 1):
            idx = i + j
            if 0 <= idx < len(cartesian_path):
                x_sum += cartesian_path[idx][0]
                y_sum += cartesian_path[idx][1]
                count += 1

        if count > 0:  # Avoid division by zero
            x_avg = x_sum / count
            y_avg = y_sum / count

            rho = max(0, math.hypot(x_avg, y_avg))  # Ensure rho is non-negative
            theta = math.degrees(math.atan2(y_avg, x_avg)) % 360  # Normalize theta to 0-360

            smoothed_path.append({"rho": rho, "theta": theta})
        else:
            smoothed_path.append(current_path[i])  # Preserve the original if no valid smoothing

    current_path = smoothed_path

def snap():
    global current_path

    if not raw_path:
        return

    snapped_path = current_path.copy()
    min_points = 24

    def interpolate_snap(start_point, end_point, num_points):
        interpolated = []
        for i in range(1, num_points + 1):
            t = i / (num_points + 1)
            rho = (1 - t) * start_point["rho"] + t * end_point["rho"]
            # Ensure smooth angular interpolation (handle angle wrapping)
            delta_theta = (end_point["theta"] - start_point["theta"] + math.pi) % (2 * math.pi) - math.pi
            theta = start_point["theta"] + t * delta_theta
            interpolated.append({"rho": rho, "theta": theta})
        return interpolated

    edge_rho = 1

    # Snap start
    if start_snap == "Origin":
        start = snapped_path[0]
        end = {"rho": 0, "theta": start["theta"]}
        interpolated = interpolate_snap(end, start, min_points)
        snapped_path = [end] + interpolated + snapped_path

    elif start_snap == "Edge":
        start = snapped_path[0]
        if start["rho"] < edge_rho:
            end = {"rho": edge_rho, "theta": start["theta"]}
            interpolated = interpolate_snap(end, start, min_points)
            snapped_path = [end] + interpolated + snapped_path

    # Snap end
    if end_snap == "Origin":
        start = snapped_path[-1]
        end = {"rho": 0, "theta": start["theta"]}
        interpolated = interpolate_snap(start, end, min_points)
        snapped_path += interpolated + [end]

    elif end_snap == "Edge":
        start = snapped_path[-1]
        if start["rho"] < edge_rho:
            end = {"rho": edge_rho, "theta": start["theta"]}
            interpolated = interpolate_snap(start, end, min_points)
            snapped_path += interpolated + [end]

    current_path = snapped_path

def mirror():
    global current_path

    if not mirror_X and not mirror_Y:
        return

    mirrored_points = []

    for point in current_path:
        rho = point["rho"]
        theta = point["theta"]

        # Always keep the original
        mirrors = set()

        if mirror_X:
            mirrors.add((rho, (180 - theta) % 360))
        if mirror_Y:
            mirrors.add((rho, (-theta) % 360))
        if mirror_X and mirror_Y:
            mirrors.add((rho, (180 + theta) % 360))

        for rho_m, theta_m in mirrors:
            # Normalize angle
            theta_rad = math.radians(theta_m)
            theta_rad = math.atan2(math.sin(theta_rad), math.cos(theta_rad))
            theta_deg = math.degrees(theta_rad) % 360
            mirrored_points.append({"rho": rho_m, "theta": theta_deg})

    current_path.extend(mirrored_points)

def pattern():
    global current_path, circular_pattern

    if circular_pattern <= 1 or not current_path:
        return  # Nothing to do

    patterned_path = []
    angle_step = 360 / circular_pattern

    for i in range(circular_pattern):
        angle_offset = i * angle_step
        for point in current_path:
            new_theta = point["theta"] + angle_offset
            patterned_path.append({
                "rho": point["rho"],
                "theta": new_theta
            })

    current_path = patterned_path

    
def applyModifiers():
    global current_path
    current_path = raw_path.copy()
    smooth()
    snap()
    mirror()
    pattern()

    socketio.emit("plot_path", current_path)

def visualize_path():
    pass

def convert_to_TP():
    global current_path_TP
    current_path_TP = []
    
    # Helper function to determine if we have a line or arc
    def is_line(start, end):
        # For simplicity, assume all moves are straight lines
        return True  

    # Convert current_path (a list of polar points) into the TP instructions
    if len(current_path) < 2:
        print("Not enough points to create toolpath.")
        return

    # Loop through the points to create lines or arcs
    for i in range(len(current_path) - 1):
        start_point = current_path[i]
        end_point = current_path[i + 1]
        
        # If it's a straight line
        if is_line(start_point, end_point):
            current_path_TP.append({
                "type": "line",
                "start": start_point,
                "end": end_point
            })
        else:
            # If it's an arc, calculate the necessary radius and direction
            # This is a placeholder for arc calculation
            radius = 1.0  # Example radius, replace with actual calculation
            direction = "CW"  # Example direction, replace with actual logic
            current_path_TP.append({
                "type": "arc",
                "start": start_point,
                "end": end_point,
                "radius": radius,
                "direction": direction
            })

def normalize_path():
    global current_path

    rho_max = settingsData.get("rhoMax", 1.0)
    if not isinstance(rho_max, (int, float)) or rho_max <= 0:
        print("Invalid rhoMax in settingsData. Skipping rho adjustment.")
        return

    adjusted_path = []
    for point in current_path:
        scaled_rho = max(0, min(point["rho"] * rho_max, rho_max))  # Clamp to [0, rho_max]
        adjusted_path.append({
            "rho": scaled_rho,
            "theta": point["theta"] % 360 
        })

    current_path = adjusted_path

################################################
############### TOOLPATH  ROUTES ###############
################################################
@app.route("/toolpath_creator")
def toolpath_hub():
    return render_template("toolpath_creator.html")