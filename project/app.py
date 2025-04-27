from flask import Flask, render_template, request, Response, send_from_directory, session, redirect, url_for
import threading 
from threading import Lock

from .settings import init_settings_handlers, retrieve_settings_save
from .utilities import init_utility_handlers
from .background_tasks import updateData, encoderTracking, controlLoop
from .config import app, socketio
from .control_commands import init_controlCommands_handlers


thread = None
thread_lock = Lock()

init_settings_handlers()
init_utils_handlers()
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
            socketio.start_background_task(encoderTracking)
            socketio.start_background_task(controlLoop)

@socketio.on("disconnect")
def disconnect():
    sid = request.sid
    connected_clients.discard(sid)
    print(f"Client disconnected: {sid}")


#####################################
########## CONTROL ROUTES ###########
#####################################
@app.route('/auto')
def automatedControl():
    return render_template('automatedControl.html')

@app.route('/')
def manualControl():
    return render_template('manualControl.html')