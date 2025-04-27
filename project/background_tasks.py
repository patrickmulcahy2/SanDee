import threading
from threading import Lock


from .config import settingsData, socketio
#from .client_comms import update_client
#from .state_changer import setPressure, setVoltage, readVoltage, readCurrent

data_thread_lock = Lock()

    
def updateData():
    global thread
    """Continuously sends templateData to the client."""
    while True:
        with data_thread_lock:
            update_client()
        socketio.sleep(1)  # Send data every second (adjust as needed)
