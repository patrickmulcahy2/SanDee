


from .config import app, socketio


def init_controlCommands_handlers():
    @socketio.on('go')
    def go():
    	pass

    @socketio.on('pause')
    def pause():
    	pass

    @socketio.on('clear')
    def clear():
    	pass