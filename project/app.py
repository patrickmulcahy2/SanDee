from flask import Flask, render_template, request, Response, send_from_directory, session, redirect, url_for
import threading 
from threading import Lock

from .console_logging import init_log_handlers
from .settings import init_settings_handlers, retrieve_settings_save
from .utilities import init_utility_handlers
from .client_comms import init_comms_handlers
from .background_tasks import updateData, safetyCheck, pressureVoltageSet, pressureVoltageCurrentRead
from .manual_control import init_manualControl_handlers
from .config import templateData, app, socketio
from .control_commands import init_controlCommands_handlers, stop


thread = None
thread_lock = Lock()

init_log_handlers()
init_settings_handlers()
init_utility_handlers()
init_comms_handlers()
init_controlCommands_handlers()
init_manualControl_handlers()

##############################################
############# CLIENT HANDLERS ################
##############################################
connected_clients = set()

@socketio.on("connect")
def connect():
    global thread
    sid = request.sid
    connected_clients.add(sid)
    retrieve_settings_save()

    print("Client connected")
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(updateData)
            socketio.start_background_task(safetyCheck)
            socketio.start_background_task(pressureVoltageSet)
            socketio.start_background_task(pressureVoltageCurrentRead)

@socketio.on("disconnect")
def disconnect():
    sid = request.sid
    connected_clients.discard(sid)
    print(f"Client disconnected: {sid}")
    if not connected_clients:
        print("All clients disconnected. Stopping system.")
        stop()



#####################################
########## CONTROL ROUTES ###########
#####################################
@app.route('/')
def automatedControl():
    templateData["armingCode"] = ""
    return render_template('automatedControl.html')

@app.route('/manual')
def manualControl():
    templateData["armingCode"] = ""
    return render_template('manualControl.html')