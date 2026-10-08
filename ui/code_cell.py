from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
)


class CodeCell(QFrame):

    run_requested = Signal(object)
    delete_requested = Signal(object)

    def __init__(self, number=1):
        super().__init__()

        self.number = number

        self.setup_ui()

    def setup_ui(self):

        # ==================================================
        # Cell style
        # ==================================================

        self.setFrameShape(
            QFrame.StyledPanel
        )

        self.setStyleSheet("""
            QFrame {
                background-color: #252526;
                color: #d4d4d4;

                border: 1px solid #3f3f3f;
                border-radius: 6px;
            }

            /* ============================================
               Cell number
               ============================================ */

            QLabel {
                color: #858585;
                background-color: transparent;
                border: none;
            }

            /* ============================================
               Code editor
               ============================================ */

            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;

                border: 1px solid #333333;
                border-radius: 4px;

                padding: 6px;

                selection-background-color: #264f78;
                selection-color: #ffffff;

                font-family: Consolas;
                font-size: 13px;
            }

            QPlainTextEdit:focus {
                border: 1px solid #555555;
            }

            /* ============================================
               Output
               ============================================ */

            QPlainTextEdit#output {
                background-color: #181818;
                color: #bdbdbd;

                border: 1px solid #333333;
                border-radius: 4px;

                padding: 6px;

                selection-background-color: #264f78;
                selection-color: #ffffff;

                font-family: Consolas;
                font-size: 12px;
            }

            /* ============================================
               Buttons
               ============================================ */

            QPushButton {
                background-color: transparent;
                color: #cccccc;

                border: none;
                border-radius: 4px;

                padding: 5px 10px;
            }

            QPushButton:hover {
                background-color: #333333;
                color: #ffffff;
            }

            QPushButton:pressed {
                background-color: #3d3d3d;
            }

            /* ============================================
               Run button
               ============================================ */

            QPushButton#runButton {
                color: #d4d4d4;
            }

            QPushButton#runButton:hover {
                background-color: #2d3d2d;
            }

            /* ============================================
               Delete button
               ============================================ */

            QPushButton#deleteButton {
                color: #999999;
                font-size: 14px;
            }

            QPushButton#deleteButton:hover {
                background-color: #3d2929;
                color: #ff8888;
            }
        """)

        # ==================================================
        # Main layout
        # ==================================================

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        main_layout.setSpacing(6)

        # ==================================================
        # Top row
        # ==================================================

        top_layout = QHBoxLayout()

        top_layout.setSpacing(3)

        # --------------------------------------------------
        # Cell number
        # --------------------------------------------------

        self.number_label = QLabel(
            f"[{self.number}]"
        )

        self.number_label.setFont(
            QFont("Consolas", 10)
        )

        top_layout.addWidget(
            self.number_label
        )

        top_layout.addStretch()

        # --------------------------------------------------
        # Run button
        # --------------------------------------------------

        self.run_button = QPushButton(
            "▶ Run"
        )

        self.run_button.setObjectName(
            "runButton"
        )

        self.run_button.clicked.connect(
            self.run
        )

        top_layout.addWidget(
            self.run_button
        )

        # --------------------------------------------------
        # Delete button
        # --------------------------------------------------

        self.delete_button = QPushButton(
            "✕"
        )

        self.delete_button.setObjectName(
            "deleteButton"
        )

        self.delete_button.setFixedWidth(
            32
        )

        self.delete_button.clicked.connect(
            self.delete
        )

        top_layout.addWidget(
            self.delete_button
        )

        main_layout.addLayout(
            top_layout
        )

        # ==================================================
        # Code editor
        # ==================================================

        self.editor = QPlainTextEdit()

        self.editor.setPlaceholderText(
            "Write Python code here..."
        )

        self.editor.setFont(
            QFont("Consolas", 11)
        )

        self.editor.setMinimumHeight(
            100
        )

        main_layout.addWidget(
            self.editor
        )

        # ==================================================
        # Output
        # ==================================================

        self.output = QPlainTextEdit()

        self.output.setObjectName(
            "output"
        )

        self.output.setReadOnly(
            True
        )

        self.output.setPlaceholderText(
            "Output will appear here..."
        )

        self.output.setFont(
            QFont("Consolas", 10)
        )

        self.output.setMaximumHeight(
            120
        )

        main_layout.addWidget(
            self.output
        )

        self.setLayout(
            main_layout
        )

    # ======================================================
    # Run
    # ======================================================

    def run(self):

        self.output.setPlainText(
            "Code execution will be implemented here."
        )

        self.run_requested.emit(
            self
        )

    # ======================================================
    # Delete
    # ======================================================

    def delete(self):

        self.delete_requested.emit(
            self
        )

    # ======================================================
    # Update number
    # ======================================================

    def set_number(self, number):

        self.number = number

        self.number_label.setText(
            f"[{number}]"
        )