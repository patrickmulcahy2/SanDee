import RPi.GPIO as GPIO
import math
import time

from .config import IO_pins, currPosition, reqPosition, settingsPID, socketio
from .config import rhoPos, rhoNeg, thetaNeg, thetaPos

class Motor:
	def __init__(self, motor_type, setpoint_getter, position_getter):
		self.get_setpoint = setpoint_getter
		self.get_position = position_getter

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

		self.sendMotorControl(output)

	def sendMotorControl(self, output):
		if output < 0:
			self.neg_pin.ChangeDutyCycle(abs(output))
			self.pos_pin.ChangeDutyCycle(0)
		else:
			self.pos_pin.ChangeDutyCycle(abs(output))
			self.neg_pin.ChangeDutyCycle(0)



	def cleanup(self):
        # Clean up GPIO settings
		self.neg_pin.stop()
		self.pos_pin.stop()
		GPIO.cleanup()

# Getter functions
def get_rho_setpoint():
    return reqPosition["rhoReq"]

def get_rho_position():
    return currPosition["rhoCurr"]

def get_theta_setpoint():
    return reqPosition["thetaReq"]

def get_theta_position():
    return currPosition["thetaCurr"]

def control_motors(dT):
	rho_motor_PID = Motor("rho", get_rho_setpoint, get_rho_position)
	theta_motor_PID = Motor("theta", get_theta_setpoint, get_theta_position)
	try:
		while True: 
			rho_motor_PID.maintain_position()
			theta_motor_PID.maintain_position()

			socketio.sleep(dT)
	except ValueError:
    	print("Error, no longer controlling motors")

    finally:
        # Clean up GPIO on exit
        rho_motor.cleanup()
        theta_motor.cleanup()
        GPIO.cleanup()
    