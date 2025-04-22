from project.app import socketio, app

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000, host='0.0.0.0', allow_unsafe_werkzeug=True)