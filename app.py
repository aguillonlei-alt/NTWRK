"""
LocalLink - Offline Local Network System
Main Application Entry Point
"""

from flask import Flask
from flask_socketio import SocketIO
from database import init_db
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.admin import admin_bp
from routes.files import files_bp
import os

# ── App Setup ─────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "locallink_secret_key_2026"
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200MB max upload

# ── SocketIO Setup ────────────────────────────────────────────────
socketio = SocketIO(app, cors_allowed_origins="*")

# ── Register Blueprints ───────────────────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(files_bp)

# ── Attach SocketIO to chat routes ────────────────────────────────
from routes.chat import register_socket_events
register_socket_events(socketio)

# ── Initialize Database ───────────────────────────────────────────
with app.app_context():
    init_db()

# ── Run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    socketio.run(app, host="0.0.0.0", port=80, debug=False)
