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
app.secret_key = "pfm"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

IO_pins = {
    # Relay GPIOs 
    "rho_pos": 29,
    "rho_neg": 31,
    "theta_pos": 33,
    "theta_neg": 35,
}


# Output pin setups
GPIO.setup(IO_pins["rho_pos"], GPIO.OUT)   
GPIO.setup(IO_pins["rho_neg"], GPIO.OUT)   
GPIO.setup(IO_pins["theta_pos"], GPIO.OUT)   
GPIO.setup(IO_pins["theta_neg"], GPIO.OUT)   

# Initialize GPIO states
GPIO.output(IO_pins["rho_pos"], GPIO.LOW)
GPIO.output(IO_pins["rho_neg"], GPIO.LOW)
GPIO.output(IO_pins["theta_pos"], GPIO.LOW)
GPIO.output(IO_pins["theta_neg"], GPIO.LOW)


#Define default states and settings (user inputs)
settingsPID = {
    'P_Rho': 1,
    'I_Rho': 1,
    'D_Rho': 1,
    'P_Theta': 1,
    'I_Theta': 1,
    'D_Theta': 1, 
}

settingsData = {
    'feedrate': 5,          #inch per second
}

currPosition = {
    'rhoCurr': 0,          #inches
    'thetaCurr': 0         #degrees
}

reqPosition = {
    'rhoReq': 0,          #inches
    'thetaReq': 0         #degrees
}