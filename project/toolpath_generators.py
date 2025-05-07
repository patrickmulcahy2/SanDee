import math
import json

def generate_flower_toolpath(A=5.0, k=6, revolutions=6, step_deg=5):
    toolpath = []
    theta_vals = list(range(0, int(revolutions * 360), step_deg))
    
    def rho(theta_deg):
        theta_rad = math.radians(theta_deg)
        return A * abs(math.cos(k * theta_rad)) * (1 - theta_deg / (revolutions * 360))  # decay factor

    for i in range(len(theta_vals) - 1):
        theta1 = theta_vals[i]
        theta2 = theta_vals[i + 1]
        segment = {
            "type": "line",
            "start": {"rho": round(rho(theta1), 3), "theta": theta1},
            "end": {"rho": round(rho(theta2), 3), "theta": theta2}
        }
        toolpath.append(segment)

    return toolpath

# Generate and save
toolpath = generate_flower_toolpath()
with open("spiral_flower_toolpath.json", "w") as f:
    json.dump(toolpath, f, indent=4)