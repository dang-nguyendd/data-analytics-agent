from PySide6.QtWidgets import QMainWindow, QStackedWidget

from ui.notebook_screen import NotebookScreen


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My Application")
        self.resize(1400, 900)

        self.stack = QStackedWidget()

        self.notebook_screen = NotebookScreen()

        self.stack.addWidget(self.notebook_screen)

        self.setCentralWidget(self.stack)

        self.show_notebook

    def show_notebook(self):
        self.stack.setCurrentWidget(
            self.notebook_screen
        )