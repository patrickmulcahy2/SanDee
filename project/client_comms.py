from flask_socketio import SocketIO

from .config import settingsData, userInputs, currPosition, reqPosition, socketio, system_states, settingsPID


def update_client():

    socketio.emit("updateInputs", {
        "userInputs": userInputs,
        "settingsData" : settingsData,
        })
    socketio.emit("updatePosition", {
    	"currPosition" : currPosition,
    	"reqPosition"  : reqPosition, 
        "rhoMax"       : settingsData["rhoMax"]
    	})
    socketio.emit("systemStates",{
        "pauseStatus"       : system_states.pauseStatus,
        "clearingStatus"    : system_states.clearingStatus,
        "patterningStatus"    : system_states.patterningStatus,
        })
    socketio.emit("updatePID-gains", {
        "settingsPID"  : settingsPID
        })
    socketio.emit("statusPercent", system_states.statusPercent)



def init_comms_handlers():
    @socketio.on('updatePresets')
    def updatePresets(data):
        # Update templateData with received values
        userInputs['feedrateOffset'] = int(data.get("feedrateOffset", 0))

        requestedFeedrate = settingsData['feedrateDefault'] + userInputs['feedrateOffset']

        if requestedFeedrate <= settingsData["feedrateMax"]:
            userInputs['feedrate'] = requestedFeedrate
        else:
            userInputs['feedrate'] = settingsData["feedrateMax"]

