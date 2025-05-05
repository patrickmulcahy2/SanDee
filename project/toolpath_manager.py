import os

from flask import send_from_directory

from .config import socketio, app, BASE_DIR, userInputs
from .visualizer import generate_toolpath_image

def init_toolpath_handlers():
    @socketio.on('requestToolpathList')
    def toolpathList():
        # Get the path to the toolpaths folder
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # One level up from app.py
        toolpath_dir = os.path.join(base_dir, "toolpaths")

        # Get all .TP files in the directory
        listTP = [
            f for f in os.listdir(toolpath_dir)
            if os.path.isfile(os.path.join(toolpath_dir, f)) and f.lower().endswith(".tp")
        ]

        # Generate image for each toolpath file
        for filename in listTP:
            full_path = os.path.join(toolpath_dir, filename)
            generate_toolpath_image(full_path)

        # Emit the list back to the client
        socketio.emit("toolpathlist", listTP)

    @socketio.on("newSelected_TP")
    def newSelection(filepath):
        filepath_png = filepath
        filepath_TP = filepath_png.replace(".png", ".TP")

        userInputs["selected_TP"] = filepath_TP




@app.route('/toolpaths/<path:filename>')
def serve_toolpath_image(filename):
    toolpath_dir = os.path.join(BASE_DIR, 'toolpaths')
    return send_from_directory(toolpath_dir, filename)