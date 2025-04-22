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
app.secret_key = "edenlab"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class stopCheck:
    value = True

IO_pins = {
    # Analog IO Hat Pins
    "VOLTAGE_SETPOINT_PIN": 1,
    "PRESSURE_SETPOINT_PIN": 3,
    "VOLTAGE_READ_PIN": 1,
    "CURRENT_READ_PIN": 2,
    "PRESSURE_READ_PIN": 3,

    # Relay GPIOs 
    "DUMP_PIN": 13,
    "PRESSURE_PIN": 6,
    "CHARGE_PIN": 12,
    "HV_TOGGLE_S1_PIN": 26,
    "HV_TOGGLE_S2_PIN": 20,
    "TRIGGER_PIN": 5
}


ARMING_CODE_MANUAL = "eyebreakrocks"
ARMING_CODE_AUTO = "webreakrocks"

# Output pin setups
GPIO.setup(IO_pins["DUMP_PIN"], GPIO.OUT)   
GPIO.setup(IO_pins["PRESSURE_PIN"], GPIO.OUT)   
GPIO.setup(IO_pins["CHARGE_PIN"], GPIO.OUT)   
GPIO.setup(IO_pins["HV_TOGGLE_S1_PIN"], GPIO.OUT)  
GPIO.setup(IO_pins["HV_TOGGLE_S2_PIN"], GPIO.OUT) 
GPIO.setup(IO_pins["TRIGGER_PIN"], GPIO.OUT)   

# Initialize GPIO states
GPIO.output(IO_pins["DUMP_PIN"], GPIO.HIGH)
GPIO.output(IO_pins["PRESSURE_PIN"], GPIO.HIGH)
GPIO.output(IO_pins["CHARGE_PIN"], GPIO.HIGH)
GPIO.output(IO_pins["HV_TOGGLE_S1_PIN"], GPIO.LOW)
GPIO.output(IO_pins["HV_TOGGLE_S2_PIN"], GPIO.LOW)
GPIO.output(IO_pins["TRIGGER_PIN"], GPIO.LOW)


#Define default states and settings (user inputs)
settingsData = {
    'chargeTimeout': 10,    # Seconds
    'supplyVoltage': 100,   # kV
    'supplyWattage': 300,   # Watts
    'supplyCurrent': 3,     # mA
    'plotSampleRate': 8,    # Samples per second
    'plotLength': 20,       # Seconds of data shown
    'pressureMultiplier': 0.977706,
    'pressureOffset': 17.3008,
    'chargeMultiplier': 210,
    'chargeOffset': 7.5
}

templateData = {
    'altitudeCurr': 0,          #ft
    'vSetpoint': 0,             #kV
    'pulsesRequested': 0, 
    'currPressureGauge': 0,     #PSI
    'currPressureGauge_AltAdj': 0, #PSI
    'pressureOffset': 0,        #PSI
    'purgeTime': 8,             #seconds

    'armingCode': "",

    'dumpCurrState': True,
    'chargeCurrState': True,
    'pressureCurrState': True,
    'hvToggleCurrState': False,
    'safetyCurrState' : True,

    'pulsesCompleted': 0,
    'triggerCountdown': 0
}