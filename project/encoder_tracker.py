import lgpio
import time

class Encoder:
    def __init__(self, chip, pin_a, pin_b):
        self.chip = chip
        self.pin_a = pin_a
        self.pin_b = pin_b

        # Request input lines
        self.chip.claim_input(self.pin_a)
        self.chip.claim_input(self.pin_b)

        # Encoder state tracking
        self.position = 0
        self.last_position = 0
        self.last_a = self.chip.read(self.pin_a)
        self.last_b = self.chip.read(self.pin_b)
        self.last_time = time.time()
        self.angular_velocity = 0

        # Set up watchers
        self.watcher = lgpio.watcher()
        self.watcher.add(self.chip, self.pin_a, lgpio.BOTH_EDGES)
        self.watcher.add(self.chip, self.pin_b, lgpio.BOTH_EDGES)

    def poll(self):
        # Call this in your loop to check for events
        for event in self.watcher:
            if event[1] == self.pin_a or event[1] == self.pin_b:
                self.update_position()

    def update_position(self):
        a_state = self.chip.read(self.pin_a)
        b_state = self.chip.read(self.pin_b)

        if a_state != self.last_a:
            if b_state != a_state:
                self.position += 1  # Clockwise
            else:
                self.position -= 1  # Counter-clockwise

        self.last_a = a_state
        self.last_b = b_state

        current_time = time.time()
        dT = current_time - self.last_time
        if dT > 0:
            self.angular_velocity = (self.position - self.last_position) / dT
        self.last_time = current_time
        self.last_position = self.position

    def get_position(self):
        return self.position

    def get_angular_velocity(self):
        return self.angular_velocity

    def reset_position(self):
        self.position = 0
        self.angular_velocity = 0

    def cleanup(self):
        self.watcher.close()
