try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    from mock.RPi import GPIO

import time

class Encoder:
    def __init__(self, pin_a, pin_b):
        # Initialize GPIO settings
        GPIO.setmode(GPIO.BCM)
        self.pin_a = pin_a
        self.pin_b = pin_b

        # Encoder state tracking
        self.position = 0
        self.last_position = 0
        
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
