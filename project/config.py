import os
from datetime import timedelta
import lgpio
from flask import Flask
from flask_socketio import SocketIO

# ==== Flask / SocketIO setup ====

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
socketio = SocketIO(app, cors_allowed_origins='*')
app.secret_key = "pfm"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)

# ==== System states ====

class SystemStates:
    def __init__(self):
        self.pauseStatus = False
        self.clearingStatus = False
        self.patterningStatus = False
        self.dT = 0.005
        self.PID_active = True
        self.statusPercent = 0

system_states = SystemStates()

class LedColors:
    def __init__(self):
        self.r = 0
        self.g = 0
        self.b = 0

LED_color = LedColors()

# ==== GPIO pin definitions ====

IO_pins = {
    "rho_pos": 18,
    "rho_neg": 12,
    "theta_neg": 13,
    "theta_pos": 19,
    "encoder_rho_A": 23,
    "encoder_rho_B": 16,
    "encoder_theta_A": 20,
    "encoder_theta_B": 21,
    "LED_pin": 24,
}

# ==== lgpio chip setup ====

PWM_freq = 1000  # Hz PWM frequency
chip = lgpio.chip(0)

# ==== Motion parameters ====

gearRatios = {
    'thetaToDrive': (320/40),
    'rhoToDrive': 1.572,        # revs per inch or inch per rev (as in original)
    'encoderTicksPerRev': 12,
}

settingsPID = {
    'kp_Rho': 1.00,
    'ki_Rho': 0.10,
    'kd_Rho': 0.01,
    'kp_Theta': 1.00,
    'ki_Theta': 0.10,
    'kd_Theta': 0.01, 
}

settingsData = {
    'feedrateMax': 10,           
    'feedrateMax_rho': 5,       
    'feedrateMax_theta': 20,    

    'feedrateDefault': 5,       
    'rhoMax': 8,                
    'maxStepover': 0.125,       
    'clearingStepover': 0.125,  
    'clearingType': "Spiral",   
    'ballSize': 1,              
}

userInputs = {
    'feedrateOffset': 0,         
    'feedrate': 5,              
    'selected_TP_filepath': None
}

currPosition = {
    'rhoCurr': 0,         
    'thetaCurr': 0,       
}

currVelocity = {
    'rhoVelocity': 0,     
    'thetaVelocity': 0,   
    'linearSpeed': 0      
}

reqPosition = {
    'rhoReq': 0,          
    'thetaReq': 0         
}

