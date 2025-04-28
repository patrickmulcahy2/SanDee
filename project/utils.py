import math


from .config import app, socketio, gearRatios, currPosition


def init_utils_handlers():
	@socketio.on('utility')
	def utility(data):
		pass



rhoConversionFactor = 1  #Convert encoder increments to inches from center
thetaConversionFactor = 1  #Convert encoder increments to degrees from 0°


def rhoCalibrate(rho_encoder):
	rho_rotations = rho_encoder / gearRatios["encoderTicksPerRev"]
	rho_linear = rho_rotations / gearRatios["rhoToDrive"]  ####MAY BY MULTIPLY INSTEAD OF DIVIDE
	return rho_linear

def thetaCalibrate(theta_encoder):
	theta_drive_rotations = theta_encoder / gearRatios["encoderTicksPerRev"]
	theta_rotations = theta_drive_rotations / gearRatios["thetaToDrive"]
	return theta_rotations

def linearVelocityCalc(rho_velocity_encoder, theta_velocity_encoder):
	rhoPrimeCalibrated = rhoCalibrate(rho_velocity_encoder)
	thetaPrimeCalibrated = thetaCalibrate(theta_velocity_encoder)
	thetaPrimeCalibrated_rads = thetaPrimeCalibrated * math.pi / 180

	currRho = currPosition["rhoCurr"]

	tangentialVelocity = ((currRho * thetaPrimeCalibrated_rads) ** 2)
	linearVelocity = math.sqrt((rhoPrimeCalibrated ** 2) + tangentialVelocity)
	
	return linearVelocity