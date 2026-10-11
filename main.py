import sys
import ctypes
import pwinput
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon 
from services.authentication import authenticate

from ui.main_window import MainWindow

# (Keep your resource_path function here if you used it earlier)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


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
    print("        Welcome slave! Once you enter this path, there is no turning back!")
    print("========================================")
    print()

    username = input("Username: ")
    # mask="*" tells it to show asterisks instead of hiding input
    password = pwinput.pwinput(prompt="Password: ", mask="*")

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

    icon_path = resource_path("app-icon.ico")
    app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()