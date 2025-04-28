from flask_socketio import SocketIO

from .config import settingsData, userInputs, currPosition, reqPosition, socketio


def update_client():
    socketio.emit("updateInputs", {
        "userInputs": userInputs,
        "settingsData" : settingsData,
        })
    socketio.emit("updatePosition", {
    	"currPosition" : currPosition,
    	"reqPosition"  : reqPosition, 
    	})


def init_comms_handlers():
    @socketio.on('updatePresets')
    def updatePresets(data):
        global userInputs
        # Update templateData with received values
        userInputs['feedrate'] = int(data.get("feedrate", 0))

        # Emit updated data to all clients
        update_client()


