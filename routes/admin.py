"""
LocalLink - Admin Routes
Teacher admin panel: user management, session monitoring, file uploads
"""

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from database import (
    get_all_users, add_user, delete_user,
    get_active_sessions, force_logout, get_all_files
)
from functools import wraps

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            return redirect(url_for("chat.dashboard"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/admin")
@admin_required
def panel():
    """Main admin dashboard."""
    users    = get_all_users()
    sessions = get_active_sessions()
    files    = get_all_files()
    return render_template(
        "admin.html",
        users=users,
        active_sessions=sessions,
        files=files,
        full_name=session["full_name"]
    )


@admin_bp.route("/admin/add_user", methods=["POST"])
@admin_required
def add_user_route():
    """Register a new student account."""
    student_id = request.form.get("student_id", "").strip()
    password   = request.form.get("password", "").strip()
    full_name  = request.form.get("full_name", "").strip()

    if not student_id or not password or not full_name:
        flash("error:All fields are required.")
        return redirect(url_for("admin.panel"))

    success = add_user(student_id, password, full_name)
    if success:
        flash(f"success:Student '{full_name}' ({student_id}) added successfully.")
    else:
        flash(f"error:ID Number '{student_id}' already exists.")

    return redirect(url_for("admin.panel"))


@admin_bp.route("/admin/delete_user/<student_id>", methods=["POST"])
@admin_required
def delete_user_route(student_id):
    """Remove a student account and their active session."""
    delete_user(student_id)
    flash(f"success:Student {student_id} has been removed.")
    return redirect(url_for("admin.panel"))


@admin_bp.route("/admin/force_logout/<student_id>", methods=["POST"])
@admin_required
def force_logout_route(student_id):
    """Force a student off the network."""
    force_logout(student_id)
    flash(f"success:Session for {student_id} has been terminated.")
    return redirect(url_for("admin.panel"))
