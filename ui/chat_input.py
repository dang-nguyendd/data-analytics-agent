from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QFrame,
)

# ==========================================================
# Chat input
# ==========================================================

class ChatInput(QFrame):

    send_requested = Signal(str)

    def __init__(self):

        super().__init__()

        self.current_file = None

        self.setup_ui()

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        self.setObjectName(
            "chatInput"
        )

        self.setStyleSheet("""
            QFrame#chatInput {
                background-color: #252526;
                border: 1px solid #444444;
                border-radius: 12px;
            }

            QPlainTextEdit {
                background-color: transparent;
                color: #d4d4d4;
                border: none;
                padding: 6px;
                font-family: "Segoe UI";
                font-size: 14px;
            }

            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: none;
                border-radius: 7px;
                padding: 7px 12px;
            }

            QPushButton:hover {
                background-color: #4a4a4a;
            }

            QPushButton:pressed {
                background-color: #555555;
            }
        """)

        # ====================================================
        # Main vertical layout
        # ====================================================

        layout = QVBoxLayout()

        layout.setContentsMargins(
            10,
            6,
            8,
            8
        )

        layout.setSpacing(2)

        # ====================================================
        # Current file
        # ====================================================

        self.file_row = QWidget()

        file_layout = QHBoxLayout()

        file_layout.setContentsMargins(
            2,
            0,
            2,
            0
        )

        file_layout.setSpacing(4)

        # ----------------------------------------------------
        # Small data icon
        # ----------------------------------------------------

        self.file_icon = QLabel("📄")

        self.file_icon.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
                color: #999999;
                font-size: 11px;
            }
        """)

        # ----------------------------------------------------
        # File name
        # ----------------------------------------------------

        self.file_name = QLabel()

        self.file_name.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
                color: #999999;
                font-size: 11px;
            }
        """)

        self.file_name.setToolTip("")

        file_layout.addWidget(
            self.file_icon
        )

        file_layout.addWidget(
            self.file_name
        )

        file_layout.addStretch()

        self.file_row.setLayout(
            file_layout
        )

        self.file_row.hide()

        # File row is ABOVE the input
        layout.addWidget(
            self.file_row
        )

        # ====================================================
        # Editor + Send
        # ====================================================

        input_layout = QHBoxLayout()

        input_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        input_layout.setSpacing(8)

        # ----------------------------------------------------
        # Editor
        # ----------------------------------------------------

        self.editor = QPlainTextEdit()

        self.editor.setPlaceholderText(
            "Message My Notebook..."
        )

        self.editor.setFixedHeight(
            44
        )

        self.editor.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.editor.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        input_layout.addWidget(
            self.editor
        )

        # ----------------------------------------------------
        # Send
        # ----------------------------------------------------

        self.send_button = QPushButton(
            "↑"
        )

        self.send_button.setFixedSize(
            36,
            36
        )

        self.send_button.clicked.connect(
            self.send
        )

        input_layout.addWidget(
            self.send_button
        )

        # Add editor row underneath file
        layout.addLayout(
            input_layout
        )

        self.setLayout(
            layout
        )

        self.editor.installEventFilter(
            self
        )

    # ========================================================
    # Send
    # ========================================================

    def send(self):

        text = self.editor.toPlainText().strip()

        if not text:
            return

        self.editor.clear()

        self.send_requested.emit(
            text
        )

    # ========================================================
    # Enter handling
    # ========================================================

    def eventFilter(
        self,
        obj,
        event
    ):

        if (
            obj == self.editor
            and event.type()
            == event.Type.KeyPress
        ):

            if event.key() in (
                Qt.Key_Return,
                Qt.Key_Enter
            ):

                if event.modifiers() & Qt.ShiftModifier:

                    return False

                self.send()

                return True

        return super().eventFilter(
            obj,
            event
        )

    # ========================================================
    # Set Current File
    # ========================================================

    def set_current_file(
        self,
        file_path
    ):

        self.current_file = file_path

        if file_path is None:

            self.file_row.hide()

            return

        filename = Path(
            file_path
        ).name

        self.file_name.setText(
            filename
        )

        self.file_name.setToolTip(
            file_path
        )

        self.file_row.show()