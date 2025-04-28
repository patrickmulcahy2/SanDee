import RPi.GPIO as GPIO
import time

from .config import IO_pins, currPosition, currVelocity, socketio
from .utils import rhoCalibrate, thetaCalibrate, linearVelocityCalc

class Encoder:
    def __init__(self, pin_a, pin_b):
        # Initialize GPIO settings
        self.pin_a = pin_a
        self.pin_b = pin_b

        # Encoder state tracking
        self.position = 0
        self.last_a = GPIO.input(self.pin_a)
        self.last_b = GPIO.input(self.pin_b)

        self.last_time = time.time()
        self.angular_velocity = 0

        # Interrupts for encoder signal changes
        GPIO.add_event_detect(self.pin_a, GPIO.BOTH, callback=self.update_position)
        GPIO.add_event_detect(self.pin_b, GPIO.BOTH, callback=self.update_position)

    def update_position(self, channel):
        # Read current states of the encoder signals
        a_state = GPIO.input(self.pin_a)
        b_state = GPIO.input(self.pin_b)

        # Determine direction based on A and B signal states
        if a_state != self.last_a:
            if b_state != a_state:
                self.position += 1  # Clockwise
            else:
                self.position -= 1  # Counter-clockwise

        # Update previous states
        self.last_a = a_state
        self.last_b = b_state

        # Calculate angular velocity
        current_time = time.time()
        dT = current_time - self.last_time  # Time difference
        if dT > 0:
            self.angular_velocity = (self.position - self.last_position) / dT  # Position change over time
        self.last_time = current_time
        self.last_position = self.position

    def get_position(self):
        return self.position

    def get_angular_velocity(self):
        return self.angular_velocity

    def reset_position(self):
        self.position = 0
        self.angular_velocity = 0  # Reset velocity when position is reset

    def cleanup(self):
        # Clean up GPIO settings
        GPIO.remove_event_detect(self.pin_a)
        GPIO.remove_event_detect(self.pin_b)
        GPIO.cleanup()

def read_encoders(dT):
    global currPosition
    # Create Encoder objects for rho and theta
    encoder_rho = Encoder(IO_pins["encoder_rho_A"], IO_pins["encoder_rho_B"])
    encoder_theta = Encoder(IO_pins["encoder_theta_A"], IO_pins["encoder_theta_B"])

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
            currVelocity['linearVelocity'] = linearVelocityCalc(rho_velocity_encoder, theta_velocity_encoder)

            socketio.sleep(dT)

    
    except KeyboardInterrupt:
        print("Program stopped by user.")
    
    finally:
        # Clean up GPIO on exit
        encoder_rho.cleanup()
        encoder_theta.cleanup()
