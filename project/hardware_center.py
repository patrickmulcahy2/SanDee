import lgpio
import time

from .encoder_tracker import Encoder
from .PID_controller import Motor
from .config import reqPosition, currPosition, currVelocity, IO_pins, settingsPID, socketio, system_states
from .utils import rhoCalibrate, thetaCalibrate, linearVelocityCalc

# Create shared chip instance
chip = lgpio.chip(0)

# Motor parameters map
motor_params = {
    "rho": {
        "neg_pin": IO_pins["rho_neg"],
        "pos_pin": IO_pins["rho_pos"],
        "Kp": settingsPID["kp_Rho"],
        "Ki": settingsPID["ki_Rho"],
        "Kd": settingsPID["kd_Rho"],
    },
    "theta": {
        "neg_pin": IO_pins["theta_neg"],
        "pos_pin": IO_pins["theta_pos"],
        "Kp": settingsPID["kp_Theta"],
        "Ki": settingsPID["ki_Theta"],
        "Kd": settingsPID["kd_Theta"],
    }
}

# Getter functions
def get_rho_setpoint():
    return reqPosition["rhoReq"]

def get_rho_position():
    return currPosition["rhoCurr"]

def get_theta_setpoint():
    return reqPosition["thetaReq"]

def get_theta_position():
    return currPosition["thetaCurr"]

# Create encoder + motor objects
encoder_rho = Encoder(chip, IO_pins["encoder_rho_A"], IO_pins["encoder_rho_B"])
encoder_theta = Encoder(chip, IO_pins["encoder_theta_A"], IO_pins["encoder_theta_B"])

rho_motor_PID = Motor(chip, "rho", get_rho_setpoint, get_rho_position, encoder_rho, motor_params)
theta_motor_PID = Motor(chip, "theta", get_theta_setpoint, get_theta_position, encoder_theta, motor_params)

def read_encoders(dT):
    try:
        while True:
            encoder_rho.poll()
            encoder_theta.poll()

            rho_position_encoder = encoder_rho.get_position()
            theta_position_encoder = encoder_theta.get_position()

            rho_velocity_encoder = encoder_rho.get_angular_velocity()
            theta_velocity_encoder = encoder_theta.get_angular_velocity()

            currPosition['rhoCurr'] = rhoCalibrate(rho_position_encoder)
            currPosition['thetaCurr'] = thetaCalibrate(theta_position_encoder)

            currVelocity['rhoVelocity'] = rhoCalibrate(rho_velocity_encoder)
            currVelocity['thetaVelocity'] = thetaCalibrate(theta_velocity_encoder)
            currVelocity['linearVelocity'] = linearVelocityCalc(currVelocity['rhoVelocity'], currVelocity['thetaVelocity'])

            socketio.sleep(dT)

    except KeyboardInterrupt:
        print("Program stopped by user.")
    finally:
        encoder_rho.cleanup()
        encoder_theta.cleanup()
        chip.close()

def home_motors():
    rho_motor_PID.home_motor()
    # theta_motor_PID.home_motor()  # Optional

def control_motors(dT):
    home_motors()

    try:
        while True:
            while system_states.PID_active:
                rho_motor_PID.maintain_position()
                theta_motor_PID.maintain_position()
                socketio.sleep(dT)
    except ValueError:
        print("Error, no longer controlling motors")
    finally:
        rho_motor_PID.cleanup()
        theta_motor_PID.cleanup()
        chip.close()
