import os
import configparser
import subprocess

from flask import render_template, request, redirect, url_for, session, jsonify

from .config import settingsData, app, socketio
#from .utilities import sparkGapPressureCalc


# Create a config parser instance
configParser = configparser.ConfigParser()

# Path to the settings file
settings_file_path = os.path.join(os.path.dirname(__file__), "settings.cfg")

################################################
########## SETTINGS SOCKET HANDLERS ############
################################################
def init_settings_handlers():
    @socketio.on('settings_sent')
    def new_settings(data):
        global settingsData

        settingsData['chargeTimeout'] = int(data.get("chargeTimeout", 0))
        settingsData['supplyVoltage'] = int(data.get("supplyVoltage", 0))
        settingsData['supplyWattage'] = int(data.get("supplyWattage", 0))
        settingsData['supplyCurrent'] = (settingsData['supplyWattage'] / settingsData['supplyVoltage'])
        settingsData['plotSampleRate'] = int(data.get("plotSampleRate", 0))
        settingsData['plotLength'] = int(data.get("plotLength", 0))
        settingsData['pressureMultiplier'] = float(data.get("pressureMultiplier", 0))
        settingsData['pressureOffset'] = float(data.get("pressureOffset", 0))


        templateData['currPressureGauge'] = sparkGapPressureCalc(templateData['vSetpoint'] + templateData["pressureOffset"])
        update_client()
        update_settings_save()

    @socketio.on("reboot") 
    def reboot():
        os.system("sudo reboot")

# Access settings file and update the settings
def retrieve_settings_save():
    global settingsData

    if not os.path.exists(settings_file_path):
        print("Settings file not found. Using default values.")
        return

    configParser.read(settings_file_path)

    if 'Settings' in configParser:
        s = configParser['Settings']
        settingsData['chargeTimeout'] = int(s.get("chargeTimeout", 10))
        settingsData['supplyVoltage'] = int(s.get("supplyVoltage", 100))
        settingsData['supplyWattage'] = int(s.get("supplyWattage", 600))
        settingsData['plotSampleRate'] = int(s.get("plotSampleRate", 8))
        settingsData['plotLength'] = int(s.get("plotLength", 20))
        settingsData['supplyCurrent'] = settingsData['supplyWattage'] / settingsData['supplyVoltage']
        settingsData['pressureMultiplier'] = float(s.get("pressureMultiplier", 0.977706))
        settingsData['pressureOffset'] = float(s.get("pressureOffset", 17.3008))
    else:
        print("Settings section not found in file.")

def update_settings_save():
    if 'Settings' not in configParser:
        configParser['Settings'] = {}

    s = configParser['Settings']
    s["chargeTimeout"] = str(settingsData['chargeTimeout'])
    s["supplyVoltage"] = str(settingsData['supplyVoltage'])
    s["supplyWattage"] = str(settingsData['supplyWattage'])
    s["plotSampleRate"] = str(settingsData['plotSampleRate'])
    s["plotLength"] = str(settingsData['plotLength'])
    s["pressureMultiplier"] = str(settingsData['pressureMultiplier'])
    s["pressureOffset"] = str(settingsData['pressureOffset'])


    with open(settings_file_path, 'w') as configfile:
        configParser.write(configfile)
    print("Settings saved to file.")

################################################
########## SETTINGS BLUE PRINT ROUTES ##########
################################################
@app.route("/settings")
def settings():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("settings.html", settingsData=settingsData)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == app.secret_key:  # Replace with secure hash check in production
            session.permanent = True
            session["authenticated"] = True
            return redirect(url_for("settings"))
        else:
            return render_template("login.html", error="Incorrect password")
    return render_template("login.html")

