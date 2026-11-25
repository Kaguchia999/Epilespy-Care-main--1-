# app.py - the backend server
from flask import Flask, jsonify, request
from flask_cors import CORS
import bcrypt
import bcrypt
import mysql.connector
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
    # ======================================
# PATIENT MEDICATIONS + REMINDER SCHEDULE
# ======================================

@app.route("/api/medications/<int:patient_id>", methods=["GET"])
def get_medications(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT m.med_id,
                  m.medication_name,
                  m.strength,
                  m.dose_amount AS frequency,
                  TIME_FORMAT(r.reminder_time, '%H:%i') AS reminder_time,
                  m.instructions,
                  m.is_active
           FROM medication m
           LEFT JOIN reminderschedule r ON m.med_id = r.med_id
           WHERE m.patient_id = %s AND m.is_active = 1
           ORDER BY m.med_id DESC""",
        (patient_id,),
    )
    medications = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(medications)


@app.route("/api/medications", methods=["POST"])
def add_medication():
    data = request.get_json()
    patient_id = data.get("patient_id")
    medication_name = data.get("medication_name", "").strip()
    dosage = data.get("dosage", "").strip()
    frequency = data.get("frequency", "").strip()
    reminder_time = data.get("reminder_time", "").strip()
    start_date = data.get("start_date", "").strip()
    notes = data.get("notes", "").strip()

    if not patient_id or not medication_name or not dosage or not reminder_time:
        return jsonify({"message": "Please fill in medication name, dosage, and time"}), 400

    instructions = f"Start: {start_date}" + (f" | {notes}" if notes else "") if start_date else notes

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Save the medication details
        cursor.execute(
            """INSERT INTO medication (patient_id, medication_name, strength, dose_amount, instructions)
               VALUES (%s, %s, %s, %s, %s)""",
            (patient_id, medication_name, dosage, frequency or None, instructions or None),
        )
        med_id = cursor.lastrowid

        # 2. Save the reminder time linked to that new med_id
        cursor.execute(
            """INSERT INTO reminderschedule (med_id, reminder_time, days_of_the_week)
               VALUES (%s, %s, %s)""",
            (med_id, reminder_time, frequency[:20] if frequency else None),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Medication and reminder saved!", "med_id": med_id}), 201


# ======================================
# PATIENT HEALTH RECORDS (SEIZURES + SYMPTOMS)
# ======================================

@app.route("/api/health-records/<int:patient_id>", methods=["GET"])
def get_health_records(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Fetch seizure logs
    cursor.execute(
        """SELECT DATE_FORMAT(seizure_datetime, '%Y-%m-%d') AS record_date,
                  seizure_type,
                  duration_secs,
                  notes
           FROM seizurerecord
           WHERE patient_id = %s""",
        (patient_id,),
    )
    seizures = cursor.fetchall()

    # 2. Fetch non-seizure symptom logs
    cursor.execute(
        """SELECT DATE_FORMAT(symptom_datetime, '%Y-%m-%d') AS record_date,
                  symptom,
                  notes
           FROM symptomrecord
           WHERE patient_id = %s""",
        (patient_id,),
    )
    symptoms = cursor.fetchall()

    cursor.close()
    conn.close()

    records = []

    for row in seizures:
        details = []
        if row["seizure_type"]:
            details.append(row["seizure_type"])
        if row["duration_secs"]:
            details.append(f"{row['duration_secs']}s")
        seizure_label = f"Yes ({', '.join(details)})" if details else "Yes"

        # Separate symptoms and observations if both were stored in notes
        raw_notes = row["notes"] or ""
        sym_text, obs_text = "-", raw_notes or "-"
        if " | Observations: " in raw_notes:
            parts = raw_notes.split(" | Observations: ", 1)
            sym_text = parts[0].replace("Symptoms: ", "") or "-"
            obs_text = parts[1] or "-"

        records.append({
            "record_date": row["record_date"],
            "had_seizure": True,
            "seizure_occurrence": seizure_label,
            "symptoms": sym_text,
            "observations": obs_text,
        })

    for row in symptoms:
        records.append({
            "record_date": row["record_date"],
            "had_seizure": False,
            "seizure_occurrence": "No",
            "symptoms": row["symptom"] or "-",
            "observations": row["notes"] or "-",
        })

    records.sort(key=lambda item: item["record_date"], reverse=True)
    return jsonify(records)


@app.route("/api/health-records", methods=["POST"])
def add_health_record():
    data = request.get_json()
    patient_id = data.get("patient_id")
    record_date = data.get("record_date", "").strip()
    had_seizure = data.get("seizure", "").strip()
    seizure_type = data.get("seizure_type", "").strip()
    duration_secs = data.get("duration_secs")
    symptoms = data.get("symptoms", "").strip()
    observations = data.get("observations", "").strip()

    if not patient_id or not record_date or not had_seizure:
        return jsonify({"message": "Please fill in the date and seizure selection"}), 400

    record_datetime = f"{record_date} 00:00:00"

    conn = get_connection()
    cursor = conn.cursor()
    try:
        if had_seizure == "Yes":
            clean_duration = int(duration_secs) if str(duration_secs).isdigit() else None
            combined_notes = f"Symptoms: {symptoms or '-'} | Observations: {observations or '-'}"
            cursor.execute(
                """INSERT INTO seizurerecord (patient_id, seizure_datetime, duration_secs, seizure_type, notes)
                   VALUES (%s, %s, %s, %s, %s)""",
                (patient_id, record_datetime, clean_duration, seizure_type or None, combined_notes),
            )
        else:
            cursor.execute(
                """INSERT INTO symptomrecord (patient_id, symptom_datetime, symptom, notes)
                   VALUES (%s, %s, %s, %s)""",
                (patient_id, record_datetime, (symptoms or "General check-in")[:100], observations or None),
            )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Health record saved successfully!"}), 201
if __name__ == "__main__":
    app.run(debug=True)