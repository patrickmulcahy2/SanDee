


from .config import app, socketio, reqPosition, settingsData, system_states


def init_manualControl_handlers():
	@socketio.on('sendPolarCoordinates')
	def recievePolarCoorinates_manual(data):
		canDraw = not system_states.patterningStatus and not system_states.pauseStatus and not system_states.clearingStatus

		if canDraw:
			rhoReq_normalized = data.get('rho')
			thetaReq = data.get('theta')

			reqPosition["rhoReq"] = rhoReq_normalized * settingsData["rhoMax"]
			reqPosition["thetaReq"] = thetaReq
