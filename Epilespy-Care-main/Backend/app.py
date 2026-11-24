# app.py - the backend server
from flask import Flask, jsonify, request
from flask_cors import CORS
import bcrypt
from db import get_connection
app = Flask(__name__)
CORS(app)
# health check: tells us whether the database can be reached
@app.route("/api/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"status": "ok", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
# administrator login
@app.route("/api/login/admin", methods=["POST"])
def login_admin():
    # read the email and password sent by the login page
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    # look for an administrator with this email
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Administrator WHERE email = %s", (email,))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()
    # if no administrator has this email, refuse
    if admin is None:
        return jsonify({"message": "Wrong email or password"}), 401
    # compare the typed password with the stored hash
    if not bcrypt.checkpw(password.encode(), admin["password_hash"].encode()):
        return jsonify({"message": "Wrong email or password"}), 401
    # refuse accounts that have been switched off
    if admin["status"] != "active":
        return jsonify({"message": "This account is not active"}), 403
    # everything is correct, so let them in
    return jsonify({
        "message": "Login successful",
        "admin_id": admin["admin_id"],
        "full_name": admin["full_name"]
    })
if __name__ == "__main__":
    app.run(debug=True)