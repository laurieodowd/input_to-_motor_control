"""
library for motor control. 
"""
import pigpio
from time import sleep

class Motor:
    def __init__(self, *args):
        self.pins = args

    def cleanup(self):
        pass
    

class ServoMotor(Motor):
    def __init__(self, control_pin):
        super().__init__(control_pin)
        self.pi = pigpio.pi()
        self.control_pin = control_pin

    def set_pulsewidth(self, pulsewidth):
        self.pi.set_servo_pulsewidth(self.control_pin, pulsewidth)
    
    def move_between_angles(self, angle1, angle2, step, get_sleep_time_func):
        pulse_width1 = angle1
        pulse_width2 = angle2

        pulse_width = min(pulse_width1, pulse_width2)
        upper_limit = max(pulse_width1, pulse_width2)

        step *= 1 if pulse_width1 < pulse_width2 else -1

        while True:
            self.set_pulsewidth(pulse_width)
            sleep_time = get_sleep_time_func()  # Get the sleep time from the provided function
            sleep(sleep_time)
            pulse_width += step
            if (step > 0 and pulse_width >= upper_limit) or (step < 0 and pulse_width <= min(pulse_width1, pulse_width2)):
                step = -step
    def cleanup(self):
        self.pi.set_servo_pulsewidth(self.control_pin, 0)
        self.pi.stop()

class DCMotor(Motor):
    def __init__(self, in1, in2, enable):
        super().__init__(in1, in2, enable)
        self.pi = pigpio.pi()
        self.setup_pins(in1, in2, enable)

    def setup_pins(self, in1, in2, enable):
        self.pi.set_mode(in1, pigpio.OUTPUT)
        self.pi.set_mode(in2, pigpio.OUTPUT)
        self.pi.set_mode(enable, pigpio.OUTPUT)

        self.pwm = enable

    def set_speed(self, speed):
        duty_cycle = int(speed * 255 / 100)
        self.pi.set_PWM_dutycycle(self.pwm, duty_cycle)

    def forward(self):
        self.pi.write(self.pins[0], 1)
        self.pi.write(self.pins[1], 0)

    def backward(self):
        self.pi.write(self.pins[0], 0)
        self.pi.write(self.pins[1], 1)

    def stop(self):
        self.pi.write(self.pins[0], 0)
        self.pi.write(self.pins[1], 0)

    def cleanup(self):
        self.pi.write(self.pins[0], 0)
        self.pi.write(self.pins[1], 0)
        self.pi.write(self.pwm, 0)
        self.pi.stop()