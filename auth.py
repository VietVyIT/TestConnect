import re
import sys
from db import get_db

# ==============================
#   VALIDATION
# ==============================

def retry_or_exit():
    print("\n1. Enter again")
    print("2. Exit")
    return input("Choose: ").strip() == "1"

def validate_password(pw):
    return (
        len(pw) >= 6
        and any(c.isdigit() for c in pw)
        and any(not c.isalnum() for c in pw)
    )

def validate_email(email):
    return "@" in email and "." in email and not email.startswith("@") and not email.endswith("@")

def validate_phone(phone):
    return phone.isdigit() and len(phone) == 10


# ==============================
#   ĐĂNG NHẬP
# ==============================

def login():
    print("\n===== SYSTEM LOGIN =====")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # chọn vai trò
    while True:
        role = input("Choose role (admin / librarian): ").strip().lower()
        if role in ["admin", "librarian"]:
            break
        print(" Invalid role!")
    
    # đăng nhập
    attempts = 0

    while True:
        username = input("\nUsername: ").strip()
        password = input("Password: ").strip()

        if username == "" or password == "":
            print("\n Cannot be empty!")
            if not retry_or_exit():
                sys.exit()
            continue

        cursor.execute("SELECT * FROM users WHERE username=%s AND role=%s", (username, role))
        user = cursor.fetchone()

        if not user:
            print("\n Incorrect username or role.")
            if not retry_or_exit():
                sys.exit()
            continue

        # kiểm tra khóa tài khoản
        if user["fail"] >= 3:
            print("\n ACCOUNT LOCKED DUE TO 3 FAILED ATTEMPTS.")
            sys.exit()

        # kiểm tra mật khẩu
        if password != user["password"]:
            attempts += 1
            print(f"\n Incorrect password. Attempt {attempts}/3")

            if attempts == 3:
                cursor.execute("UPDATE users SET fail = 3 WHERE id=%s", (user["id"],))
                conn.commit()
                print("\n You have entered the wrong password more than the allowed number of times (3 times)!")
                print("ACCOUNT LOCKED.")
                print("→ The program will automatically exit.")
                sys.exit()

            if not retry_or_exit():
                sys.exit()
            continue

        # successful login
        cursor.execute("UPDATE users SET fail = 0 WHERE id=%s", (user["id"],))
        conn.commit()

        print(f"\n🎉 Login successful! Welcome {user['username']}.")
        cursor.close()
        conn.close()
        return user


# ==============================
#   ĐĂNG KÝ TÀI KHOẢN
# ==============================

def register():
    print("\n===== REGISTER ACCOUNT =====")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # username
    while True:
        username = input("Username: ").strip()

        if username == "":
            print(" Cannot be empty.")
            if not retry_or_exit(): return
            continue

        cursor.execute("SELECT username FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            print(" Username already exists.")
            if not retry_or_exit(): return
            continue
        break

    # password
    while True:
        pw = input("Mật khẩu: ").strip()

        if not validate_password(pw):
            print("\n Password must be at least 6 characters long, contain a number and a special character.")
            if not retry_or_exit(): return
            continue

        pw2 = input("Confirm password: ").strip()
        if pw != pw2:
            print(" Passwords do not match.")
            if not retry_or_exit(): return
            continue
        break

    # email
    while True:
        email = input("Email: ").strip()

        if email == "":
            print(" Cannot be empty.")
            if not retry_or_exit(): return
            continue

        if not validate_email(email):
            print(" Invalid email.")
            if not retry_or_exit(): return
            continue

        break

    # phone
    while True:
        phone = input("Phone number (10 digits): ").strip()

        if phone == "":
            print(" Cannot be empty.")
            if not retry_or_exit(): return
            continue

        if not validate_phone(phone):
            print(" Invalid phone number.")
            if not retry_or_exit(): return
            continue
        break

    # thêm tài khoản mới (vai trò mặc định là thủ thư)
    cursor.execute("""
        INSERT INTO users(username, password, role, fail, email, phone)
        VALUES (%s, %s, 'thuthu', 0, %s, %s)
    """, (username, pw, email, phone))

    conn.commit()
    cursor.close()
    conn.close()

    print("\n Registration successful! You can log in now.")


# ==============================
#   QUÊN MẬT KHẨU
# ==============================

def forgot_password():
    print("\n===== FORGOT PASSWORD =====")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    phone = input("Enter phone number: ").strip()

    cursor.execute("""
        SELECT * FROM users 
        WHERE username=%s AND email=%s AND phone=%s
    """, (username, email, phone))

    user = cursor.fetchone()

    if not user:
        print("\n Information is incorrect.")
        return

    print("\n✔ Verification successful. You can set a new password.")

    while True:
        pw = input("New password: ").strip()
        if not validate_password(pw):
            print("Password must be at least 6 characters long, contain a number and a special character.")
            if not retry_or_exit(): return
            continue

        pw2 = input("Confirm password: ").strip()
        if pw != pw2:
            print("Passwords do not match.")
            if not retry_or_exit(): return
            continue
        break

    cursor.execute("UPDATE users SET password=%s, fail=0 WHERE id=%s", (pw, user["id"]))
    conn.commit()
    cursor.close()
    conn.close()

    print("\n Password changed successfully! Please log in again.")


# ==============================
#   MENU ĐẦU TIÊN
# ==============================

def auth_menu():
    while True:
        print("\n===== LIBRARY SYSTEM =====")
        print("1. Log in")
        print("2. Register")
        print("3. Forgot password")
        print("0. Exit")
        c = input("Choose: ").strip()

        if c == "1":
            return login()
        elif c == "2":
            register()
        elif c == "3":
            forgot_password()
        elif c == "0":
            print("Goodbye!")
            sys.exit()
        else:
            print(" Invalid choice.")