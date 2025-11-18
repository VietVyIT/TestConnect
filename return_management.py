import datetime
from db import get_db


def parse_ddmmyyyy(s):
    try:
        return datetime.datetime.strptime(s, "%d-%m-%Y").date()
    except:
        return None


def return_book():
    print("\n===== Return Book =====")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # ===== Enter borrow ID =====
    borrow_id = input("Enter borrow ID: ").strip()

    cursor.execute("SELECT * FROM borrows WHERE borrow_id=%s", (borrow_id,))
    br = cursor.fetchone()

    if not br:
        print(" Borrow record does not exist.")
        return

    if br["returned"]:
        print(" This borrow record has already been returned.")
        return

    # ===== Enter return date =====
    ret_str = input("Enter return date (dd-mm-yyyy): ").strip()
    ret_date = parse_ddmmyyyy(ret_str)

    if not ret_date:
        print("Invalid return date.")
        return

    borrow_date = br["borrow_date"]
    borrow_date = datetime.datetime.strptime(str(borrow_date), "%Y-%m-%d").date()

    if ret_date < borrow_date:
        print(" Return date cannot be earlier than borrow date.")
        return

    # ===== Update return status =====
    cursor.execute("""
        UPDATE borrows
        SET returned = 1,
            return_date = %s
        WHERE borrow_id=%s
    """, (ret_date.strftime("%Y-%m-%d"), borrow_id))

    # ===== Increase book quantity =====
    book_id = br["book_id"]

    cursor.execute("""
        UPDATE books
        SET quantity = quantity + 1
        WHERE book_id=%s
    """, (book_id,))

    conn.commit()

    # ===== Kiểm tra trễ hạn =====
    due_date = br["due_date"]
    due_date = datetime.datetime.strptime(str(due_date), "%Y-%m-%d").date()

    if ret_date > due_date:
        print("\n Late return!")

    print("\n Return successful.")
    print("Book", book_id, "quantity has been increased.")

def return_menu():
    while True:
        print("\n===== RETURN MANAGEMENT =====")
        print("1. Return book")
        print("0. Exit")

        c = input("Choose: ").strip()
        if c == "1":
            return_book()
        elif c == "0":
            break
        else:
            print(" Invalid choice.")
