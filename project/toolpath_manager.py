import os

from werkzeug.utils import secure_filename
from flask import send_from_directory, request, redirect, url_for, flash

from .config import socketio, app, BASE_DIR, userInputs
from .visualizer import generate_toolpath_image

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'toolpaths')
ALLOWED_EXTENSIONS = {'tp'}

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

    @socketio.on("delete_file")
    def handle_delete_file(filename):
        try:
            base_name = os.path.splitext(os.path.basename(filename))[0]
            
            tp_path = os.path.join(BASE_DIR, "toolpaths", f"{base_name}.TP")
            png_path = os.path.join(BASE_DIR, "toolpaths", f"{base_name}.png")

            if os.path.exists(tp_path):
                os.remove(tp_path)

            if os.path.exists(png_path):
                os.remove(png_path)

            socketio.emit("file_deleted", filename)
        except Exception as e:
            socketio.emit("error", str(e))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/toolpaths/<path:filename>')
def serve_toolpath_image(filename):
    toolpath_dir = os.path.join(BASE_DIR, 'toolpaths')
    return send_from_directory(toolpath_dir, filename)

@app.route('/upload_toolpath', methods=['POST'])
def upload_toolpath():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.referrer)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.referrer)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(save_path)
        flash('File uploaded successfully!')
        return redirect(request.referrer)
    else:
        flash('Invalid file type. Only .TP files are allowed.')
        return redirect(request.referrer)
