from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
)

class ChatMessage(QFrame):
    def __init__(
        self,
        message,
        role="user"  # Now safely accepts the string role
    ):
        super().__init__()

        self.message = message
        self.role = role
        self.is_user = (self.role == "user") 

        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 8, 0, 8)

        bubble = QFrame()
        bubble_layout = QVBoxLayout()
        bubble_layout.setContentsMargins(14, 10, 14, 10)
        bubble_layout.setSpacing(4)

        # ----------------------------------------------------
        # Sender
        # ----------------------------------------------------
        sender = QLabel("You" if self.is_user else "Assistant")
        sender.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #858585;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        bubble_layout.addWidget(sender)

        # ----------------------------------------------------
        # Message
        # ----------------------------------------------------
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        message_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #d4d4d4;
                font-size: 14px;
            }
        """)
        bubble_layout.addWidget(message_label)

        bubble.setLayout(bubble_layout)

        # ----------------------------------------------------
        # User (Aligned Right)
        # ----------------------------------------------------
        if self.is_user:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border: 1px solid #3f3f3f;
                    border-radius: 10px;
                }
            """)
            layout.addStretch()
            layout.addWidget(bubble, 0)

        # ----------------------------------------------------
        # Assistant (Aligned Left)
        # ----------------------------------------------------
        else:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: #252526;
                    border: 1px solid #333333;
                    border-radius: 10px;
                }
            """)
            layout.addWidget(bubble, 0)
            layout.addStretch()

        self.setLayout(layout)