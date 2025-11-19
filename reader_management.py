import datetime
from db import get_db


# ==========================
# COMMON VALIDATION
# ==========================

def retry_or_exit():
    print("\n1. Enter again")
    print("2. Exit")
    return input("Choose: ").strip() == "1"


def validate_email(e):
    return "@" in e and "." in e and not e.startswith("@") and not e.endswith("@")


def validate_phone(p):
    return p.isdigit() and len(p) == 10


def validate_date_input(d):
    try:
        dob = datetime.datetime.strptime(d, "%Y-%m-%d").date()
        if dob >= datetime.date.today():
            return False
        if dob.year < 1900:
            return False
        return True
    except:
        return False


# ==========================
# ADD READER
# ==========================

def add_reader():
    print("\n===== ADD READER =====")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Reader ID
    while True:
        rid = input("Enter reader ID (e.g., DG001): ").strip()
        if rid == "":
            print("\n This field cannot be empty.")
            if not retry_or_exit(): return
            continue

        if not (len(rid) == 5 and rid.startswith("DG") and rid[2:].isdigit()):
            print("\n Reader ID must follow DGxxx.")
            if not retry_or_exit(): return
            continue

        cursor.execute("SELECT reader_id FROM readers WHERE reader_id=%s", (rid,))
        if cursor.fetchone():
            print("\n Reader ID already exists.")
            if not retry_or_exit(): return
            continue
        break

    # Full name
    while True:
        name = input("Enter full name: ").strip()
        if name == "":
            print("\n Name cannot be empty.")
            if not retry_or_exit(): return
            continue
        break

    # Date of birth
    while True:
        dob_input = input("Enter date of birth (YYYY-MM-DD): ").strip()

        if not validate_date_input(dob_input):
            print("\n Invalid date format or logic (YYYY-MM-DD, year >= 1900, < today).")
            if not retry_or_exit(): return
            continue

        dob = datetime.datetime.strptime(dob_input, "%Y-%m-%d").date()
        break

    # Phone
    while True:
        phone = input("Enter phone number (10 digits): ").strip()

        if not validate_phone(phone):
            print("\n Invalid phone number (must be 10 digits).")
            if not retry_or_exit(): return
            continue

        cursor.execute("SELECT phone FROM readers WHERE phone=%s", (phone,))
        if cursor.fetchone():
            print("\n Phone number already exists.")
            if not retry_or_exit(): return
            continue

        break

    # Email
    while True:
        email = input("Enter email: ").strip()

        if not validate_email(email):
            print("\n Invalid email.")
            if not retry_or_exit(): return
            continue

        cursor.execute("SELECT email FROM readers WHERE email=%s", (email,))
        if cursor.fetchone():
            print("\n Email already exists.")
            if not retry_or_exit(): return
            continue

        break

    # Address
    while True:
        address = input("Enter address: ").strip()
        if address == "":
            print("\n Address cannot be empty.")
            if not retry_or_exit(): return
            continue
        break

    # INSERT into DB (convert date → string)
    cursor.execute("""
        INSERT INTO readers (reader_id, name, dob, phone, email, address)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (rid, name, dob.strftime("%Y-%m-%d"), phone, email, address))

    conn.commit()
    cursor.close()
    conn.close()

    print("\n Reader added successfully!")


# ==========================
# LIST READERS
# ==========================

def list_readers():
    print("\n===== LIST OF READERS =====")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM readers ORDER BY reader_id")
    rows = cursor.fetchall()

    if not rows:
        print("No readers found.")
        return

    for r in rows:
        print(f"\nID: {r['reader_id']}")
        print("Name:", r["name"])
        print("Date of Birth:", r["dob"])
        print("Phone:", r["phone"])
        print("Email:", r["email"])
        print("Address:", r["address"])

    cursor.close()
    conn.close()


# ==========================
# VIEW DETAIL
# ==========================

def view_reader():
    print("\n===== VIEW READER =====")
    rid = input("Enter reader ID: ").strip()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM readers WHERE reader_id=%s", (rid,))
    r = cursor.fetchone()

    if not r:
        print("\n Reader does not exist.")
        return

    print("\nID:", r["reader_id"])
    print("Name:", r["name"])
    print("Date of Birth:", r["dob"])
    print("Phone:", r["phone"])
    print("Email:", r["email"])
    print("Address:", r["address"])

    cursor.close()
    conn.close()


# ==========================
# EDIT READER
# ==========================

def edit_reader():
    print("\n===== EDIT READER =====")
    rid = input("Enter reader ID: ").strip()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM readers WHERE reader_id=%s", (rid,))
    r = cursor.fetchone()

    if not r:
        print("\n Reader does not exist.")
        return

    print("\nPress Enter to skip any field.")

    # Name
    name = input("New name: ").strip()
    if name:
        r["name"] = name

    # DOB
    dob_input = input("New DOB (YYYY-MM-DD): ").strip()
    if dob_input:
        if validate_date_input(dob_input):
            dob = datetime.datetime.strptime(dob_input, "%Y-%m-%d").date()
            r["dob"] = dob.strftime("%Y-%m-%d")
        else:
            print("Invalid DOB → kept old value.")

    # Phone
    phone = input("New phone: ").strip()
    if phone:
        if validate_phone(phone):
            cursor.execute("SELECT phone FROM readers WHERE phone=%s AND reader_id!=%s", (phone, rid))
            if cursor.fetchone():
                print("Phone already exists → kept old value.")
            else:
                r["phone"] = phone
        else:
            print("Invalid phone.")

    # Email
    email = input("New email: ").strip()
    if email:
        if validate_email(email):
            cursor.execute("SELECT email FROM readers WHERE email=%s AND reader_id!=%s", (email, rid))
            if cursor.fetchone():
                print("Email already exists → kept old value.")
            else:
                r["email"] = email
        else:
            print("Invalid email.")

    # Address
    addr = input("New address: ").strip()
    if addr:
        r["address"] = addr

    # UPDATE DB
    cursor.execute("""
        UPDATE readers
        SET name=%s, dob=%s, phone=%s, email=%s, address=%s
        WHERE reader_id=%s
    """, (r["name"], r["dob"], r["phone"], r["email"], r["address"], rid))

    conn.commit()
    cursor.close()
    conn.close()

    print("\n Reader updated successfully!")


# ==========================
# DELETE READER
# ==========================

def delete_reader():
    print("\n===== DELETE READER =====")
    rid = input("Enter reader ID: ").strip()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM readers WHERE reader_id=%s", (rid,))
    r = cursor.fetchone()

    if not r:
        print("\n Reader does not exist.")
        return

    print(f"\nDelete reader: {r['name']} ?")
    print("1. Yes")
    print("2. Cancel")

    if input("Choose: ").strip() != "1":
        print("\n Cancelled.")
        return

    cursor.execute("DELETE FROM readers WHERE reader_id=%s", (rid,))
    conn.commit()

    cursor.close()
    conn.close()

    print("\n Reader deleted successfully!")


# ==========================
# MENU
# ==========================

def reader_menu():
    while True:
        print("\n===== READER MANAGEMENT =====")
        print("1. Add reader")
        print("2. List readers")
        print("3. View details")
        print("4. Edit information")
        print("5. Delete reader")
        print("6. Exit")

        choice = input("Choose: ").strip()

        if choice == "1": add_reader()
        elif choice == "2": list_readers()
        elif choice == "3": view_reader()
        elif choice == "4": edit_reader()
        elif choice == "5": delete_reader()
        elif choice == "6":
            break
        else:
            print("\n Invalid choice!")
