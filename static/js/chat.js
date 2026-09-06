/**
 * LocalLink — Chat & Real-Time Events
 * Handles Socket.IO connection, messaging, and file push notifications
 */

const socket = io();
const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const sendBtn      = document.getElementById("sendBtn");
const pushNotif    = document.getElementById("pushNotification");
const pushText     = document.getElementById("pushText");

// ── Scroll to bottom of chat ──────────────────────────────────
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
scrollToBottom();

// ── Render a new message bubble ───────────────────────────────
function renderMessage(data) {
    const div = document.createElement("div");
    const isOwn = data.student_id === CURRENT_USER_ID;

    if (data.msg_type === "system") {
        div.className = "message message-system";
        div.innerHTML = `<div class="msg-bubble">${escHtml(data.content)}</div>`;
    } else {
        div.className = `message ${isOwn ? "message-own" : "message-other"}`;
        div.innerHTML = `
            ${!isOwn ? `<div class="msg-name">${escHtml(data.full_name)}</div>` : ""}
            <div class="msg-bubble">${escHtml(data.content)}</div>
            <div class="msg-meta">${escHtml(data.timestamp)}</div>
        `;
    }

    chatMessages.appendChild(div);
    scrollToBottom();
}

// ── Render a file push notification card ──────────────────────
function renderFilePush(data) {
    // Show push notification banner
    pushText.textContent =
        `New file from teacher: ${data.original_name} — click Download in Files panel`;
    pushNotif.classList.remove("hidden");

    // Also add a system message in chat
    const div = document.createElement("div");
    div.className = "message message-system";
    div.innerHTML = `
        <div class="msg-bubble">
            📎 Teacher shared a file: <strong>${escHtml(data.original_name)}</strong>
            — check the Files panel to download.
        </div>
    `;
    chatMessages.appendChild(div);
    scrollToBottom();

    // Refresh file list
    refreshFileList();
}

// ── Dismiss push notification banner ─────────────────────────
function dismissPush() {
    pushNotif.classList.add("hidden");
}

// ── Refresh file list via API ─────────────────────────────────
function refreshFileList() {
    fetch("/api/files")
        .then(r => r.json())
        .then(files => {
            const list = document.getElementById("fileList");
            if (!files.length) {
                list.innerHTML = '<div class="empty-state">No files uploaded yet.</div>';
                return;
            }
            list.innerHTML = files.map(f => {
                const icon = getFileIcon(f.file_type);
                const size = (f.file_size / 1024).toFixed(1);
                return `
                    <div class="file-item">
                        <div class="file-icon">${icon}</div>
                        <div class="file-info">
                            <div class="file-name">${escHtml(f.original_name)}</div>
                            <div class="file-meta">${size} KB &nbsp;|&nbsp; ${f.uploaded_at.slice(0,16)}</div>
                        </div>
                        <a href="/download/${f.filename}" class="btn-download" download>Download</a>
                    </div>
                `;
            }).join("");
        })
        .catch(err => console.error("File list refresh failed:", err));
}

// ── File type icon helper ─────────────────────────────────────
function getFileIcon(type) {
    const icons = {
        pdf: "📄", ppt: "📊", pptx: "📊",
        doc: "📝", docx: "📝", xls: "📗", xlsx: "📗",
        jpg: "🖼️", jpeg: "🖼️", png: "🖼️", gif: "🖼️",
        mp4: "🎬", mp3: "🎵", zip: "📦"
    };
    return icons[type] || "📎";
}

// ── Escape HTML to prevent XSS ────────────────────────────────
function escHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

// ── Send a message ────────────────────────────────────────────
function sendMessage() {
    const content = messageInput.value.trim();
    if (!content) return;
    socket.emit("send_message", { content });
    messageInput.value = "";
    messageInput.focus();
}

sendBtn.addEventListener("click", sendMessage);
messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// ── Socket.IO Event Listeners ─────────────────────────────────
socket.on("connect", () => {
    console.log("LocalLink connected:", socket.id);
});

socket.on("disconnect", () => {
    console.log("LocalLink disconnected.");
});

socket.on("receive_message", (data) => {
    renderMessage(data);
});

socket.on("user_event", (data) => {
    const action = data.type === "join" ? "joined the network" : "left the network";
    renderMessage({
        student_id: "__system__",
        content: `${data.name} ${action}`,
        timestamp: data.timestamp,
        msg_type: "system"
    });

    // Update online count display
    updateOnlineCount();
});

socket.on("receive_file_push", (data) => {
    renderFilePush(data);
});

// ── Online count (simple implementation) ─────────────────────
function updateOnlineCount() {
    const indicator = document.getElementById("onlineCount");
    if (indicator) {
        indicator.textContent = "Online";
    }
}
