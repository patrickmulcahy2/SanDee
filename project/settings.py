import os
import configparser
import subprocess

from flask import render_template, request, redirect, url_for, session, jsonify

from .config import settingsData, settingsPID, app, socketio

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

        settingsData['chargeTimeout'] = int(data.get("feedrate"), 5)

        settingsPID['kp_Rho'] = float(data.get("kp_Rho", 1.00 ))
        settingsPID['ki_Rho'] = float(data.get("ki_Rho", 0.10))
        settingsPID['kd_Rho'] = float(data.get("kd_Rho", 0.01))
        settingsPID['kp_Theta'] = float(data.get("kp_Theta", 1.00))
        settingsPID['ki_Theta'] = float(data.get("ki_Theta", 0.10))
        settingsPID['kd_Theta'] = float(data.get("kd_Theta", 0.01))

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
        settingsData['feedrate'] = int(s.get("feedrate"), 5)


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
    s["feedrate"] = str(settingsData['feedrate'])

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
########## SETTINGS BLUE PRINT ROUTES ##########
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

