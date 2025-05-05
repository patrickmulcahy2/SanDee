try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    from mock.RPi import GPIO


from .encoder_tracker import Encoder
from .PID_controller import Motor
from .config import reqPosition, currPosition, IO_pins, socketio, IO_pins, currPosition, currVelocity, system_states
from .utils import rhoCalibrate, thetaCalibrate, linearVelocityCalc


# Getter functions
def get_rho_setpoint():
    return reqPosition["rhoReq"]

def get_rho_position():
    return currPosition["rhoCurr"]

def get_theta_setpoint():
    return reqPosition["thetaReq"]

def get_theta_position():
    return currPosition["thetaCurr"]


encoder_rho = Encoder(IO_pins["encoder_rho_A"], IO_pins["encoder_rho_B"])
encoder_theta = Encoder(IO_pins["encoder_theta_A"], IO_pins["encoder_theta_B"])

rho_motor_PID = Motor("rho", get_rho_setpoint, get_rho_position, encoder_rho)
theta_motor_PID = Motor("theta", get_theta_setpoint, get_theta_position, encoder_theta)

def read_encoders(dT):
    try:
        while True:
            # Get the current positions of rho and theta
            rho_position_encoder = encoder_rho.get_position()
            theta_position_encoder = encoder_theta.get_position()

            rho_velocity_encoder = encoder_rho.get_angular_velocity()  # Get rho angular velocity
            theta_velocity_encoder = encoder_theta.get_angular_velocity()  # Get theta angular velocity

            # Update the current position values (convert counts to desired units)
            currPosition['rhoCurr'] = rhoCalibrate(rho_position_encoder)
            currPosition['thetaCurr'] = thetaCalibrate(theta_position_encoder)

            currVelocity['rhoVelocity'] = rhoCalibrate(rho_velocity_encoder)
            currVelocity['thetaVelocity'] = thetaCalibrate(theta_velocity_encoder)
            currVelocity['linearVelocity'] = linearVelocityCalc(currVelocity['rhoVelocity'], currVelocity['thetaVelocity'])

            socketio.sleep(dT)

    
    except KeyboardInterrupt:
        print("Program stopped by user.")
    
    finally:
        # Clean up GPIO on exit
        encoder_rho.cleanup()
        encoder_theta.cleanup()

def home_motors():
    rho_motor_PID.homeMotor()
    ##theta_motor_PID.homeMotor() Unclear how I should home theta

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
        # Clean up GPIO on exit
        rho_motor_PID.cleanup()
        theta_motor_PID.cleanup()
        GPIO.cleanup()


    