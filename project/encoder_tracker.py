import RPi.GPIO as GPIO
import time

from flask_socketio import SocketIO


from .config import IO_pins, currPosition


class Encoder:
    def __init__(self, pin_a, pin_b):
        # Initialize GPIO settings
        self.pin_a = pin_a
        self.pin_b = pin_b

        # Encoder state tracking
        self.position = 0
        self.last_a = GPIO.input(self.pin_a)
        self.last_b = GPIO.input(self.pin_b)

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

    def get_position(self):
        return self.position

    def reset_position(self):
        self.position = 0

    def cleanup(self):
        # Clean up GPIO settings
        GPIO.remove_event_detect(self.pin_a)
        GPIO.remove_event_detect(self.pin_b)
        GPIO.cleanup()

def read_encoders():
    global currPosition
    # Create Encoder objects for rho and theta
    encoder_rho = Encoder(IO_pins["encoder_rho_A"], IO_pins["encoder_rho_B"])
    encoder_theta = Encoder(IO_pins["encoder_theta_A"], IO_pins["encoder_theta_B"])

    try:
        while True:
            # Get the current positions of rho and theta
            rho_position = encoder_rho.get_position()
            theta_position = encoder_theta.get_position()

            rhoConversionFactor = 1  #Convert encoder increments to inches from center
            thetaConversionFactor = 1  #Convert encoder increments to degrees from 0°


            # Update the current position values (convert counts to desired units)
            currPosition['rhoCurr'] = rho_position * rhoConversionFactor
            currPosition['thetaCurr'] = theta_position * thetaConversionFactor

            # Print current position values (optional)
            print(f"Rho Position: {currPosition['rhoCurr']} inches, Theta Position: {currPosition['thetaCurr']} degrees")

            # Sleep for a short period before reading again
            socketio.sleep(0.01)  # Adjust based on your update frequency requirements
    
    except KeyboardInterrupt:
        print("Program stopped by user.")
    
    finally:
        # Clean up GPIO on exit
        encoder_rho.cleanup()
        encoder_theta.cleanup()
