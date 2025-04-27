


from .config import app, socketio


def init_utils_handlers():
	@socketio.on('utility')
	def utility(data):
    	pass

