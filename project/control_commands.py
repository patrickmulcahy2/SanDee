import os

from .config import app, socketio, system_states, userInputs, BASE_DIR
from .clearTable import clearTable
from .parseToolpath import follow_path


def init_controlCommands_handlers():
    @socketio.on('go')
    def go():
        if (system_states.pauseStatus == True):
            system_states.pauseStatus = False
            print("Command Recieved: 'Resume'")
        else:
            print("Command Recieved: 'Go'")
            system_states.patterningStatus = True

            # Construct the full file path for selected_TP
            selected_TP_path = BASE_DIR + userInputs["selected_TP"]

            # Call follow_path with the correct full path
            follow_path(selected_TP_path)

    @socketio.on('pause')
    def pause():
        if (system_states.pauseStatus == True):
            system_states.pauseStatus = False
            system_states.patterningStatus = False
            system_states.clearingStatus = False
            socketio.emit("clearPlot")
            print("Command Recieved: 'Cancel'")

        else:
            print("Command Recieved: 'Pause'")
            system_states.pauseStatus = True


    @socketio.on('clear')
    def clear():
        print("Command Recieved: 'Clear'")
        system_states.clearingStatus = True
        socketio.start_background_task(clearTable)
