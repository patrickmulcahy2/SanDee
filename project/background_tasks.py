import threading
from threading import Lock


from .config import templateData, settingsData, socketio, stopCheck
from .client_comms import update_client
from .state_changer import setPressure, setVoltage, readVoltage, readCurrent

data_thread_lock = Lock()

    
def updateData():
    global thread
    """Continuously sends templateData to the client."""
    while True:
        with data_thread_lock:
            update_client()
        socketio.sleep(1)  # Send data every second (adjust as needed)

def safetyCheck():
    global templateData, stopCheck
    while True:
        prev_state = templateData["safetyCurrState"]
        templateData["safetyCurrState"] = all([
            templateData["dumpCurrState"],
            templateData["chargeCurrState"],
            templateData["pressureCurrState"],
            stopCheck.value,
            not templateData["hvToggleCurrState"]
        ])
        if templateData["safetyCurrState"] != prev_state:  # Emit only if changed
            socketio.emit("updateData", templateData)
        socketio.sleep(1)

def pressureVoltageSet():
    while True:
        if setPressure(templateData['currPressureGauge_AltAdj']) is None:  # Check for error (None or -1)
            print("Error in setting pressure, breaking the loop.")
            socketio.emit("logMessage", {
                "type": "error",
                "errorMessage": "Error in setting pressure, disabling Sequent.",
            })
            break  # Exit the loop if there was an error setting the pressure

        if setVoltage(templateData['vSetpoint']) is None:  # Check for error (None or -1)
            print("Error in setting voltage, breaking the loop.")
            socketio.emit("logMessage", {
                "type": "error",
                "errorMessage": "Error in setting voltage, disabling Sequent.",
            })
            break  # Exit the loop if there was an error setting the voltage
            
        socketio.sleep(1)

def pressureVoltageCurrentRead():
    while True:
        voltage_kV = readVoltage()
        if voltage_kV is None:  # Check for error (None or -1)
            print("Error in reading voltage, breaking the loop.")
            socketio.emit("logMessage", {
                "type": "error",
                "errorMessage": "Error in reading voltage, disabling Sequent.",
            })
            break  # Exit the loop if there was an error reading voltage

        current_mA = readCurrent()
        if current_mA is None:  # Check for error (None or -1)
            print("Error in reading current, breaking the loop.")
            socketio.emit("logMessage", {
                "type": "error",
                "errorMessage": "Error in reading current, disabling Sequent.",
            })
            break  # Exit the loop if there was an error reading current

        maxVoltage = settingsData['supplyVoltage']
        maxCurrent = settingsData['supplyCurrent']
        plotLength_Points = settingsData['plotLength'] * settingsData['plotSampleRate']

        data = {
            "voltage": voltage_kV,
            "current": current_mA,
            "supplyVoltage": maxVoltage,
            "supplyCurrent": maxCurrent,
            "plotLength_Points": plotLength_Points
        }

        socketio.emit("updatePlot", data)

        sampleRate = (settingsData['plotSampleRate'])

        #Making sure sample rate set between 1 and 32 Hz
        if sampleRate == 0:
            sampleRate = 1
        elif sampleRate > 32:
            sampleRate = 32

        socketio.sleep(1/sampleRate)