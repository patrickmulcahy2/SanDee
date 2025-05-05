import time
import numpy as np

from threading import Event, Lock
from flask import render_template, request, redirect, url_for, session, jsonify

from .config import settingsData, settingsPID, app, socketio, system_states, currPosition, reqPosition
from .utils import calculateParameters, find_peaks

thread_event = Event()
thread_lock = Lock()
thread = None

class ImpulseData:
    def __init__(self):
        self.timeData = np.array([])
        self.thetaPosition = np.array([])
        self.rhoPosition = np.array([])
        self.timeData_last = np.array([])
        self.thetaPosition_last = np.array([])
        self.rhoPosition_last = np.array([])
        self.riseTime_last = 0
        self.settlingTime_last = 0
        self.overshoot_last = 0
        self.peak_last = 0
        self.riseTime = 0
        self.settlingTime = 0
        self.overshoot = 0
        self.peak = 0

    def clear_data(self):
        self.timeData_last = self.timeData
        self.thetaPosition_last = self.thetaPosition
        self.rhoPosition_last = self.rhoPosition

        self.riseTime_last = self.riseTime
        self.settlingTime_last = self.settlingTime
        self.overshoot_last = self.overshoot
        self.peak_last = self.peak

        self.timeData = np.array([])
        self.thetaPosition = np.array([])
        self.rhoPosition = np.array([])

        self.riseTime = 0
        self.settlingTime = 0
        self.overshoot = 0
        self.peak = 0
impulse_data = ImpulseData()


def init_tuner_handlers():
    @socketio.on('disable_motors')
    def disable_motors():
        system_states.PID_active = False
        print("Disabling PID Controllers")

    @socketio.on('enable_motors')
    def enable_motors():
        system_states.PID_active = True
        print("Enabling PID Controllers")

    @socketio.on('check_tune')
    def check_tune(data):
        startPoint = data['startPoint']
        moveMagnitude = data['moveMagnitude']
        newPos = startPoint + moveMagnitude
        recordLength = data['recordLength']
        axis = data['axis']

        system_states.PID_active = True
        #reset position of axis to starting point
        provideImpulse(axis, startPoint)
        socketio.sleep(3)

        if axis == "rho":
            moveMagnitude_adj = moveMagnitude * settingsData["rhoMax"]/100
            newPos_adj = newPos * settingsData["rhoMax"]/100
        elif axis == "theta":
            moveMagnitude_adj = moveMagnitude * 360 / 100
            newPos_adj = newPos * 360 / 100
        else:
            raise ValueError("Invalid axis")

        startRecording()
        provideImpulse(axis, newPos_adj)
        socketio.sleep(recordLength)
        stopRecording()

        impulse_data.timeData = zeroTime()

        if axis == "rho":
            posData = impulse_data.rhoPosition
        elif axis == "theta":
            posData = impulse_data.thetaPosition
        else:
            raise ValueError("Invalid axis")

        impulse_data.riseTime, impulse_data.settlingTime, impulse_data.overshoot, impulse_data.peak = calculateParameters(newPos_adj, moveMagnitude_adj, posData)

        plotData()

        impulse_data.clear_data()

    @socketio.on('update_pid')
    def handle_pid_update(data):
        setting = data['setting']
        value = data['value']
        if setting in settingsPID:
            settingsPID[setting] = value
            print(f"[PID Update] {setting} set to {value:.3f}")
        else:
            print(f"[PID Update] Unknown setting: {setting}")


    @socketio.on('zieglerNichols')
    def zieglerNichols(data):
        startPoint = data['startPoint']
        moveMagnitude = data['moveMagnitude']
        newPos = startPoint + moveMagnitude
        recordLength = data['recordLength']
        axis = data['axis']

        if axis == "rho":
            kp = "kp_Rho"
            ki = "ki_Rho"
            kd = "kd_Rho"
        elif axis == "theta":
            kp = "kp_Theta"
            ki = "ki_Theta"
            kd = "kd_Theta"
        else:
            raise ValueError("Invalid axis")

        critGainFound = False

        settingsPID[ki] = 0
        settingsPID[kd] = 0

        #reset position of axis to starting point
        provideImpulse(axis, startPoint)
        socketio.sleep(3)
        system_states.PID_active = False

        if axis == "rho":
            moveMagnitude_adj = moveMagnitude * settingsData["rhoMax"]/100
            newPos_adj = newPos * settingsData["rhoMax"]/100
        elif axis == "theta":
            moveMagnitude_adj = moveMagnitude * 360 / 100
            newPos_adj = newPos * 360 / 100
        else:
            raise ValueError("Invalid axis")

        Kp = 0.25

        settingsPID[kp] = Kp

        while not critGainFound:
            if Kp > 10:
                print("Critical Gain not found, exiting loop.")
                break
            startRecording()
            system_states.PID_active = True
            provideImpulse(axis, newPos_adj)
            socketio.sleep(recordLength)
            stopRecording()
            system_states.PID_active = False

            impulse_data.timeData = zeroTime()

            if axis == "rho":
                posData = impulse_data.rhoPosition
            elif axis == "theta":
                posData = impulse_data.thetaPosition
            else:
                raise ValueError("Invalid axis")

            impulse_data.riseTime, impulse_data.settlingTime, impulse_data.overshoot, impulse_data.peak = calculateParameters(newPos_adj, moveMagnitude_adj, posData)
            
            plotData()

            previous_amplitude = None
            amplitude_trend = "increasing"

            # Detecting amplitude trend by finding the peaks (or troughs) in the data
            peaks = find_peaks(posData)[0]
            if len(peaks) >= 2:
                # Calculate amplitude as the difference between the first and last peaks
                amplitude = np.abs(posData[peaks[-1]] - posData[peaks[0]])

                if previous_amplitude is not None:
                    if amplitude > previous_amplitude:
                        amplitude_trend = "increasing"
                    elif amplitude < previous_amplitude:
                        amplitude_trend = "decreasing"
                    else:
                        amplitude_trend = "static"
                
                # Update the previous amplitude for the next comparison
                previous_amplitude = amplitude

            # Calculate the period of the oscillation (time between peaks)
            periods = []
            if len(peaks) >= 2:
                for i in range(1, len(peaks)):
                    # Find time difference between consecutive peaks
                    time_diff = impulse_data.timeData[peaks[i]] - impulse_data.timeData[peaks[i-1]]
                    periods.append(time_diff)
                
                # Calculate the average period
                average_period = np.mean(periods)

            # Adjust Kp based on amplitude trend
            if amplitude_trend == "increasing":
                Kp += 0.125
                print("Amplitude increasing, increasing Kp.")
            elif amplitude_trend == "decreasing":
                Kp -= 0.125/2
                print("Amplitude decreasing, decreasing Kp.")
                critGainFound = True
                Pu = average_period
                settingsPID[kp] = 0.8 * Kp
                settingsPID[ki] = 0.5 * Pu
                settingsPID[kd] = 0.25 * Pu
            elif amplitude_trend == "static":
                print("Amplitude static, keeping Kp.")
                critGainFound = True
                Pu = average_period
                settingsPID[kp] = 0.8 * Kp
                settingsPID[ki] = 0.5 * Pu
                settingsPID[kd] = 0.25 * Pu

            settingsPID[kp] = Kp
            impulse_data.clear_data()

        system_states.PID_active = True



def provideImpulse(axis, newPos_adj):
    if axis == "rho":
        reqPosition["rhoReq"] = newPos_adj
    elif axis == "theta":
        reqPosition["thetaReq"] = newPos_adj

def recordData(event):
    global thread
    try:
        while event.is_set():
            impulse_data.timeData = np.append(impulse_data.timeData, time.time())
            impulse_data.thetaPosition = np.append(impulse_data.thetaPosition, currPosition["thetaCurr"])
            impulse_data.rhoPosition = np.append(impulse_data.rhoPosition, currPosition["rhoCurr"])
            socketio.sleep(system_states.dT)
    finally:
        event.clear()
        thread = None


def startRecording():
    global thread
    with thread_lock:
        if thread is None:
            thread_event.set()
            thread = socketio.start_background_task(recordData, thread_event)

def stopRecording():
    global thread
    thread_event.clear()
    with thread_lock:
        if thread is not None:
            thread.join()
            thread = None

def zeroTime():
    time_zero = impulse_data.timeData[0]
    timeData_adj = impulse_data.timeData - time_zero

    return timeData_adj


def plotData():
    print("Plotting Impulse!")
    socketio.emit('plotData', {
        'timeData': impulse_data.timeData.tolist(),
        'rhoPosition': impulse_data.rhoPosition.tolist(),
        'thetaPosition': impulse_data.thetaPosition.tolist(),
        'timeData_last': impulse_data.timeData_last.tolist(),
        'rhoPosition_last': impulse_data.rhoPosition_last.tolist(),
        'thetaPosition_last': impulse_data.thetaPosition_last.tolist(),
        'riseTime': {
            'current': impulse_data.riseTime,
            'last': impulse_data.riseTime_last
        },
        'settlingTime': {
            'current': impulse_data.settlingTime,
            'last': impulse_data.settlingTime_last
        },
        'overshoot': {
            'current': impulse_data.overshoot,
            'last': impulse_data.overshoot_last
        },
        'peak': {
            'current': impulse_data.peak,
            'last': impulse_data.peak_last
        }
    })


@app.route("/PID_tuner")
def PID_tuner():
    return render_template("PID_tuner.html")