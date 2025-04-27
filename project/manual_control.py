


from .config import app, socketio


def init_manualControl_handlers():
	@socketio.on('manual')
	def manual(data):
		pass

