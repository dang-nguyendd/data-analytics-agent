import sys
import getpass
import ctypes

from PySide6.QtWidgets import QApplication

from services.authentication import authenticate
from ui.main_window import MainWindow


def close_console():
    """Close the current Windows CMD/console window."""

    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # Get the current console window
    console_window = kernel32.GetConsoleWindow()

    if console_window:
        user32.PostMessageW(
            console_window,
            0x0010,  # WM_CLOSE
            0,
            0
        )


def login():

    print()
    print("========================================")
    print("        My Application Login")
    print("========================================")
    print()

    username = input("Username: ")
    password = getpass.getpass("Password: ")

    if authenticate(username, password):
        return True

    print()
    print("Authentication failed.")
    return False


def main():

    # --------------------------------------------
    # Authentication
    # --------------------------------------------

    if not login():
        input("\nPress ENTER to exit...")
        return

    # --------------------------------------------
    # Close CMD window
    # --------------------------------------------

    close_console()

    # --------------------------------------------
    # Start PySide6 application
    # --------------------------------------------

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()