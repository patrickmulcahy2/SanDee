from flask_socketio import SocketIO

from .config import userInputs, currPosition, reqPosition, socketio
from .utilities import sparkGapPressureCalc, pressureAltAdjCalc


def update_client():
    socketio.emit("updateInputs", userInputs)
    socketio.emit("updatePosition", {
    	"currPos" : currPosition,
    	"reqPos"  : reqPosition, }
    	)


def init_comms_handlers():
    @socketio.on('updatePresets')
    def updatePresets(data):
        global templateData
        # Update templateData with received values
        templateData['feedrate'] = int(data.get("feedrate", 0))

        # Emit updated data to all clients
        update_client()


