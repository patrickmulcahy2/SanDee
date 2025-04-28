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
    "rho_pos": 12,
    "rho_neg": 32,
    "theta_neg": 33,
    "theta_pos": 35,
    "encoder_rho_A": 26,
    "encoder_rho_B": 36,
    "encoder_theta_A": 38,
    "encoder_theta_B": 40,
}


# Output pin setups
GPIO.setup(IO_pins["rho_pos"], GPIO.OUT)   
GPIO.setup(IO_pins["rho_neg"], GPIO.OUT)   
GPIO.setup(IO_pins["theta_neg"], GPIO.OUT)   
GPIO.setup(IO_pins["theta_pos"], GPIO.OUT)   
GPIO.setup(IO_pins["encoder_rho_A"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(IO_pins["encoder_rho_B"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(IO_pins["encoder_theta_A"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(IO_pins["encoder_theta_B"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize GPIO states
PWM_freq = 1000 # 1000 Hz frequency
rhoPos = GPIO.PWM(IO_pins["rho_pos"], PWM_freq)  
rhoNeg = GPIO.PWM(IO_pins["rho_neg"], PWM_freq)  
thetaNeg = GPIO.PWM(IO_pins["theta_neg"], PWM_freq)  
thetaPos = GPIO.PWM(IO_pins["theta_pos"], PWM_freq)  
rhoPos.start(0)
rhoNeg.start(0)
thetaNeg.start(0)
thetaPos.start(0)

gearRatios = {
    'thetaToDrive': (320/40),
    'rhoToDrive': 1.572,
    'encoderTicksPerRev': 12,
}

#Define default states and settings (user inputs)
settingsPID = {
    'kp_Rho': 1.00,
    'ki_Rho': 0.10,
    'kd_Rho': 0.01,
    'kp_Theta': 1.00,
    'ki_Theta': 0.10,
    'kd_Theta': 0.01, 
}

settingsData = {
    'feedrate': 5,          #inch per second
}



userInputs = {
    'feedrateOffset': 0,    #inch per second
}

currPosition = {
    'rhoCurr': 0,           #inches
    'thetaCurr': 0,         #degrees

}

currVelocity = {
    'rhoVelocity': 0,       #in/s
    'thetaVelocity': 0,     #deg/s
    'linearSpeed': 0        #in/s
}
reqPosition = {
    'rhoReq': 0,          #inches
    'thetaReq': 0         #degrees
}