


from .config import app, socketio, reqPosition


def init_manualControl_handlers():
	@socketio.on('sendPolarCoordinates')
	def recievePolarCoorinates_manual(data):
		global reqPosition

		rhoReq = data.get('rho')
		thetaReq = data.get('theta')

		reqPosition["rhoReq"] = rhoReq
		reqPosition["thetaReq"] = thetaReq

