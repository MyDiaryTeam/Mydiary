from passlib.hash import bcrypt

try:
    hashed = bcrypt.hash("password123")
    print("Hashing succeeded:", hashed)
except Exception as e:
    print("Hashing failed:", e)
