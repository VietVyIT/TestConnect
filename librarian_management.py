import datetime
from db import get_db

# ==============================
#  COMMON VALIDATION
# ==============================

def retry_or_exit():
    print("\n1. Enter the information again")
    print("2. Exit")
    return input("Choose: ").strip() == "1"

def validate_date(d):
    try:
        date = datetime.datetime.strptime(d, "%Y-%m-%d").date()
        if date >= datetime.date.today():
            return False
        if date.year < 1900:
            return False
        return True
    except:
        return False

def validate_phone(phone):
    return phone.isdigit() and len(phone) == 10

def validate_email(email):
    return "@" in email and "." in email and not email.startswith("@") and not email.endswith("@")

def validate_staff_id(sid):
    return len(sid) == 5 and sid.startswith("LB") and sid[2:].isdigit()


# ==============================
#  THÊM NHÂN VIÊN
# ==============================

def add_librarian():
    print("\n===== ADD LIBRARIAN =====")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # librarian_id
    while True:
        sid = input("Enter librarian ID (e.g., LB001): ").strip()

        if sid == "":
            print("\n Librarian ID cannot be empty.")
            if not retry_or_exit(): return
            continue

        if not validate_staff_id(sid):
            print("\nInvalid ID format (LBxxx).")
            if not retry_or_exit(): return
            continue

        cursor.execute("SELECT librarian_id FROM librarian_management WHERE librarian_id=%s", (sid,))
        if cursor.fetchone():
            print("\n Librarian ID already exists.")
            if not retry_or_exit(): return
            continue
        break

    # name
    while True:
        name = input("Enter full name: ").strip()
        if name == "":
            print("\n Full name cannot be empty.")
            if not retry_or_exit(): return
            continue
        break

    # dob
    while True:
        dob = input("Enter date of birth (YYYY-MM-DD): ").strip()
        if not validate_date(dob):
            print("\n Invalid date of birth.")
            if not retry_or_exit(): return
            continue
        break

    # phone
    while True:
        phone = input("Enter phone number (10 digits): ").strip()
        if not validate_phone(phone):
            print("\n Invalid phone number.")
            if not retry_or_exit(): return
            continue

        cursor.execute("SELECT phone FROM librarian_management WHERE phone=%s", (phone,))
        if cursor.fetchone():
            print("\n Phone number already exists.")
            if not retry_or_exit(): return
            continue
        break

    # email
    while True:
        email = input("Enter email: ").strip()

        if not validate_email(email):
            print("\n Invalid email.")
            if not retry_or_exit(): return
            continue

        cursor.execute("SELECT email FROM librarian_management WHERE email=%s", (email,))
        if cursor.fetchone():
            print("\n Email already exists.")
            if not retry_or_exit(): return
            continue
        break

    # role
    while True:
        role = input("Enter role (Librarian): ").strip().lower()
        if role not in ["librarian"]:
            print("\n Invalid role.")
            if not retry_or_exit(): return
            continue
        break

    # address
    address = input("Enter address: ").strip()

    cursor.execute("""
        INSERT INTO librarian_management
        (librarian_id, name, dob, phone, email, role, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (sid, name, dob, phone, email, role.capitalize(), address))

    conn.commit()
    cursor.close()
    conn.close()

    print("\n✅ Librarian added successfully.")


# ==============================
#  LIST
# ==============================

def list_librarians():
    print("\n===== LIBRARIAN LIST =====")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM librarian_management ORDER BY librarian_id")
    rows = cursor.fetchall()

    if not rows:
        print(" No librarians found.")
        return

    for s in rows:
        print(f"\nID: {s['librarian_id']}")
        print("Full name:", s["name"])
        print("Date of birth:", s["dob"])
        print("Phone number:", s["phone"])
        print("Email:", s["email"])
        print("Role:", s["role"])
        print("Address:", s["address"])

    cursor.close()
    conn.close()


# ==============================
#  XEM CHI TIẾT
# ==============================

def view_librarian():
    print("\n===== VIEW LIBRARIAN DETAILS =====")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    sid = input("Enter librarian ID: ").strip()
    cursor.execute("SELECT * FROM librarian_management WHERE librarian_id=%s", (sid,))
    s = cursor.fetchone()

    if not s:
        print("❌ Not found.")
        return

    print("\nID:", s["librarian_id"])
    print("Full name:", s["name"])
    print("Date of birth:", s["dob"])
    print("Phone number:", s["phone"])
    print("Email:", s["email"])
    print("Role:", s["role"])
    print("Address:", s["address"])
    cursor.close()
    conn.close()


# ==============================
#  SỬA
# ==============================

def edit_librarian():
    print("\n===== EDIT LIBRARIAN INFORMATION =====")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    sid = input("Enter librarian ID: ").strip()
    cursor.execute("SELECT * FROM librarian_management WHERE librarian_id=%s", (sid,))
    s = cursor.fetchone()

    if not s:
        print(" Not found.")
        return

    print("\nPress Enter to skip.")

    name = input("New name: ").strip()
    if name:
        s["name"] = name

    dob = input("New date of birth (YYYY-MM-DD): ").strip()
    if dob:
        if validate_date(dob):
            s["dob"] = dob
        else:
            print(" Invalid date of birth.")

    phone = input("New phone number: ").strip()
    if phone:
        if validate_phone(phone):

            cursor.execute("SELECT phone FROM librarian_management WHERE phone=%s AND librarian_id!=%s", (phone, sid))
            if cursor.fetchone():
                print(" Phone number already exists.")
            else:
                s["phone"] = phone

    email = input("New email: ").strip()
    if email:
        if validate_email(email):

            cursor.execute("SELECT email FROM librarian_management WHERE email=%s AND librarian_id!=%s", (email, sid))
            if cursor.fetchone():
                print(" Email already exists.")
            else:
                s["email"] = email

    role = input("New role (Librarian): ").strip().lower()
    if role == "librarian":
        s["role"] = "Librarian"

    address = input("New address: ").strip()
    if address:
        s["address"] = address

    cursor.execute("""
        UPDATE librarian_management
        SET name=%s, dob=%s, phone=%s, email=%s, role=%s, address=%s
        WHERE librarian_id=%s
    """, (s["name"], s["dob"], s["phone"], s["email"], s["role"], s["address"], sid))

    conn.commit()
    cursor.close()
    conn.close()

    print("\n Update successful.")


# ==============================
#  XÓA
# ==============================

def delete_librarian():
    print("\n===== DELETE LIBRARIAN =====")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    sid = input("Enter librarian ID: ").strip()
    cursor.execute("SELECT * FROM librarian_management WHERE librarian_id=%s", (sid,))
    s = cursor.fetchone()

    if not s:
        print(" Not found.")
        return

    print("\nDelete librarian:", s["name"])
    print("1. Confirm")
    print("2. Cancel")

    if input("Choose: ").strip() != "1":
        print("Cancelled.")
        return

    cursor.execute("DELETE FROM librarian_management WHERE librarian_id=%s", (sid,))
    conn.commit()

    cursor.close()
    conn.close()

    print("\n Delete successful.")


# ==============================
#  MENU
# ==============================

def librarian_menu():
    while True:
        print("\n===== LIBRARIAN MANAGEMENT =====")
        print("1. Add librarian")
        print("2. List librarians")
        print("3. View details")
        print("4. Edit information")
        print("5. Delete")
        print("6. Exit")

        c = input("Choose: ").strip()

        if c == "1": add_librarian()
        elif c == "2": list_librarians()
        elif c == "3": view_librarian()
        elif c == "4": edit_librarian()
        elif c == "5": delete_librarian()
        elif c == "6": break
        else:
            print("Invalid choice.")