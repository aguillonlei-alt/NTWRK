"""
LocalLink - Chat Routes
Handles real-time messaging via Socket.IO
"""

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session
)
from flask_socketio import emit, join_room
from database import save_message, get_recent_messages, get_all_files
from datetime import datetime

chat_bp = Blueprint("chat", __name__)

ROOM = "locallink_room"


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@chat_bp.route("/dashboard")
@login_required
def dashboard():
    """Main chat + file dashboard for students."""
    messages = get_recent_messages(limit=100)
    files    = get_all_files()
    return render_template(
        "dashboard.html",
        messages=messages,
        files=files,
        student_id=session["student_id"],
        full_name=session["full_name"],
        role=session.get("role", "student")
    )


def register_socket_events(socketio):
    """Register all Socket.IO event handlers."""

    @socketio.on("connect")
    def on_connect():
        if "student_id" not in session:
            return False  # Reject unauthenticated connections
        join_room(ROOM)
        # Notify others that user joined
        emit("user_event", {
            "type": "join",
            "name": session.get("full_name", "Unknown"),
            "student_id": session.get("student_id"),
            "timestamp": datetime.now().strftime("%I:%M %p")
        }, room=ROOM)

    @socketio.on("disconnect")
    def on_disconnect():
        if "student_id" in session:
            emit("user_event", {
                "type": "leave",
                "name": session.get("full_name", "Unknown"),
                "student_id": session.get("student_id"),
                "timestamp": datetime.now().strftime("%I:%M %p")
            }, room=ROOM)

    @socketio.on("send_message")
    def on_message(data):
        """Handle incoming text message from a client."""
        if "student_id" not in session:
            return

        student_id = session["student_id"]
        full_name  = session["full_name"]
        content    = data.get("content", "").strip()

        if not content:
            return

        # Save to database
        save_message(student_id, full_name, content, msg_type="text")

        # Broadcast to all connected clients
        emit("receive_message", {
            "student_id": student_id,
            "full_name":  full_name,
            "content":    content,
            "msg_type":   "text",
            "timestamp":  datetime.now().strftime("%I:%M %p")
        }, room=ROOM)

    @socketio.on("file_pushed")
    def on_file_pushed(data):
        """Broadcast a file push notification to all connected clients."""
        emit("receive_file_push", {
            "filename":      data.get("filename"),
            "original_name": data.get("original_name"),
            "file_type":     data.get("file_type"),
            "uploaded_by":   data.get("uploaded_by"),
            "timestamp":     datetime.now().strftime("%I:%M %p")
        }, room=ROOM)
