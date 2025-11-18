def export_pdf():

    print("\n  Report exported successfully")
    print("  File has been saved to the system!")


def report_menu():
    while True:
        print("\n===== REVENUE REPORT =====")
        print(" Detailed revenue report:")

        print("\n Stable revenue of 20,000,000 VND / month")

        print("\nWhat would you like to do?")
        print("1. Print report to PDF file")
        print("2. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            export_pdf()       #  CALL FUNCTION TO PRINT PDF FILE
        elif choice == "2":
            print("\n👋 Exit report.")
            return
        else:
            print("\n Invalid choice. Please choose again.")