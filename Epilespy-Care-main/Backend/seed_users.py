import bcrypt
from db import get_connection
def hash_pw(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()
conn = get_connection()
cursor = conn.cursor()

pw = hash_pw("Password123")

# 1. Demo Patient
cursor.execute(
    """INSERT IGNORE INTO patient (full_name, phone, email, password_hash, status)
       VALUES (%s, %s, %s, %s, 'active')""",
    ("Jane Wanjiku", "0712345678", "patient@epilepsycare.com", pw),
)

# 2. Demo Approved Doctor (can log in immediately)
cursor.execute(
    """INSERT IGNORE INTO doctor (full_name, EMAIL, password_hash, registration_no, facility, approval_status)
       VALUES (%s, %s, %s, %s, %s, 'approved')""",
    ("Dr. David Kamau", "doctor@epilepsycare.com", pw, "KMPDC-1024", "Kenyatta National Hospital"),
)

# 3. Demo Pending Doctor (blocked until an Admin approves them)
cursor.execute(
    """INSERT IGNORE INTO doctor (full_name, EMAIL, password_hash, registration_no, facility, approval_status)
       VALUES (%s, %s, %s, %s, %s, 'pending')""",
    ("Dr. Grace Ochieng", "pending.doctor@epilepsycare.com", pw, "KMPDC-2048", "Nairobi Hospital"),
)

# 4. Demo Caregiver
cursor.execute(
    """INSERT IGNORE INTO caregiver (full_name, phone, email, password_hash, status)
       VALUES (%s, %s, %s, %s, 'active')""",
    ("Peter Mwangi", "0722987654", "caregiver@epilepsycare.com", pw),
)

conn.commit()
cursor.close()
conn.close()
print("Demo accounts ready! Password for all accounts: Password123")