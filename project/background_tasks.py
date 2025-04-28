import threading
from threading import Lock
import RPi.GPIO as GPIO
import time


from .config import settingsData, socketio, currPosition, IO_pins
from .client_comms import update_client
from .encoder_tracker import read_encoders
from .PID_controller import control_motors

data_thread_lock = Lock()

dT = 0.01 #Seconds between polls

def updateData():
    """Continuously sends templateData to the client."""
    while True:
        with data_thread_lock:
            update_client()
        socketio.sleep(50*dT)

def encoderTracking():
    while True:
        read_encoders(dT)


def controlLoop(): 
    while True:
        control_motors(dT)
