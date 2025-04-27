import RPi.GPIO as GPIO
from datetime import timedelta
import os

from flask import Flask, render_template, request, Response, send_from_directory, session, redirect, url_for, Blueprint
from flask_socketio import SocketIO

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

socketio = SocketIO(app, cors_allowed_origins='*')
app.secret_key = "SanDee"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class stopCheck:
    value = True

IO_pins = {
    # Relay GPIOs 
    "DUMP_PIN": 13,
}


ARMING_CODE_MANUAL = "eyebreakrocks"

# Output pin setups
GPIO.setup(IO_pins["DUMP_PIN"], GPIO.OUT)   


# Initialize GPIO states
GPIO.output(IO_pins["DUMP_PIN"], GPIO.HIGH)


#Define default states and settings (user inputs)
settingsData = {
    'chargeTimeout': 10,    # Seconds
}

templateData = {
    'altitudeCurr': 0,          #ft
}