import time

class Motor:
    def __init__(self, chip, motor_type, setpoint_getter, position_getter, encoder, motor_params):
        self.chip = chip
        self.get_setpoint = setpoint_getter
        self.get_position = position_getter
        self.encoder = encoder

        self.neg_pin = motor_params[motor_type]["neg_pin"]
        self.pos_pin = motor_params[motor_type]["pos_pin"]
        self.Kp = motor_params[motor_type]["Kp"]
        self.Ki = motor_params[motor_type]["Ki"]
        self.Kd = motor_params[motor_type]["Kd"]

        self.previous_error = 0
        self.integral_error = 0
        self.last_time = time.time()

        # Initialize PWM on both pins
        self.chip.tx_pwm(self.neg_pin, 1000, 0)  # 1 kHz, 0% duty cycle
        self.chip.tx_pwm(self.pos_pin, 1000, 0)

    def maintain_position(self):
        now_time = time.time()
        dT = now_time - self.last_time
        self.last_time = now_time

        setpoint = self.get_setpoint()
        position_curr = self.get_position()

        error = setpoint - position_curr
        self.integral_error += error * dT
        derivative_error = (error - self.previous_error) / dT if dT > 0 else 0

        output = (self.Kp * error) + (self.Ki * self.integral_error) + (self.Kd * derivative_error)
        self.previous_error = error

        output = max(min(output, 100), -100)  # Clamp to [-100, 100]

        deadband = 5
        if 0 < output < deadband or 0 > output > -deadband:
            output = 0

        self.send_motor_control(output)

    def send_motor_control(self, output):
        if output < 0:
            self.chip.tx_pwm(self.neg_pin, 1000, abs(output))
            self.chip.tx_pwm(self.pos_pin, 1000, 0)
        else:
            self.chip.tx_pwm(self.pos_pin, 1000, abs(output))
            self.chip.tx_pwm(self.neg_pin, 1000, 0)

    def home_motor(self):
        print("Starting homing sequence for motor...")

        low_speed = 15
        timeout = 5
        sample_interval = 0.05
        min_movement = 0.1

        last_position = self.get_position()
        start_time = time.time()

        self.send_motor_control(-low_speed)

        while True:
            time.sleep(sample_interval)
            current_position = self.get_position()
            delta = abs(current_position - last_position)

            if delta < min_movement:
                break

            if time.time() - start_time > timeout:
                print("Homing timed out — no stall detected.")
                break

            last_position = current_position

        self.send_motor_control(0)

        print("Homing complete. Setting position to zero.")
        self.encoder.reset_position()

    def cleanup(self):
        self.chip.tx_pwm(self.neg_pin, 0, 0)  # Stop PWM
        self.chip.tx_pwm(self.pos_pin, 0, 0)
