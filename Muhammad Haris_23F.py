# secure_password_policy.py
# Small demo that enforces a password policy and shows hashing - console program
import re
import bcrypt
import getpass

def valid_password(p):
    # Enforce: min 8 chars, at least one digit, one uppercase, one special
    return len(p) >= 8 and re.search(r"\d", p) and re.search(r"[A-Z]", p) and re.search(r"[!@#$%^&*()_+-=]", p)

print("Create account (demo)")
username = input("Username: ").strip()
while True:
    pwd = getpass.getpass("Password: ")
    if not valid_password(pwd):
        print("Password must be >=8 chars, include digit, uppercase and special char.")
        continue
    pwd2 = getpass.getpass("Confirm Password: ")
    if pwd != pwd2:
        print("Passwords do not match.")
        continue
    break

hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
print("Stored hash (demo):", hashed)
print("Account created for", username)
