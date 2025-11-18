from auth import login, register, forgot_password
from reader_management import reader_menu
from book_manager import book_menu
from borrow_management import borrow_menu
from return_management import return_menu
from librarian_management import librarian_menu
from report import report_menu

# ==============================
#  MENU SAU ĐĂNG NHẬP
# ==============================

def system_menu(role):
    while True:
        print("\n=====SYSTEM MENU =====")
        print("1. Reader Management")
        print("2. Book Management")
        print("3. Borrow Management")
        print("4. Return Management")
        if role == "admin":
            print("5. Librarian Management")

        print("6. Revenue Report")
        print("0. Logout")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            reader_menu()
        elif choice == "2":
            book_menu()
        elif choice == "3":
            borrow_menu()
        elif choice == "4":
            return_menu()
        elif choice == "5" and role == "admin":
            librarian_menu()
        elif choice == "6":
            report_menu()
        elif choice == "0":
            print("\n Logout successful!")
            break
        else:
            print("\n Invalid option!")


# ==============================
#  MENU CHÍNH
# ==============================

def main():
    while True:
        print("\n===== LIBRARY MANAGEMENT SYSTEM =====")
        print("1. Login")
        print("2. Register")
        print("3. Forgot password")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        # --------------------
        # 1. LOGIN
        # --------------------
        if choice == "1":
            user = login()
            if user:  
                print(f"\n Hello, {user['username']} ({user['role']})")
                system_menu(user["role"])

        # --------------------
        # 2. ĐĂNG KÝ
        # --------------------
        elif choice == "2":
            register()

        # --------------------
        # 3. QUÊN MẬT KHẨU
        # --------------------
        elif choice == "3":
            forgot_password()

        # --------------------
        # 0. THOÁT
        # --------------------
        elif choice == "0":
            print("\n Goodbye!")
            break

        else:
            print("\n Invalid option!")

if __name__ == "__main__":
    main()
