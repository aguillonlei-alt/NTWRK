"""
LocalLink - Authentication Routes
Handles captive portal login, logout, and session management
"""

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from database import get_user, create_session, delete_session, is_session_active

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    """Root — redirect to login or dashboard."""
    if "student_id" in session:
        return redirect(url_for("chat.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Captive portal login page."""
    if "student_id" in session:
        return redirect(url_for("chat.dashboard"))

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        password   = request.form.get("password", "").strip()
        device_ip  = request.remote_addr

        # Validate credentials
        user = get_user(student_id)
        if not user:
            flash("error:Invalid ID Number or Password.")
            return render_template("login.html")

        if user["password"] != password:
            flash("error:Invalid ID Number or Password.")
            return render_template("login.html")

        # Check for duplicate active session
        if is_session_active(student_id) and user["role"] != "admin":
            flash("conflict:This ID is already connected on another device. "
                  "Please log out from the other device first.")
            return render_template("login.html")

        # Admin goes directly to admin panel
        if user["role"] == "admin":
            session["student_id"] = student_id
            session["full_name"]  = user["full_name"]
            session["role"]       = "admin"
            create_session(student_id, device_ip)
            return redirect(url_for("admin.panel"))

        # Grant access
        session["student_id"] = student_id
        session["full_name"]  = user["full_name"]
        session["role"]       = "student"
        create_session(student_id, device_ip)
        return redirect(url_for("chat.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Clear session and redirect to login."""
    student_id = session.get("student_id")
    if student_id:
        delete_session(student_id)
    session.clear()
    return redirect(url_for("auth.login"))
