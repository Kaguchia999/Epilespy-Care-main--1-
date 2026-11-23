import bcrypt
from getpass import getpass

from db import get_connection


def main() -> None:
    full_name = input("Full name: ").strip()
    email = input("Email: ").strip()
    password = getpass("Password: ")
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            sql = (
                "INSERT INTO Administrator (full_name, email, password_hash) "
                "VALUES (%s, %s, %s)"
            )
            cursor.execute(sql, (full_name, email, hashed))
            conn.commit()
        finally:
            cursor.close()
    finally:
        conn.close()

    print("Administrator created.")


if __name__ == "__main__":
    main()