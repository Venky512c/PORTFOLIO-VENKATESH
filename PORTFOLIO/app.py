import re
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "Venkatesh P – Portfolio.html"
DB_PATH = BASE_DIR / "portfolio.db"

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


@app.route("/")
def index():
    return send_file(HTML_FILE, mimetype="text/html")


@app.route("/<path:filename>")
def serve_file(filename):
    return send_from_directory(BASE_DIR, filename)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/contact", methods=["POST"])
def save_contact_message():
    payload = request.get_json(silent=True) or request.form or {}

    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    message = (payload.get("message") or "").strip()

    if len(name) < 2:
        return jsonify({"success": False, "message": "Enter your name (at least 2 characters)."}), 400

    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"success": False, "message": "Enter a valid email address, like name@example.com."}), 400

    if len(message) < 10:
        return jsonify({"success": False, "message": "Write a message of at least 10 characters."}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO contact_messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message),
    )
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Thanks! Your message has been saved and I will get back to you soon.",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
