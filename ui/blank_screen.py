from PySide6.QtWidgets import QWidget


class BlankScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)