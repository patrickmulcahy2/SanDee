from flask import Flask, render_template, request, Response, send_from_directory, session, redirect, url_for
import threading 
from threading import Lock

from .config import app, socketio
from .settings import init_settings_handlers, retrieve_settings_save
from .utils import init_utils_handlers
from .client_comms import init_comms_handlers
from .background_tasks import updateData, encoderTracking, controlLoop, controlLED
from .control_commands import init_controlCommands_handlers
from .manual_control import init_manualControl_handlers
from .PID_tuner import init_tuner_handlers
from .toolpath_manager import init_toolpath_handlers
from .toolpath_creator import init_toolpathCreator_handlers

thread = None
thread_lock = Lock()

init_settings_handlers()
init_utils_handlers()
init_comms_handlers()
init_controlCommands_handlers()
init_manualControl_handlers()
init_tuner_handlers()
init_toolpath_handlers()
init_toolpathCreator_handlers()


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
            socketio.start_background_task(encoderTracking)
            socketio.start_background_task(controlLoop)
            socketio.start_background_task(controlLED)

@socketio.on("disconnect")
def disconnect():
    sid = request.sid
    connected_clients.discard(sid)
    print(f"Client disconnected: {sid}")


#####################################
########## CONTROL ROUTES ###########
#####################################
@app.route('/')
def automatedControl():
    return render_template('automatedControl.html')

@app.route('/manual')
def manualControl():
    return render_template('manualControl.html')