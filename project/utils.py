import math
import numpy as np
from scipy.signal import find_peaks 

from .config import app, socketio, gearRatios, currPosition, settingsData


def init_utils_handlers():
	@socketio.on('utility')
	def utility(data):
		pass


def rhoCalibrate(rho_encoder):
	rho_rotations = rho_encoder / gearRatios["encoderTicksPerRev"]
	rho_linear = rho_rotations / gearRatios["rhoToDrive"]  ####MAY BY MULTIPLY INSTEAD OF DIVIDE
	return rho_linear

def thetaCalibrate(theta_encoder):
	theta_drive_rotations = theta_encoder / gearRatios["encoderTicksPerRev"]
	theta_rotations = theta_drive_rotations / gearRatios["thetaToDrive"]
	return theta_rotations

def linearVelocityCalc(rho_prime, theta_prime):
	thetaPrime_rads = theta_prime * math.pi / 180

	currRho = currPosition["rhoCurr"]

	tangentialVelocity = ((currRho * thetaPrime_rads) ** 2)
	linearVelocity = math.sqrt((rho_prime ** 2) + tangentialVelocity)
	
	return linearVelocity

def polar_to_cartesian(rho, theta):
	theta_rads = math.radians(theta)
	x = rho * math.cos(theta_rads)
	y = rho * math.sin(theta_rads)
	return x, y

def cartesian_to_polar(x, y):
	rho = math.sqrt(x**2 + y**2)  # Radius (distance from the origin)
	thetaRads = math.atan2(y, x)  # Angle in radians
	theta = math.degrees(thetaRads)
	return rho, theta


def calculateParameters(newPos, moveMagnitude_adj, posData):
    startPos = newPos - moveMagnitude_adj

    # Peak and overshoot
    peak = np.max(posData)
    overshoot = (peak - newPos) / moveMagnitude_adj * 100

    # Rise time: time to go from 10% to 90% of the move (from startPos)
    try:
        t_10_index = np.where(posData >= startPos + 0.1 * moveMagnitude_adj)[0][0]
        t_90_index = np.where(posData >= startPos + 0.9 * moveMagnitude_adj)[0][0]
        riseTime = timeArray[t_90_index] - timeArray[t_10_index]
    except IndexError:
        riseTime = 999  # Didn't reach required levels

    # Settling time: last time signal exits 5% tolerance around newPos
    settling_tolerance = 0.05 * moveMagnitude_adj
    try:
        for i in range(len(posData) - 1, -1, -1):
            if abs(posData[i] - newPos) > settling_tolerance:
                settlingTime = timeArray[i + 1] if i + 1 < len(timeArray) else 999
                break
        else:
            settlingTime = timeArray[0]
    except Exception:
        settlingTime = 999

    return riseTime, settlingTime, overshoot, peak

def findPeaks(data):
    return find_peaks(data)