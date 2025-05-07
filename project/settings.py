import os
import configparser
import subprocess

from flask import render_template, request, redirect, url_for, session, jsonify

from .config import settingsData, settingsPID, app, socketio
from .hardware_center import home_motors

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
        settingsData['feedrateMax'] = float(data.get("feedrateMax", 5))
        settingsData['feedrateMax_rho'] = float(data.get("feedrateMax_rho", 5))
        settingsData['feedrateMax_theta'] = float(data.get("feedrateMax_theta", 5))

        settingsData['feedrateDefault'] = float(data.get("feedrateDefault", 5))
        settingsData['rhoMax'] = float(data.get("rhoMax", 8))
        settingsData['maxStepover'] = float(data.get("maxStepover", 8))
        settingsData['ballSize'] = float(data.get("ballSize", 8))
        settingsData['clearingStepover'] = float(data.get("clearingStepover", 8))
        settingsData['clearingType'] = (data.get("clearingType", "spiral"))

        settingsPID['kp_Rho'] = float(data.get("kp_Rho", 1.00 ))
        settingsPID['ki_Rho'] = float(data.get("ki_Rho", 0.10))
        settingsPID['kd_Rho'] = float(data.get("kd_Rho", 0.01))
        settingsPID['kp_Theta'] = float(data.get("kp_Theta", 1.00))
        settingsPID['ki_Theta'] = float(data.get("ki_Theta", 0.10))
        settingsPID['kd_Theta'] = float(data.get("kd_Theta", 0.01))

        update_settings_save()

    @socketio.on("reboot") 
    def reboot():
        os.system("sudo reboot")

    @socketio.on("homeMotors") 
    def homeCalled():
        home_motors()

# Access settings file and update the settings
def retrieve_settings_save():
    if not os.path.exists(settings_file_path):
        print("Settings file not found. Using default values.")
        return

    configParser.read(settings_file_path)

    if 'Settings' in configParser:
        s = configParser['Settings']
        settingsData['feedrateMax'] = float(s.get("feedrateMax", 5))
        settingsData['feedrateMax_rho'] = float(s.get("feedrateMax_rho", 5))
        settingsData['feedrateMax_theta'] = float(s.get("feedrateMax_theta", 20))

        settingsData['feedrateDefault'] = float(s.get("feedrateDefault", 5))
        settingsData['rhoMax'] = float(s.get("rhoMax", 8))
        settingsData['maxStepover'] = float(s.get("maxStepover", 8))
        settingsData['ballSize'] = float(s.get("ballSize", 8))
        settingsData['clearingStepover'] = float(s.get("clearingStepover", 8))
        settingsData['clearingType'] = (s.get("clearingType", "spiral"))


        settingsPID['kp_Rho'] = float(s.get("kp_Rho", 1.00 ))
        settingsPID['ki_Rho'] = float(s.get("ki_Rho", 0.10))
        settingsPID['kd_Rho'] = float(s.get("kd_Rho", 0.01))
        settingsPID['kp_Theta'] = float(s.get("kp_Theta", 1.00))
        settingsPID['ki_Theta'] = float(s.get("ki_Theta", 0.10))
        settingsPID['kd_Theta'] = float(s.get("kd_Theta", 0.01))

    else:
        print("Settings section not found in file.")

def update_settings_save():
    if 'Settings' not in configParser:
        configParser['Settings'] = {}

    s = configParser['Settings']
    s["feedrateMax"] = str(settingsData['feedrateMax'])
    s["feedrateMax_rho"] = str(settingsData['feedrateMax_rho'])
    s["feedrateMax_theta"] = str(settingsData['feedrateMax_theta'])

    s["feedrateDefault"] = str(settingsData['feedrateDefault'])
    s["rhoMax"] = str(settingsData['rhoMax'])
    s["maxStepover"] = str(settingsData['maxStepover'])
    s["ballSize"] = str(settingsData['ballSize'])
    s["clearingStepover"] = str(settingsData['clearingStepover'])
    s["clearingType"] = str(settingsData['clearingType'])


    s["kp_Rho"] = str(settingsPID['kp_Rho'])
    s["ki_Rho"] = str(settingsPID['ki_Rho'])
    s["kd_Rho"] = str(settingsPID['kd_Rho'])
    s["kp_Theta"] = str(settingsPID['kp_Theta'])
    s["ki_Theta"] = str(settingsPID['ki_Theta'])
    s["kd_Theta"] = str(settingsPID['kd_Theta'])

    with open(settings_file_path, 'w') as configfile:
        configParser.write(configfile)
    print("Settings saved to file.")

################################################
############### SETTINGS  ROUTES ###############
################################################
@app.route("/settings")
def settings():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("settings.html", settingsData=settingsData, settingsPID=settingsPID)

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

