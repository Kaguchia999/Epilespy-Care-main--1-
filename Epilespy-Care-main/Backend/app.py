# app.py - the backend server

import os
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import bcrypt
import mysql.connector
from db import get_connection

app = Flask(__name__)
CORS(app)

invite_serializer = URLSafeTimedSerializer("epilepsy-care-invite-secret")


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
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Administrator WHERE email = %s", (email,))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()

    if admin is None:
        return jsonify({"message": "Wrong email or password"}), 401

    if not bcrypt.checkpw(password.encode(), admin["password_hash"].encode()):
        return jsonify({"message": "Wrong email or password"}), 401

    if admin["status"] != "active":
        return jsonify({"message": "This account is not active"}), 403

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
                  r.schedule_id,
                  m.medication_name,
                  m.strength,
                  m.dose_amount AS frequency,
                  r.reminder_time,
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
        cursor.execute(
            """INSERT INTO medication (patient_id, medication_name, strength, dose_amount, instructions)
               VALUES (%s, %s, %s, %s, %s)""",
            (patient_id, medication_name, dosage, frequency or None, instructions or None),
        )
        med_id = cursor.lastrowid

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


@app.route("/api/medications/<int:med_id>", methods=["DELETE"])
def delete_medication(med_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE reminderschedule SET is_active = 0 WHERE med_id = %s", (med_id,))
        cursor.execute("UPDATE medication SET is_active = 0 WHERE med_id = %s", (med_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Medication schedule deleted successfully"}), 200


# ======================================
# PATIENT HEALTH RECORDS (SEIZURES + SYMPTOMS)
# ======================================
@app.route("/api/health-records/<int:patient_id>", methods=["GET"])
def get_health_records(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
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

        cursor.execute(
            """SELECT DATE_FORMAT(symptom_datetime, '%Y-%m-%d') AS record_date,
                      symptom,
                      notes
               FROM symptomrecord
               WHERE patient_id = %s""",
            (patient_id,),
        )
        symptoms = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    records = []

    for row in seizures:
        details = []
        if row["seizure_type"]:
            details.append(row["seizure_type"])
        if row["duration_secs"] is not None:
            details.append(f"{row['duration_secs']}s")
        seizure_label = f"Yes ({', '.join(details)})" if details else "Yes"

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
        return jsonify({"message": "Please fill in the date and seizure selection."}), 400

    record_datetime = f"{record_date} 00:00:00"

    conn = get_connection()
    cursor = conn.cursor()
    try:
        if had_seizure == "Yes":
            clean_duration = None
            if duration_secs not in (None, ""):
                try:
                    clean_duration = int(duration_secs)
                except ValueError:
                    clean_duration = None

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
    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Health record saved successfully!"}), 201


# ======================================
# ADMIN: DOCTOR APPLICATIONS
# ======================================
@app.route("/api/admin/doctors", methods=["GET"])
def get_doctor_applications():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT doctor_id,
                  full_name,
                  EMAIL AS email,
                  registration_no,
                  facility,
                  approval_status
           FROM doctor
           ORDER BY FIELD(approval_status, 'pending', 'approved', 'rejected'), doctor_id DESC"""
    )
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(doctors)


@app.route("/api/admin/doctors/<int:doctor_id>", methods=["PUT"])
def update_doctor_status(doctor_id):
    data = request.get_json()
    new_status = data.get("approval_status", "").strip().lower()

    if new_status not in ("approved", "rejected"):
        return jsonify({"message": "Invalid status. Use approved or rejected."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE doctor SET approval_status = %s WHERE doctor_id = %s",
        (new_status, doctor_id),
    )
    conn.commit()
    updated_rows = cursor.rowcount
    cursor.close()
    conn.close()

    if updated_rows == 0:
        return jsonify({"message": "Doctor account not found"}), 404

    return jsonify({"message": f"Doctor application {new_status} successfully!"})


# ======================================
# ADMIN: LIVE SYSTEM USAGE COUNTS
# ======================================
@app.route("/api/admin/usage-stats", methods=["GET"])
def get_usage_stats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM patient")
    patients = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM doctor")
    doctors = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM caregiver")
    caregivers = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return jsonify({
        "total_users": patients + doctors + caregivers,
        "patients": patients,
        "doctors": doctors,
        "caregivers": caregivers,
    })


# ======================================
# ADMIN: MANAGE ALL USER ACCOUNTS
# ======================================
@app.route("/api/admin/users", methods=["GET"])
def get_all_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT patient_id, full_name, email, phone, status FROM patient ORDER BY patient_id DESC"
    )
    patients = cursor.fetchall()

    cursor.execute(
        """SELECT doctor_id, full_name, EMAIL AS email, registration_no, facility, approval_status
           FROM doctor ORDER BY doctor_id DESC"""
    )
    doctors = cursor.fetchall()

    cursor.execute(
        "SELECT caregiver_id, full_name, email, phone, status FROM caregiver ORDER BY caregiver_id DESC"
    )
    caregivers = cursor.fetchall()

    cursor.close()
    conn.close()

    users = []

    for p in patients:
        users.append({
            "id": p["patient_id"],
            "display_id": f"PAT-{p['patient_id']:03d}",
            "full_name": p["full_name"],
            "email": p["email"],
            "role": "patient",
            "status": (p["status"] or "active").lower(),
            "details": f"Phone: {p['phone'] or 'Not provided'}",
        })

    for d in doctors:
        users.append({
            "id": d["doctor_id"],
            "display_id": f"DOC-{d['doctor_id']:03d}",
            "full_name": d["full_name"],
            "email": d["email"],
            "role": "doctor",
            "status": (d["approval_status"] or "pending").lower(),
            "details": f"Reg No: {d['registration_no'] or '-'} | Facility: {d['facility'] or 'Not provided'}",
        })

    for c in caregivers:
        users.append({
            "id": c["caregiver_id"],
            "display_id": f"CRG-{c['caregiver_id']:03d}",
            "full_name": c["full_name"],
            "email": c["email"],
            "role": "caregiver",
            "status": (c["status"] or "active").lower(),
            "details": f"Phone: {c['phone'] or 'Not provided'}",
        })

    return jsonify({
        "counts": {
            "patients": len(patients),
            "doctors": len(doctors),
            "caregivers": len(caregivers),
        },
        "users": users,
    })


@app.route("/api/admin/users/<role>/<int:user_id>/status", methods=["PUT"])
def update_user_account_status(role, user_id):
    data = request.get_json()
    new_status = data.get("status", "").strip().lower()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if role == "patient" and new_status in ("active", "inactive"):
            cursor.execute(
                "UPDATE patient SET status = %s WHERE patient_id = %s",
                (new_status, user_id),
            )
        elif role == "caregiver" and new_status in ("active", "inactive"):
            cursor.execute(
                "UPDATE caregiver SET status = %s WHERE caregiver_id = %s",
                (new_status, user_id),
            )
        elif role == "doctor" and new_status in ("approved", "rejected"):
            cursor.execute(
                "UPDATE doctor SET approval_status = %s WHERE doctor_id = %s",
                (new_status, user_id),
            )
        else:
            return jsonify({"message": "Invalid role or status value"}), 400

        conn.commit()
        updated = cursor.rowcount
    finally:
        cursor.close()
        conn.close()

    if updated == 0:
        return jsonify({"message": "User account not found"}), 404

    return jsonify({"message": f"Account updated to {new_status} successfully!"})


# ======================================
# 1. REGISTER (PATIENT, DOCTOR, INVITED CAREGIVER)
# ======================================
@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.get_json() or {}
    role = (data.get("role") or "").strip().lower()
    full_name = (data.get("fullName") or data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    phone = (data.get("phone") or "").strip()
    registration_no = (data.get("registrationNo") or data.get("registration_no") or "").strip()
    facility = (data.get("facility") or "").strip()
    invite_token = (data.get("inviteToken") or "").strip()

    if role not in ("patient", "caregiver", "doctor"):
        return jsonify({"error": "Invalid account type"}), 400

    if not full_name or not email or not password:
        return jsonify({"error": "Please fill in full name, email, and password"}), 400

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(f"SELECT 1 FROM {role} WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "An account with this email already exists"}), 409

        if role == "patient":
            cursor.execute(
                """INSERT INTO patient (full_name, phone, email, password_hash, status, created_at)
                   VALUES (%s, %s, %s, %s, 'active', NOW())""",
                (full_name, phone or None, email, password_hash),
            )

        elif role == "doctor":
            cursor.execute(
                """INSERT INTO doctor (full_name, EMAIL, password_hash, registration_no, facility, approval_status)
                   VALUES (%s, %s, %s, %s, %s, 'pending')""",
                (full_name, email, password_hash, registration_no or None, facility or None),
            )

        elif role == "caregiver":
            if not invite_token:
                return jsonify({"error": "Caregivers must register using an invitation link from a patient"}), 400

            try:
                invite_data = invite_serializer.loads(invite_token, max_age=604800)  # valid 7 days
            except (BadSignature, SignatureExpired):
                return jsonify({"error": "This invitation link is invalid or has expired"}), 400

            patient_id = invite_data["patient_id"]

            cursor.execute(
                """INSERT INTO caregiver (full_name, phone, email, password_hash, status, created_at)
                   VALUES (%s, %s, %s, %s, 'active', NOW())""",
                (full_name, phone or None, email, password_hash),
            )
            caregiver_id = cursor.lastrowid

            cursor.execute(
                """INSERT INTO patientcaregiverlink (patient_id, caregiver_id, can_view_dose_status, status, invited_at)
                   VALUES (%s, %s, 1, 'active', NOW())""",
                (patient_id, caregiver_id),
            )

        conn.commit()
        return jsonify({"message": "Account created successfully!"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ======================================
# 2. PATIENT SENDS CAREGIVER INVITE
# ======================================
@app.route("/api/caregiver/invite", methods=["POST"])
def create_caregiver_invite():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    caregiver_email = (data.get("caregiver_email") or "").strip().lower()

    if not patient_id or not caregiver_email:
        return jsonify({"error": "Patient ID and caregiver email are required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT full_name FROM patient WHERE patient_id = %s", (patient_id,))
    patient = cursor.fetchone()
    cursor.close()
    conn.close()

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    token = invite_serializer.dumps({
        "patient_id": patient_id,
        "patient_name": patient["full_name"],
        "caregiver_email": caregiver_email,
    })

    invite_link = f"http://127.0.0.1:5000/caregiver/accept-invitation.html?invite={token}"
    print(f"\n[CAREGIVER INVITE] For {caregiver_email}: {invite_link}\n")

    return jsonify({
        "message": f"Invitation link created for {caregiver_email}",
        "invite_link": invite_link,
    }), 200


@app.route("/api/caregiver/invite/<token>", methods=["GET"])
def verify_caregiver_invite(token):
    try:
        invite_data = invite_serializer.loads(token, max_age=604800)
        return jsonify(invite_data), 200
    except (BadSignature, SignatureExpired):
        return jsonify({"error": "Invalid or expired invitation link"}), 400


# ======================================
# 3. LOGIN (PATIENT, CAREGIVER, DOCTOR)
# ======================================
@app.route("/api/login/<role>", methods=["POST"])
def login_user(role):
    role = role.strip().lower()
    if role not in ("patient", "caregiver", "doctor"):
        return jsonify({"error": "Invalid role"}), 400

    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    id_col = f"{role}_id"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {role} WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user is None or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        cursor.close()
        conn.close()
        return jsonify({"error": "Wrong email or password"}), 401

    if role == "doctor" and (user.get("approval_status") or "").lower() != "approved":
        cursor.close()
        conn.close()
        return jsonify({"error": "Your doctor account is still pending admin approval"}), 403

    if role in ("patient", "caregiver") and (user.get("status") or "").lower() != "active":
        cursor.close()
        conn.close()
        return jsonify({"error": "This account is not active"}), 403

    response = {
        "message": "Login successful",
        "role": role,
        id_col: user[id_col],
        "full_name": user["full_name"],
    }

    if role == "caregiver":
        cursor.execute(
            """SELECT patient_id, can_view_dose_status
               FROM patientcaregiverlink
               WHERE caregiver_id = %s AND status = 'active'
               LIMIT 1""",
            (user["caregiver_id"],),
        )
        link = cursor.fetchone()
        if link:
            response["linked_patient_id"] = link["patient_id"]
            response["can_view_dose_status"] = bool(link["can_view_dose_status"])

    cursor.close()
    conn.close()
    return jsonify(response), 200


# ======================================
# ADMIN: SYSTEM ERROR LOGS
# ======================================
@app.route("/api/admin/errors", methods=["GET"])
def get_error_logs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT error_id,
                  module,
                  message,
                  DATE_FORMAT(logged_at, '%d/%m/%Y %H:%i') AS logged_at
           FROM errorlog
           ORDER BY logged_at DESC, error_id DESC"""
    )
    errors = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(errors)


# ======================================
# HELP REQUESTS (PATIENT <-> CAREGIVER)
# ======================================
def get_or_create_template_id(cursor):
    cursor.execute(
        "SELECT template_id FROM helpmessagetemplate WHERE is_current = 1 ORDER BY template_id ASC LIMIT 1"
    )
    row = cursor.fetchone()
    if row:
        return row["template_id"]

    cursor.execute("SELECT template_id FROM helpmessagetemplate ORDER BY template_id ASC LIMIT 1")
    row = cursor.fetchone()
    if row:
        return row["template_id"]

    cursor.execute(
        "INSERT INTO helpmessagetemplate (template_text, is_current, updated_by) VALUES (%s, 1, 1)",
        ("Patient requested assistance.",),
    )
    return cursor.lastrowid


def get_or_create_contact_id(cursor, patient_id):
    cursor.execute(
        "SELECT contact_id FROM caregivercontact WHERE patient_id = %s ORDER BY contact_id ASC LIMIT 1",
        (patient_id,),
    )
    row = cursor.fetchone()
    if row:
        return row["contact_id"]

    cursor.execute("SELECT full_name, phone FROM patient WHERE patient_id = %s", (patient_id,))
    patient = cursor.fetchone() or {}
    contact_name = patient.get("full_name") or "Primary Caregiver"
    phone = patient.get("phone") or "0000000000"

    cursor.execute(
        """INSERT INTO caregivercontact (patient_id, contact_name, phone, relationship)
           VALUES (%s, %s, %s, %s)""",
        (patient_id, contact_name, phone, "Caregiver"),
    )
    return cursor.lastrowid


@app.route("/api/help-requests", methods=["POST"])
def create_help_request():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    message = (data.get("message") or "").strip()

    if not patient_id or not message:
        return jsonify({"error": "Please describe the assistance you need."}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        template_id = get_or_create_template_id(cursor)
        contact_id = get_or_create_contact_id(cursor, patient_id)

        cursor.execute(
            """INSERT INTO helprequest (patient_id, contact_id, template_id, status, failure_reason)
               VALUES (%s, %s, %s, 'pending', %s)""",
            (patient_id, contact_id, template_id, message[:100]),
        )
        conn.commit()
        return jsonify({"message": "Help request sent!"}), 201
    except Exception as e:
        conn.rollback()
        print("HELP REQUEST ERROR:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/help-requests/caregiver/<int:caregiver_id>", methods=["GET"])
def get_caregiver_help_requests(caregiver_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """SELECT h.request_id,
                      p.full_name AS patient_name,
                      DATE_FORMAT(h.requested_at, '%d/%m/%Y %H:%i') AS date_sent,
                      COALESCE(h.failure_reason, t.template_text) AS message,
                      h.status
               FROM helprequest h
               JOIN patient p ON h.patient_id = p.patient_id
               JOIN patientcaregiverlink pcl ON pcl.patient_id = h.patient_id
               LEFT JOIN helpmessagetemplate t ON h.template_id = t.template_id
               WHERE pcl.caregiver_id = %s AND pcl.status = 'active'
               ORDER BY h.requested_at DESC""",
            (caregiver_id,),
        )
        rows = cursor.fetchall()
        return jsonify(rows), 200
    finally:
        cursor.close()
        conn.close()


@app.route("/api/help-requests/<int:request_id>/acknowledge", methods=["PUT"])
def acknowledge_help_request(request_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE helprequest SET status = 'acknowledged' WHERE request_id = %s",
            (request_id,),
        )
        conn.commit()
        return jsonify({"message": "Help request acknowledged."}), 200
    finally:
        cursor.close()
        conn.close()


# ======================================
# DOSE LOGS (PATIENT <-> CAREGIVER)
# ======================================
@app.route("/api/dose-logs", methods=["POST"])
def create_dose_log():
    data = request.get_json() or {}
    schedule_id = data.get("schedule_id")
    med_id = data.get("med_id")
    dose_date = (data.get("dose_date") or "").strip()
    status = (data.get("status") or "").strip().lower()

    if status not in ("taken", "missed"):
        return jsonify({"error": "Status must be 'taken' or 'missed'."}), 400

    if not dose_date:
        return jsonify({"error": "Dose date is required."}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        resolved_schedule_id = schedule_id
        if not resolved_schedule_id and med_id:
            cursor.execute(
                "SELECT schedule_id FROM reminderschedule WHERE med_id = %s ORDER BY schedule_id ASC LIMIT 1",
                (med_id,),
            )
            sched_row = cursor.fetchone()
            if sched_row:
                resolved_schedule_id = sched_row["schedule_id"]

        if not resolved_schedule_id:
            return jsonify({"error": "Valid schedule_id or med_id is required."}), 400

        cursor.execute(
            """INSERT INTO doselog (schedule_id, dose_date, status)
               VALUES (%s, %s, %s)""",
            (resolved_schedule_id, dose_date, status),
        )
        conn.commit()
        return jsonify({"message": f"Dose marked as {status}."}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/dose-logs/caregiver/<int:caregiver_id>", methods=["GET"])
def get_caregiver_dose_logs(caregiver_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """SELECT dl.dose_id,
                      p.full_name AS patient_name,
                      m.medication_name,
                      m.strength,
                      DATE_FORMAT(dl.dose_date, '%Y-%m-%d') AS dose_date,
                      r.reminder_time,
                      dl.status,
                      DATE_FORMAT(dl.logged_at, '%d/%m/%Y %H:%i') AS logged_at
               FROM doselog dl
               JOIN reminderschedule r ON dl.schedule_id = r.schedule_id
               JOIN medication m ON r.med_id = m.med_id
               JOIN patient p ON m.patient_id = p.patient_id
               JOIN patientcaregiverlink pcl ON pcl.patient_id = p.patient_id
               WHERE pcl.caregiver_id = %s AND pcl.status = 'active'
               ORDER BY dl.dose_date DESC, dl.dose_id DESC""",
            (caregiver_id,),
        )
        rows = cursor.fetchall()
        return jsonify(rows), 200
    finally:
        cursor.close()
        conn.close()


@app.route("/api/caregiver/<int:caregiver_id>/missed-doses", methods=["GET"])
def get_caregiver_missed_doses(caregiver_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    cutoff_time = (datetime.now() - timedelta(minutes=30)).strftime("%H:%M")

    try:
        cursor.execute(
            """SELECT p.patient_id,
                      p.full_name AS patient_name,
                      m.med_id,
                      m.medication_name,
                      m.strength,
                      r.schedule_id,
                      r.reminder_time
               FROM patientcaregiverlink pcl
               JOIN patient p ON pcl.patient_id = p.patient_id
               JOIN medication m ON m.patient_id = p.patient_id AND m.is_active = 1
               JOIN reminderschedule r ON r.med_id = m.med_id AND r.is_active = 1
               WHERE pcl.caregiver_id = %s
                 AND pcl.status = 'active'
                 AND pcl.can_view_dose_status = 1""",
            (caregiver_id,),
        )
        schedules = cursor.fetchall()

        cursor.execute(
            """SELECT dl.schedule_id, dl.status
               FROM doselog dl
               JOIN reminderschedule r ON dl.schedule_id = r.schedule_id
               JOIN medication m ON r.med_id = m.med_id
               JOIN patientcaregiverlink pcl ON pcl.patient_id = m.patient_id
               WHERE pcl.caregiver_id = %s
                 AND pcl.status = 'active'
                 AND dl.dose_date = %s""",
            (caregiver_id, today_str),
        )
        logs = cursor.fetchall()

        taken_counts = {}
        missed_schedules = set()
        for log in logs:
            sid = log["schedule_id"]
            status = (log["status"] or "").lower()
            if status == "taken":
                taken_counts[sid] = taken_counts.get(sid, 0) + 1
            elif status == "missed":
                missed_schedules.add(sid)

        alerts = []
        for s in schedules:
            sid = s["schedule_id"]
            times = [t.strip()[:5] for t in (s["reminder_time"] or "").split(",") if t.strip()]

            if sid in missed_schedules:
                alerts.append({
                    "patient_name": s["patient_name"],
                    "medication_name": s["medication_name"],
                    "strength": s["strength"] or "",
                    "time": s["reminder_time"] or "-",
                    "reason": "Marked as missed"
                })
                continue

            overdue_times = [t for t in times if t <= cutoff_time]
            if len(overdue_times) > taken_counts.get(sid, 0):
                alerts.append({
                    "patient_name": s["patient_name"],
                    "medication_name": s["medication_name"],
                    "strength": s["strength"] or "",
                    "time": overdue_times[-1],
                    "reason": "Overdue (not logged)"
                })

        return jsonify(alerts), 200
    finally:
        cursor.close()
        conn.close()


# ======================================
# PATIENT SIDE EFFECTS
# ======================================
@app.route("/api/side-effects/<int:patient_id>", methods=["GET"])
def get_side_effects(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """SELECT s.side_effect_id,
                      DATE_FORMAT(s.effect_datetime, '%Y-%m-%d') AS record_date,
                      m.medication_name,
                      s.effect,
                      s.severity,
                      s.notes
               FROM sideeffectrecord s
               JOIN medication m ON s.med_id = m.med_id
               WHERE s.patient_id = %s
               ORDER BY s.effect_datetime DESC, s.side_effect_id DESC""",
            (patient_id,),
        )
        rows = cursor.fetchall()

        severity_labels = {1: "Mild", 2: "Moderate", 3: "Severe"}
        results = []
        for row in rows:
            raw_notes = row["notes"] or ""
            duration = "-"
            if raw_notes.startswith("Duration: "):
                duration = raw_notes.split(" | ", 1)[0].replace("Duration: ", "").strip() or "-"

            results.append({
                "side_effect_id": row["side_effect_id"],
                "record_date": row["record_date"],
                "medication_name": row["medication_name"],
                "effect": row["effect"],
                "severity": severity_labels.get(row["severity"], str(row["severity"] or "-")),
                "duration": duration,
                "notes": raw_notes,
            })

        return jsonify(results), 200
    finally:
        cursor.close()
        conn.close()


@app.route("/api/side-effects", methods=["POST"])
def add_side_effect():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    med_id = data.get("med_id")
    record_date = (data.get("record_date") or "").strip()
    effect = (data.get("effect") or "").strip()
    severity_str = (data.get("severity") or "").strip().lower()
    duration = (data.get("duration") or "").strip()
    description = (data.get("description") or "").strip()
    action = (data.get("action") or "").strip()

    if not patient_id or not med_id or not record_date or not effect:
        return jsonify({"error": "Please fill in date, medication, and side effect."}), 400

    severity_map = {"mild": 1, "moderate": 2, "severe": 3}
    severity_val = severity_map.get(severity_str)

    effect_datetime = f"{record_date} 00:00:00"
    combined_notes = (
        f"Duration: {duration or '-'} | "
        f"Description: {description or '-'} | "
        f"Action: {action or '-'}"
    )

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO sideeffectrecord (patient_id, med_id, effect_datetime, effect, severity, notes)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (patient_id, med_id, effect_datetime, effect[:100], severity_val, combined_notes),
        )
        conn.commit()
        return jsonify({"message": "Side effect saved successfully!"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ======================================
# DOCTOR PORTAL: OVERVIEW, PATIENT SUMMARIES & CONSULTATIONS
# ======================================
def ensure_consultation_table(cursor):
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS consultation_summary (
               consultation_id INT AUTO_INCREMENT PRIMARY KEY,
               doctor_id INT NOT NULL,
               patient_id INT NOT NULL,
               consultation_date DATE NOT NULL,
               diagnosis VARCHAR(255),
               treatment_plan TEXT,
               notes TEXT,
               follow_up_date DATE,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )"""
    )


@app.route("/api/doctor/overview", methods=["GET"])
def get_doctor_overview():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        ensure_consultation_table(cursor)

        cursor.execute(
            """SELECT p.patient_id,
                      p.full_name,
                      p.email,
                      p.phone,
                      p.status,
                      (SELECT COUNT(*) FROM medication m
                       WHERE m.patient_id = p.patient_id AND m.is_active = 1) AS active_meds,
                      (SELECT COUNT(*) FROM seizurerecord s
                       WHERE s.patient_id = p.patient_id) AS seizure_count
               FROM patient p
               ORDER BY p.patient_id DESC"""
        )
        patients = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM seizurerecord")
        total_seizures = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM consultation_summary")
        total_consultations = cursor.fetchone()["total"]

        return jsonify({
            "stats": {
                "total_patients": len(patients),
                "total_seizures": total_seizures,
                "total_consultations": total_consultations,
            },
            "patients": patients,
        }), 200
    finally:
        cursor.close()
        conn.close()


@app.route("/api/doctor/patient-summary/<int:patient_id>", methods=["GET"])
def get_patient_clinical_summary(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT patient_id, full_name, email, phone, status FROM patient WHERE patient_id = %s",
            (patient_id,),
        )
        patient = cursor.fetchone()
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        cursor.execute(
            """SELECT m.medication_name,
                      m.strength,
                      m.dose_amount AS frequency,
                      r.reminder_time,
                      m.instructions
               FROM medication m
               LEFT JOIN reminderschedule r ON m.med_id = r.med_id
               WHERE m.patient_id = %s AND m.is_active = 1
               ORDER BY m.med_id DESC""",
            (patient_id,),
        )
        medications = cursor.fetchall()

        cursor.execute(
            """SELECT DATE_FORMAT(seizure_datetime, '%Y-%m-%d') AS record_date,
                      seizure_type,
                      duration_secs,
                      notes
               FROM seizurerecord
               WHERE patient_id = %s
               ORDER BY seizure_datetime DESC""",
            (patient_id,),
        )
        seizures = cursor.fetchall()

        cursor.execute(
            """SELECT DATE_FORMAT(symptom_datetime, '%Y-%m-%d') AS record_date,
                      symptom,
                      notes
               FROM symptomrecord
               WHERE patient_id = %s
               ORDER BY symptom_datetime DESC""",
            (patient_id,),
        )
        symptoms = cursor.fetchall()

        cursor.execute(
            """SELECT DATE_FORMAT(s.effect_datetime, '%Y-%m-%d') AS record_date,
                      m.medication_name,
                      s.effect,
                      s.severity,
                      s.notes
               FROM sideeffectrecord s
               JOIN medication m ON s.med_id = m.med_id
               WHERE s.patient_id = %s
               ORDER BY s.effect_datetime DESC""",
            (patient_id,),
        )
        raw_effects = cursor.fetchall()
        severity_labels = {1: "Mild", 2: "Moderate", 3: "Severe"}
        side_effects = [
            {
                "record_date": row["record_date"],
                "medication_name": row["medication_name"],
                "effect": row["effect"],
                "severity": severity_labels.get(row["severity"], str(row["severity"] or "-")),
                "notes": row["notes"] or "-",
            }
            for row in raw_effects
        ]

        cursor.execute(
            """SELECT DATE_FORMAT(dl.dose_date, '%Y-%m-%d') AS dose_date,
                      m.medication_name,
                      r.reminder_time,
                      dl.status
               FROM doselog dl
               JOIN reminderschedule r ON dl.schedule_id = r.schedule_id
               JOIN medication m ON r.med_id = m.med_id
               WHERE m.patient_id = %s
               ORDER BY dl.dose_date DESC, dl.dose_id DESC
               LIMIT 20""",
            (patient_id,),
        )
        dose_logs = cursor.fetchall()

        total_doses = len(dose_logs)
        taken_doses = sum(1 for d in dose_logs if (d["status"] or "").lower() == "taken")
        adherence_rate = round((taken_doses / total_doses) * 100) if total_doses > 0 else None

        return jsonify({
            "patient": patient,
            "stats": {
                "active_medications": len(medications),
                "total_seizures": len(seizures),
                "total_side_effects": len(side_effects),
                "adherence_rate": adherence_rate,
            },
            "medications": medications,
            "seizures": seizures,
            "symptoms": symptoms,
            "side_effects": side_effects,
            "dose_logs": dose_logs,
        }), 200
    finally:
        cursor.close()
        conn.close()


@app.route("/api/doctor/consultations", methods=["GET"])
def get_doctor_consultations():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        ensure_consultation_table(cursor)
        cursor.execute(
            """SELECT c.consultation_id,
                      c.patient_id,
                      p.full_name AS patient_name,
                      COALESCE(d.full_name, 'Doctor') AS doctor_name,
                      DATE_FORMAT(c.consultation_date, '%Y-%m-%d') AS consultation_date,
                      c.diagnosis,
                      c.treatment_plan,
                      c.notes,
                      DATE_FORMAT(c.follow_up_date, '%Y-%m-%d') AS follow_up_date
               FROM consultation_summary c
               JOIN patient p ON c.patient_id = p.patient_id
               LEFT JOIN doctor d ON c.doctor_id = d.doctor_id
               ORDER BY c.consultation_date DESC, c.consultation_id DESC"""
        )
        rows = cursor.fetchall()
        return jsonify(rows), 200
    finally:
        cursor.close()
        conn.close()


@app.route("/api/doctor/consultations", methods=["POST"])
def add_doctor_consultation():
    data = request.get_json() or {}
    doctor_id = data.get("doctor_id")
    patient_id = data.get("patient_id")
    consultation_date = (data.get("consultation_date") or "").strip()
    diagnosis = (data.get("diagnosis") or "").strip()
    treatment_plan = (data.get("treatment_plan") or "").strip()
    notes = (data.get("notes") or "").strip()
    follow_up_date = (data.get("follow_up_date") or "").strip() or None

    if not doctor_id or not patient_id or not consultation_date or not diagnosis:
        return jsonify({"error": "Please select a patient, date, and clinical assessment."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        ensure_consultation_table(cursor)
        cursor.execute(
            """INSERT INTO consultation_summary
                   (doctor_id, patient_id, consultation_date, diagnosis, treatment_plan, notes, follow_up_date)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (doctor_id, patient_id, consultation_date, diagnosis[:255], treatment_plan or None, notes or None, follow_up_date),
        )
        conn.commit()
        return jsonify({"message": "Consultation summary saved successfully!"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ======================================
# PATIENT PORTAL: OWN PRE-VISIT SUMMARY & DOCTOR CONSULTATION NOTES
# ======================================
@app.route("/api/patient/<int:patient_id>/summary", methods=["GET"])
def get_own_patient_summary(patient_id):
    return get_patient_clinical_summary(patient_id)


@app.route("/api/patient/<int:patient_id>/consultations", methods=["GET"])
def get_patient_consultations(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        ensure_consultation_table(cursor)
        cursor.execute(
            """SELECT c.consultation_id,
                      DATE_FORMAT(c.consultation_date, '%Y-%m-%d') AS consultation_date,
                      c.diagnosis,
                      c.treatment_plan,
                      c.notes,
                      DATE_FORMAT(c.follow_up_date, '%Y-%m-%d') AS follow_up_date,
                      COALESCE(d.full_name, 'Doctor') AS doctor_name,
                      COALESCE(d.facility, '-') AS facility
               FROM consultation_summary c
               LEFT JOIN doctor d ON c.doctor_id = d.doctor_id
               WHERE c.patient_id = %s
               ORDER BY c.consultation_date DESC, c.consultation_id DESC""",
            (patient_id,),
        )
        rows = cursor.fetchall()
        return jsonify(rows), 200
    finally:
        cursor.close()
        conn.close()


FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@app.route("/")
def serve_home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def serve_frontend(filename):
    if filename.lower().startswith("backend"):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(FRONTEND_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True, port=5000)