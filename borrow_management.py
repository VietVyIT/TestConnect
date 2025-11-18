import datetime
from db import get_db

# ===============================
#  CONSTANT
# ===============================

MIN_YEAR = 2000          # Năm nhỏ nhất cho phép
MAX_YEAR = 2025          # Không được vượt quá năm 2025
MAX_BORROW_DAYS = 31     # Mượn tối đa 31 ngày
MAX_EXTEND_DAYS = 4      # Gia hạn tối đa 4 ngày
MIN_DAYS_BEFORE_DUE = 3  # Phải gia hạn trước hạn trả ít nhất 3 ngày


# ===============================
#  Helper
# ===============================

def retry_or_exit():
    print("\n1. Enter the information again")
    print("2. Exit")
    return input("Choose: ").strip() == "1"


def parse_ddmmyyyy(s: str):
    """Convert string dd-mm-yyyy -> date. Return None if the format is incorrect."""
    try:
        return datetime.datetime.strptime(s, "%d-%m-%Y").date()
    except ValueError:
        return None


# ===============================
#  Tự động tạo mã PMxxx từ database
# ===============================

def generate_borrow_id():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT borrow_id FROM borrows")
    rows = cursor.fetchall()

    if not rows:
        return "PM001"

    nums = []
    for r in rows:
        try:
            nums.append(int(r[0][2:]))
        except:
            continue

    nxt = max(nums) + 1 if nums else 1
    return f"PM{nxt:03d}"


# ===============================
#  TẠO PHIẾU MƯỢN
# ===============================

def add_borrow():
    print("\n===== CREATE BORROW SLIP =====")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # ===== Reader ID =====
    while True:
        rid = input("Enter reader ID: ").strip()

        if rid == "":
            print(" Reader ID is required.")
            if not retry_or_exit():
                return
            continue

        cursor.execute("SELECT * FROM readers WHERE reader_id=%s", (rid,))
        if not cursor.fetchone():
            print(" Reader does not exist.")
            if not retry_or_exit():
                return
            continue
        break

    # ===== Book ID =====
    while True:
        bid = input("Enter book ID: ").strip()

        if bid == "":
            print(" Book ID is required.")
            if not retry_or_exit():
                return
            continue

        cursor.execute("SELECT * FROM books WHERE book_id=%s", (bid,))
        b = cursor.fetchone()

        if not b:
            print(" Book does not exist.")
            if not retry_or_exit():
                return
            continue

        if b["quantity"] <= 0:
            print(" Book is temporarily out of stock!")
            return

        break

    # ===== Borrow date & due date =====
    while True:
        bd_str = input("Enter borrow date (dd-mm-yyyy): ").strip()
        dd_str = input("Enter due date (dd-mm-yyyy): ").strip()

        bd = parse_ddmmyyyy(bd_str)
        dd = parse_ddmmyyyy(dd_str)

        if not bd or not dd:
            print(" Invalid date format (correct: dd-mm-yyyy).")
            if not retry_or_exit(): return
            continue

        # year less than 2000
        if bd.year < MIN_YEAR or dd.year < MIN_YEAR:
            print(f"Year must be ≥ {MIN_YEAR}.")
            if not retry_or_exit(): return
            continue

        # năm vượt quá 2025
        if bd.year > MAX_YEAR or dd.year > MAX_YEAR:
            print(f"Year must be ≤ {MAX_YEAR}.")
            if not retry_or_exit(): return
            continue

        # hạn trả > ngày mượn
        if dd <= bd:
            print(" Due date must be later than borrow date.")
            if not retry_or_exit(): return
            continue

        # thời gian mượn tối đa 31 ngày
        if (dd - bd).days > MAX_BORROW_DAYS:
            print(f" Borrow duration must be at most {MAX_BORROW_DAYS} days.")
            if not retry_or_exit(): return
            continue

        break

    # insert phiếu
    borrow_id = generate_borrow_id()

    cursor.execute("""
        INSERT INTO borrows (borrow_id, reader_id, book_id, borrow_date, due_date, returned)
        VALUES (%s, %s, %s, %s, %s, 0)
    """, (
        borrow_id,
        rid,
        bid,
        bd.strftime("%Y-%m-%d"),
        dd.strftime("%Y-%m-%d")
    ))

    cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE book_id=%s", (bid,))
    conn.commit()

    print("\nBorrow slip created successfully.")
    print(" Slip ID:", borrow_id)


# ===============================
#  GIA HẠN PHIẾU
# ===============================

def extend_borrow():
    print("\n===== EXTEND BORROW SLIP =====")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    borrow_id = input("Enter slip ID: ").strip()

    cursor.execute("SELECT * FROM borrows WHERE borrow_id=%s", (borrow_id,))
    br = cursor.fetchone()

    if not br:
        print(" Slip does not exist.")
        return

    if br["returned"]:
        print(" Slip has been returned → cannot extend.")
        return

    # extension request date
    today_str = input("Enter extension request date (dd-mm-yyyy): ").strip()
    today = parse_ddmmyyyy(today_str)

    if not today:
        print(" Invalid date.")
        return

    if today.year < MIN_YEAR or today.year > MAX_YEAR:
        print(f"Year must be between {MIN_YEAR} and {MAX_YEAR}.")
        return

    # hạn trả hiện tại
    due_date = datetime.datetime.strptime(str(br["due_date"]), "%Y-%m-%d").date()

    # phải gia hạn trước hạn trả ít nhất 3 ngày
    if (due_date - today).days < MIN_DAYS_BEFORE_DUE:
        print(f" Must extend at least {MIN_DAYS_BEFORE_DUE} days before due date.")
        return

    ext_str = input(f"Extend by how many days (max {MAX_EXTEND_DAYS})? ").strip()

    if not ext_str.isdigit():
        print(" Invalid number of days.")
        return

    ext = int(ext_str)
    if ext <= 0 or ext > MAX_EXTEND_DAYS:
        print(f" Only allowed to extend 1 – {MAX_EXTEND_DAYS} days.")
        return

    # tính hạn trả mới
    new_due = due_date + datetime.timedelta(days=ext)

    if new_due.year > MAX_YEAR:
        print(f" New due date must not exceed year {MAX_YEAR}.")
        return

    cursor.execute("UPDATE borrows SET due_date=%s WHERE borrow_id=%s",
                   (new_due.strftime("%Y-%m-%d"), borrow_id))
    conn.commit()

    print("\nExtension successful!")
    print("New due date:", new_due.strftime("%d-%m-%Y"))


# ===============================
#  BORROW SLIP LIST
# ===============================

def list_borrows():
    print("\n===== BORROW SLIP LIST =====")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM borrows ORDER BY borrow_id")
    rows = cursor.fetchall()

    if not rows:
        print(" No borrow slips found.")
        return

    for r in rows:
        print(f"\n Slip ID: {r['borrow_id']}")
        print("   Reader ID :", r["reader_id"])
        print("   Book ID   :", r["book_id"])
        print("   Borrow Date  :", r["borrow_date"])
        print("   Due Date    :", r["due_date"])
        print("   Status:", "Borrowing" if not r["returned"] else "Returned")

# ===============================
#  MENU
# ===============================

def borrow_menu():
    while True:
        print("\n===== BORROW MANAGEMENT =====")
        print("1. Create borrow slip")
        print("2. Borrow slip list")
        print("3. Extend borrow slip")
        print("0. Exit")
        c = input("Choose: ").strip()

        if c == "1":
            add_borrow()
        elif c == "2":
            list_borrows()
        elif c == "3":
            extend_borrow()
        elif c == "0":
            print("⬅ Exit borrow management.")
            break
        else:
            print("Invalid choice.")