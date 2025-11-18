import datetime
from db import get_db

# ==============================
# VALIDATIONS
# ==============================

def retry_or_exit():
    print("\n1. Enter again")
    print("2. Exit")
    return input("Choose: ").strip() == "1"

def validate_book_id(book_id):
    return len(book_id) == 4 and book_id.startswith("S") and book_id[1:].isdigit()

def validate_year(year: str):
    if not year.isdigit():
        return False
    y = int(year)
    return 1900 <= y <= 2025

def validate_quantity(qty: str):
    return qty.isdigit() and int(qty) >= 1


# ==============================
# THÊM SÁCH
# ==============================

def add_book():
    print("\n===== ADD BOOK =====")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # book_id
    while True:
        book_id = input("Enter book ID (e.g., S001): ").strip()
        if not validate_book_id(book_id):
            print(" Invalid book ID (format Sxxx).")
            if not retry_or_exit(): return
            continue

        cursor.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
        if cursor.fetchone():
            print("Book ID already exists.")
            if not retry_or_exit(): return
            continue
        break

    # title
    while True:
        title = input("Title: ").strip()
        if title == "":
            print(" This field cannot be empty.")
            if not retry_or_exit(): return
            continue
        break

    # author
    while True:
        author = input("Author: ").strip()
        if author == "":
            print(" This field cannot be empty.")
            if not retry_or_exit(): return
            continue
        break

    # category
    while True:
        category = input("Category: ").strip()
        if category == "":
            print(" This field cannot be empty.")
            if not retry_or_exit(): return
            continue
        break

    # year
    while True:
        year = input("Publish year: ").strip()
        if not validate_year(year):
            print(" Invalid publish year (1900 - 2025).")
            if not retry_or_exit(): return
            continue
        year = int(year)
        break

    # publisher
    while True:
        publisher = input("Publisher: ").strip()
        if publisher == "":
            print(" This field cannot be empty.")
            if not retry_or_exit(): return
            continue
        break

    # quantity
    while True:
        quantity = input("Quantity: ").strip()
        if not validate_quantity(quantity):
            print("Quantity must be ≥ 1.")
            if not retry_or_exit(): return
            continue
        quantity = int(quantity)
        break

    # Insert
    cursor.execute("""
        INSERT INTO books (book_id, title, author, category, publish_year, publisher, quantity)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (book_id, title, author, category, year, publisher, quantity))

    conn.commit()
    cursor.close()
    conn.close()

    print("\n Book added successfully!")


# ==============================
# DANH SÁCH
# ==============================

def list_books():
    print("\n===== BOOK LIST =====")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM books ORDER BY book_id")
    rows = cursor.fetchall()

    if not rows:
        print(" No books in the system.")
        return

    for b in rows:
        print(f"\nBook ID: {b['book_id']}")
        print("Title:", b["title"])
        print("Author:", b["author"])
        print("Category:", b["category"])
        print("Publish year:", b["publish_year"])
        print("Publisher:", b["publisher"])
        print("Quantity:", b["quantity"])

    cursor.close()
    conn.close()


# ==============================
# XEM CHI TIẾT
# ==============================

def view_book_detail():
    print("\n===== BOOK DETAIL =====")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    book_id = input("Enter book ID: ").strip()

    cursor.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
    b = cursor.fetchone()

    if not b:
        print(" Book not found.")
        return

    print(f"\nBook ID: {b['book_id']}")
    print("Title:", b["title"])
    print("Author:", b["author"])
    print("Category:", b["category"])
    print("Publish year:", b["publish_year"])
    print("Publisher:", b["publisher"])
    print("Quantity:", b["quantity"])
    cursor.close()
    conn.close()


# ==============================
# SỬA THÔNG TIN SÁCH
# ==============================

def edit_book():
    print("\n===== EDIT BOOK INFO =====")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    book_id = input("Enter book ID to edit: ").strip()
    cursor.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
    b = cursor.fetchone()

    if not b:
        print(" Book not found.")
        return

    print("\nPress ENTER to skip editing a field.")

    new_title = input(f"Title ({b['title']}): ").strip() or b["title"]
    new_author = input(f"Author ({b['author']}): ").strip() or b["author"]
    new_category = input(f"Category ({b['category']}): ").strip() or b["category"]

    # validate year
    year_in = input(f"Publish year ({b['publish_year']}): ").strip()
    if year_in == "":
        new_year = b["publish_year"]
    else:
        if not validate_year(year_in):
            print(" Invalid year. Keeping original.")
            new_year = b["publish_year"]
        else:
            new_year = int(year_in)

    new_publisher = input(f"Publisher ({b['publisher']}): ").strip() or b["publisher"]

    qty_in = input(f"Quantity ({b['quantity']}): ").strip()
    if qty_in == "":
        new_qty = b["quantity"]
    else:
        if not validate_quantity(qty_in):
            print(" Invalid quantity. Keeping original.")
            new_qty = b["quantity"]
        else:
            new_qty = int(qty_in)

    cursor.execute("""
        UPDATE books
        SET title=%s, author=%s, category=%s, publish_year=%s, publisher=%s, quantity=%s
        WHERE book_id=%s
    """, (new_title, new_author, new_category, new_year, new_publisher, new_qty, book_id))

    conn.commit()
    cursor.close()
    conn.close()

    print("\n Update successful!")


# ==============================
# XÓA SÁCH
# ==============================

def delete_book():
    print("\n===== DELETE BOOK =====")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    book_id = input("Enter book ID to delete: ").strip()

    cursor.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
    if not cursor.fetchone():
        print(" Book not found.")
        return

    confirm = input("Are you sure you want to delete? (y/n): ").strip().lower()
    if confirm != "y":
        print(" Cancelled.")
        return

    cursor.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
    conn.commit()

    cursor.close()
    conn.close()

    print("\n Book deleted successfully!")


# ==============================
# TÌM KIẾM SÁCH
# ==============================

def search_books():
    print("\n===== SEARCH BOOKS =====")

    keyword = input("Enter keyword: ").strip().lower()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM books WHERE LOWER(title) LIKE %s", (f"%{keyword}%",))
    rows = cursor.fetchall()

    if not rows:
        print(" No books found.")
        return

    for b in rows:
        print(f"\nBook ID: {b['book_id']}")
        print("Title:", b["title"])
        print("Author:", b["author"])
        print("Category:", b["category"])
        print("Publish year:", b["publish_year"])
        print("Publisher:", b["publisher"])
        print("Quantity:", b["quantity"])

    cursor.close()
    conn.close()


# ==============================
# MENU
# ==============================

def book_menu():
    while True:
        print("\n===== BOOK MANAGEMENT =====")
        print("1. Add book")
        print("2. List books")
        print("3. View book detail")
        print("4. Edit book")
        print("5. Delete book")
        print("6. Search books")
        print("0. Exit")

        c = input("Choose an option: ").strip()

        if c == "1": add_book()
        elif c == "2": list_books()
        elif c == "3": view_book_detail()
        elif c == "4": edit_book()
        elif c == "5": delete_book()
        elif c == "6": search_books()
        elif c == "0":
            print(" Exit book menu.")
            break
        else:
            print(" Invalid option.")