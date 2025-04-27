

from flask import render_template, request, redirect, url_for, session, jsonify

from .config import settingsData, settingsPID, app, socketio



@app.route("/settings")
def settings():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("PID-tuner.html")