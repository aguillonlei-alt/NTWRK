"""
LocalLink - File Routes
Handles teacher file uploads, student downloads, and auto-push notifications
"""

from flask import (
    Blueprint, request, redirect, url_for,
    session, flash, send_from_directory,
    current_app, jsonify
)
from database import save_file_record, get_all_files, delete_file_record
from werkzeug.utils import secure_filename
import os
import uuid

files_bp = Blueprint("files", __name__)

ALLOWED_EXTENSIONS = {
    "pdf", "ppt", "pptx", "doc", "docx",
    "xls", "xlsx", "txt", "png", "jpg",
    "jpeg", "gif", "mp4", "mp3", "zip"
}


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "student_id" not in session or session.get("role") != "admin":
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@files_bp.route("/upload", methods=["POST"])
@admin_required
def upload_file():
    """Admin uploads a file to the Pi. Optionally auto-pushes to all students."""
    if "file" not in request.files:
        flash("error:No file selected.")
        return redirect(url_for("admin.panel"))

    file      = request.files["file"]
    auto_push = 1 if request.form.get("auto_push") == "1" else 0

    if file.filename == "":
        flash("error:No file selected.")
        return redirect(url_for("admin.panel"))

    if not allowed_file(file.filename):
        flash("error:File type not allowed.")
        return redirect(url_for("admin.panel"))

    # Generate unique filename to avoid conflicts
    ext           = file.filename.rsplit(".", 1)[1].lower()
    unique_name   = f"{uuid.uuid4().hex}.{ext}"
    original_name = secure_filename(file.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, unique_name)
    file.save(save_path)

    file_size = os.path.getsize(save_path)
    save_file_record(
        filename=unique_name,
        original_name=original_name,
        uploaded_by=session["full_name"],
        file_size=file_size,
        file_type=ext,
        auto_push=auto_push
    )

    if auto_push:
        # Trigger Socket.IO push event via a separate endpoint
        flash(f"success:'{original_name}' uploaded and pushed to all connected students.")
        return redirect(url_for("admin.panel") + f"?push=1&fname={unique_name}&oname={original_name}&ftype={ext}")

    flash(f"success:'{original_name}' uploaded successfully.")
    return redirect(url_for("admin.panel"))


@files_bp.route("/download/<filename>")
@login_required
def download_file(filename):
    """Serve a file for download."""
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(upload_folder, filename, as_attachment=True)


@files_bp.route("/files/delete/<int:file_id>", methods=["POST"])
@admin_required
def delete_file(file_id):
    """Admin deletes a file from the system."""
    file = delete_file_record(file_id)
    if file:
        # Remove physical file
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, file["filename"])
        if os.path.exists(file_path):
            os.remove(file_path)
        flash(f"success:File '{file['original_name']}' deleted.")
    return redirect(url_for("admin.panel"))


@files_bp.route("/api/files")
@login_required
def api_files():
    """JSON endpoint for the file list — used by the dashboard to refresh."""
    files = get_all_files()
    return jsonify([dict(f) for f in files])
