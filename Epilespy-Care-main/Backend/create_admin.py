# create_admin.py - creates the first administrator account
import bcrypt
from db import get_connection, get_db_connection
# ask for the details of the new administrator
full_name = input("Full name: ")
email = input("Email: ")
password = input("Password: ")
# scramble the password, so we never store the real one
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
# connect to the database
conn = get_connection()
cursor = conn.cursor()
# save the new administrator in the Administrator table
sql = "INSERT INTO Administrator (full_name, email, password_hash) VALUES (%s, %s, %s)"
cursor.execute(sql, (full_name, email, hashed))

# make the change permanent
conn.commit()

# close the connection
cursor.close()
conn.close()

print("Administrator created.")