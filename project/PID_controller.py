try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    from mock.RPi import GPIO
    
import math
import time

from .config import currPosition, reqPosition, settingsPID, socketio
from .config import rhoPos, rhoNeg, thetaNeg, thetaPos
from .encoder_tracker import Encoder

class Motor:
	def __init__(self, motor_type, setpoint_getter, position_getter, encoder):
		self.get_setpoint = setpoint_getter
		self.get_position = position_getter
		self.encoder = encoder

		motor_params = {
			"rho": {
				"neg_pin": rhoNeg,
				"pos_pin": rhoPos,
				"Kp": settingsPID["kp_Rho"],
				"Ki": settingsPID["ki_Rho"],
				"Kd": settingsPID["kd_Rho"],
			},
			"theta": {
				"neg_pin": thetaNeg,
				"pos_pin": thetaPos,
				"Kp": settingsPID["kp_Theta"],
				"Ki": settingsPID["ki_Theta"],
				"Kd": settingsPID["kd_Theta"],
			}
		}

        # Set the motor parameters from the dictionary
		self.neg_pin = motor_params[motor_type]["neg_pin"]
		self.pos_pin = motor_params[motor_type]["pos_pin"]
		self.Kp = motor_params[motor_type]["Kp"]
		self.Ki = motor_params[motor_type]["Ki"]
		self.Kd = motor_params[motor_type]["Kd"]

		self.previous_error = 0
		self.integral_error = 0
		self.last_time = time.time()

	def maintain_position(self):
		now_time = time.time()
		dT = now_time - self.last_time
		self.last_time = now_time

		setpoint = self.get_setpoint()
		position_curr = self.get_position()

		error = setpoint - position_curr
		self.integral_error += error * dT
		derivative_error = (error - self.previous_error) / dT

		output = (self.Kp * error) + (self.Ki * self.integral_error) + (self.Kd * derivative_error)
		self.previous_error = error

		if output > 100:
			output = 100
		elif output < -100:
			output = -100

		deadband = 5

		if 0 < output < deadband:
			output = 0
		elif 0 > output > -deadband:
			output = 0

		self.sendMotorControl(output)

	def sendMotorControl(self, output):
		if output < 0:
			self.neg_pin.ChangeDutyCycle(abs(output))
			self.pos_pin.ChangeDutyCycle(0)
		else:
			self.pos_pin.ChangeDutyCycle(abs(output))
			self.neg_pin.ChangeDutyCycle(0)


	def homeMotor(self):
		print("Starting homing sequence for motor...")

		# Parameters
		low_speed = 15  # % PWM, adjust as needed
		timeout = 5     # seconds to prevent infinite loop
		sample_interval = 0.05  # seconds
		min_movement = 0.1  # degrees or mm per second — tune based on encoder noise

		# Track encoder position
		last_position = self.get_position()
		start_time = time.time()

		# Move in negative direction slowly
		self.sendMotorControl(-low_speed)

		while True:
			time.sleep(sample_interval)
			current_position = self.get_position()
			delta = abs(current_position - last_position)

			# Stop condition: movement becomes negligible
			if delta < min_movement:
				break

			# Timeout fallback
			if time.time() - start_time > timeout:
				print("Homing timed out — no stall detected.")
				break

			last_position = current_position

		# Stop the motor
		self.sendMotorControl(0)

		# Set home position
		print("Homing complete. Setting position to zero.")
		self.encoder.reset_position()
		currPosition["rhoCurr"] = 0
		reqPosition["rhoReq"] = 0

	def cleanup(self):
        # Clean up GPIO settings
		self.neg_pin.stop()
		self.pos_pin.stop()
		GPIO.cleanup()