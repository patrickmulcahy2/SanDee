import threading
from threading import Lock

try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    from mock.RPi import GPIO

import time


from .config import settingsData, socketio, currPosition, IO_pins, system_states
from .client_comms import update_client
from .hardware_center import read_encoders, control_motors
from .led_control import control_LED

data_thread_lock = Lock()

def updateData():
    """Continuously sends templateData to the client."""
    while True:
        with data_thread_lock:
            update_client()
        socketio.sleep(2*system_states.dT)

def encoderTracking():
    while True:
        read_encoders(system_states.dT)


def controlLoop(): 
    while True:
        control_motors(system_states.dT)

def controlLED():
    while True:
        control_LED(100*system_states.dT)