from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QInputDialog,
    QMessageBox,
)


class ChatHistory(QWidget):

    chat_selected = Signal(str)
    new_chat_requested = Signal()

    def __init__(
        self,
        storage
    ):

        super().__init__()

        self.storage = storage

        self.setup_ui()

        self.refresh()

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        layout = QVBoxLayout()

        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        layout.setSpacing(
            8
        )

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        title = QLabel(
            "Chat History"
        )

        title.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
            }
        """)

        layout.addWidget(
            title
        )

        # ----------------------------------------------------
        # New Chat
        # ----------------------------------------------------

        self.new_chat_button = QPushButton(
            "+  New chat"
        )

        self.new_chat_button.setFixedHeight(
            34
        )

        self.new_chat_button.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                color: #d4d4d4;
                border: 1px solid #3f3f3f;
                border-radius: 6px;
                text-align: left;
                padding-left: 10px;
            }

            QPushButton:hover {
                background-color: #333333;
            }

            QPushButton:pressed {
                background-color: #404040;
            }
        """)

        self.new_chat_button.clicked.connect(
            self.new_chat
        )

        layout.addWidget(
            self.new_chat_button
        )

        # ----------------------------------------------------
        # Chat List
        # ----------------------------------------------------

        self.chat_list = QListWidget()

        self.chat_list.setFrameShape(
            QFrame.NoFrame
        )

        self.chat_list.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.chat_list.customContextMenuRequested.connect(
            self.show_context_menu
        )

        self.chat_list.setStyleSheet("""
            QListWidget {
                background-color: #181818;
                color: #cccccc;
                border: none;
                outline: none;
            }

            QListWidget::item {
                padding: 9px 8px;
                border-radius: 5px;
                margin: 1px 0px;
            }

            QListWidget::item:hover {
                background-color: #2a2a2a;
            }

            QListWidget::item:selected {
                background-color: #37373d;
                color: #ffffff;
            }
        """)

        self.chat_list.itemClicked.connect(
            self.select_chat
        )

        layout.addWidget(
            self.chat_list
        )

        self.setLayout(
            layout
        )

    # ========================================================
    # Refresh
    # ========================================================

    def refresh(
        self,
        selected_chat_id=None
    ):

        self.chat_list.clear()

        chats = self.storage.get_chats()

        for chat in chats:

            title = chat["title"]

            if not title:

                title = "New Chat"

            item = QListWidgetItem(
                title
            )

            # Store chat ID

            item.setData(
                Qt.UserRole,
                chat["id"]
            )

            # Full title shown on hover

            item.setToolTip(
                title
            )

            self.chat_list.addItem(
                item
            )

        # Restore selection

        if selected_chat_id:

            self.select_item(
                selected_chat_id
            )

    # ========================================================
    # Select chat
    # ========================================================

    def select_chat(
        self,
        item
    ):

        chat_id = item.data(
            Qt.UserRole
        )

        self.chat_selected.emit(
            chat_id
        )

    # ========================================================
    # Select item programmatically
    # ========================================================

    def select_item(
        self,
        chat_id
    ):

        for i in range(
            self.chat_list.count()
        ):

            item = self.chat_list.item(
                i
            )

            if item.data(
                Qt.UserRole
            ) == chat_id:

                self.chat_list.setCurrentItem(
                    item
                )

                return

    # ========================================================
    # New Chat
    # ========================================================

    def new_chat(self):

        self.new_chat_requested.emit()

    # ========================================================
    # Context Menu
    # ========================================================

    def show_context_menu(
        self,
        position
    ):

        item = self.chat_list.itemAt(
            position
        )

        if item is None:

            return

        chat_id = item.data(
            Qt.UserRole
        )

        menu = QMenu(
            self
        )

        menu.setStyleSheet("""
            QMenu {
                background-color: #252525;
                color: #d4d4d4;
                border: 1px solid #444444;
                padding: 4px;
            }

            QMenu::item {
                padding: 7px 30px 7px 10px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background-color: #37373d;
                color: #ffffff;
            }
        """)

        # ----------------------------------------------------
        # Rename
        # ----------------------------------------------------

        rename_action = menu.addAction(
            "Rename"
        )

        # ----------------------------------------------------
        # View Details
        # ----------------------------------------------------

        details_action = menu.addAction(
            "View details"
        )

        menu.addSeparator()

        # ----------------------------------------------------
        # Delete
        # ----------------------------------------------------

        delete_action = menu.addAction(
            "Delete"
        )

        action = menu.exec(
            self.chat_list.mapToGlobal(
                position
            )
        )

        if action == rename_action:

            self.rename_chat(
                item,
                chat_id
            )

        elif action == details_action:

            self.view_details(
                chat_id
            )

        elif action == delete_action:

            self.delete_chat(
                chat_id
            )

    # ========================================================
    # Rename
    # ========================================================

    def rename_chat(
        self,
        item,
        chat_id
    ):

        current_title = item.text()

        new_title, ok = QInputDialog.getText(
            self,
            "Rename chat",
            "Chat name:",
            text=current_title
        )

        if not ok:

            return

        new_title = new_title.strip()

        if not new_title:

            return

        success = self.storage.rename_chat(
            chat_id,
            new_title
        )

        if success:

            item.setText(
                new_title
            )

            item.setToolTip(
                new_title
            )

    # ========================================================
    # View Details
    # ========================================================

    def view_details(
        self,
        chat_id
    ):

        chat = self.storage.load_chat(
            chat_id
        )

        if chat is None:

            return

        message_count = len(
            chat["messages"]
        )

        user_messages = sum(
            1
            for message in chat["messages"]
            if message["role"] == "user"
        )

        assistant_messages = sum(
            1
            for message in chat["messages"]
            if message["role"] == "assistant"
        )

        details = (
            f"Title: {chat['title']}\n\n"
            f"Chat ID: {chat['id']}\n\n"
            f"Created: {chat['created']}\n\n"
            f"Updated: {chat['updated']}\n\n"
            f"Messages: {message_count}\n"
            f"User messages: {user_messages}\n"
            f"Assistant messages: {assistant_messages}"
        )

        QMessageBox.information(
            self,
            "Chat details",
            details
        )

    # ========================================================
    # Delete
    # ========================================================

    def delete_chat(
        self,
        chat_id
    ):

        chat = self.storage.load_chat(
            chat_id
        )

        if chat is None:

            return

        result = QMessageBox.question(
            self,
            "Delete chat",
            (
                f"Delete '{chat['title']}'?\n\n"
                "This cannot be undone."
            ),
            QMessageBox.Yes
            |
            QMessageBox.No,
            QMessageBox.No
        )

        if result != QMessageBox.Yes:

            return

        self.storage.delete_chat(
            chat_id
        )

        self.refresh()