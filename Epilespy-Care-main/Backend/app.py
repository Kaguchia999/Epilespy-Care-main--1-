from flask import Flask, jsonify
from flask_cors import CORS

from db import get_connection

app = Flask(__name__)
CORS(app)

@app.route("/api/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"status": "ok", "database": "connected"})
    except Exception:
        app.logger.exception("Database health check failed")
        return jsonify({"status": "error", "message": "Database connection failed"}), 500

if __name__ == "__main__":
    app.run(debug=True) 