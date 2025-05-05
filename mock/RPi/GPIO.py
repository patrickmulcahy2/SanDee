class PWM:
    def __init__(self, pin, frequency): 
        self.pin = pin
        self.frequency = frequency
    def start(self, duty_cycle): pass
    def ChangeDutyCycle(self, duty_cycle): pass
    def ChangeFrequency(self, frequency): pass
    def stop(self): pass

def setmode(mode): pass
def setup(pin, mode, **kwargs): pass
def output(pin, state): pass
def setwarnings(bool): pass
def input(pin): pass
def add_event_detect(pin, edge, callback=None, bouncetime=None): pass
def remove_event_detect(pin, callback=None, bouncetime=None): pass
def cleanup(): pass

# Constants
BCM = 'BCM'
BOARD = 'BOARD'
OUT = 'OUT'
IN = 'IN'
HIGH = 1
LOW = 0
RISING = 'RISING'
FALLING = 'FALLING'
BOTH = 'BOTH'
PUD_UP = 'PUD_UP'
PUD_DOWN = 'PUD_DOWN'
