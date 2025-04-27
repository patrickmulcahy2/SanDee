import threading
from threading import Lock
import RPi.GPIO as GPIO
import time


from .config import settingsData, socketio
from .client_comms import update_client
from .encoder_tracker import read_encoders

data_thread_lock = Lock()


def updateData():
    """Continuously sends templateData to the client."""
    while True:
        with data_thread_lock:
            update_client()
        socketio.sleep(0.05)  # Send data every second (adjust as needed)



def encoderTracking():
    while True:
        read_encoders()


def controlLoop(): 
    while True:
        pass
        