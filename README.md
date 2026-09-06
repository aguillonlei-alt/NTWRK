# LocalLink — Offline Local Network System
**SHS STEM Research Project | A.Y. 2026-2027**

---

## Project Structure

```
locallink/
├── app.py                  ← Main entry point — run this to start
├── database.py             ← All database operations (SQLite)
├── requirements.txt        ← Python packages needed
├── README.md               ← This file
│
├── routes/
│   ├── __init__.py
│   ├── auth.py             ← Login, logout, captive portal
│   ├── chat.py             ← Dashboard + Socket.IO chat events
│   ├── admin.py            ← Admin panel routes
│   └── files.py            ← File upload, download, delete
│
├── templates/
│   ├── login.html          ← Captive portal login page
│   ├── dashboard.html      ← Student chat + file dashboard
│   └── admin.html          ← Teacher admin panel
│
├── static/
│   ├── css/style.css       ← All styles
│   ├── js/chat.js          ← Real-time chat frontend logic
│   └── uploads/            ← Uploaded files stored here
│
└── instance/
    └── locallink.db        ← SQLite database (auto-created on first run)
```

---

## How to Run

### First time setup (on the Pi):
```bash
pip3 install -r requirements.txt --break-system-packages
python3 app.py
```

### Update code from GitHub:
```bash
cd ~/locallink
git pull
sudo systemctl restart locallink
```

---

## Default Admin Login
- **ID Number:** admin
- **Password:** admin2026

Change this in `database.py` → `init_db()` before deployment.

---

## Features
- Captive portal login (ID + Password)
- Duplicate session blocking
- Real-time group chat (Socket.IO)
- File upload by teacher (PDF, PPT, DOCX, images, etc.)
- Auto-push file notification to all connected students
- Admin panel: register students, monitor sessions, force logout
- Works 100% offline — no internet required
