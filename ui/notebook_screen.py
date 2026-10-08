from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QSplitter,
    QLabel,
    QPlainTextEdit,
    QFrame,
)

from cmds.show_data import show_table

from ui.file_browser import FileBrowser
from services.chat_storage import ChatStorage
from ui.chat_message import ChatMessage
from ui.chat_input import ChatInput
from ui.chat_history import ChatHistory
from ui.table_view import TableView

class NotebookScreen(QWidget):

    def __init__(self):

        super().__init__()

        # ----------------------------------------------------
        # Chat storage
        # ----------------------------------------------------

        self.storage = ChatStorage()

        # Current conversation

        self.current_chat_id = None

        self.messages = []

        self.setup_ui()

        # Create first chat if none exists

        chats = self.storage.get_chats()

        if chats:

            self.load_chat(
                chats[0]["id"]
            )

        else:

            self.create_new_chat()

    # ========================================================
    # Resize
    # ========================================================

    def resizeEvent(self, event):

        super().resizeEvent(
            event
        )

        if not hasattr(
            self,
            "_splitter_initialized"
        ):

            width = self.splitter.width()

            sidebar_width = int(
                width * 0.20
            )

            self.splitter.setSizes([
                sidebar_width,
                width - sidebar_width
            ])

            self._splitter_initialized = True

    # ========================================================
    # Setup UI
    # ========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(
            0
        )

        # ====================================================
        # Global Theme
        # ====================================================

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: "Segoe UI";
                font-size: 13px;
            }

            QPushButton {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3f3f3f;
                border-radius: 5px;
                padding: 7px 14px;
            }

            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #555555;
            }

            QPushButton:pressed {
                background-color: #252525;
            }

            QSplitter::handle {
                background-color: #333333;
            }

            QSplitter::handle:hover {
                background-color: #555555;
            }
        """)

        # ====================================================
        # Navigation Bar
        # ====================================================

        navbar = QWidget()

        navbar.setFixedHeight(
            50
        )

        navbar.setStyleSheet("""
            QWidget {
                background-color: #181818;
                border-bottom: 1px solid #333333;
            }

            QPushButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                border-radius: 4px;
                padding: 7px 12px;
            }

            QPushButton:hover {
                background-color: #2d2d2d;
                color: #ffffff;
            }
        """)

        nav_layout = QHBoxLayout()

        nav_layout.setContentsMargins(
            10,
            5,
            10,
            5
        )

        nav_layout.setSpacing(
            2
        )

        title = QLabel(
            "My Notebook"
        )

        title.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 0px 12px 0px 5px;
            }
        """)

        nav_layout.addWidget(
            title
        )

        # for text in [
        #     "File",
        #     "Edit",
        #     "View",
        #     "Run",
        #     "Kernel"
        # ]:

        #     nav_layout.addWidget(
        #         QPushButton(text)
        #     )

        nav_layout.addStretch()

        # settings = QPushButton(
        #     "⚙"
        # )

        # settings.setFixedWidth(
        #     40
        # )

        # nav_layout.addWidget(
        #     settings
        # )

        navbar.setLayout(
            nav_layout
        )

        main_layout.addWidget(
            navbar
        )

        # ====================================================
        # Main Splitter
        # ====================================================

        self.splitter = QSplitter(
            Qt.Horizontal
        )

        self.splitter.setHandleWidth(
            1
        )

        # ====================================================
        # LEFT SIDEBAR
        # ====================================================

        self.sidebar_splitter = QSplitter(
            Qt.Vertical
        )

        self.sidebar_splitter.setHandleWidth(
            1
        )

        # ----------------------------------------------------
        # File Browser
        # ----------------------------------------------------

        self.file_browser = FileBrowser()
        self.file_browser.current_file_changed.connect(
            self.on_current_file_changed
        )

        self.file_browser.setStyleSheet("""
            QWidget {
                background-color: #181818;
                color: #cccccc;
            }

            QPushButton {
                background-color: #252525;
                color: #d4d4d4;
                border: 1px solid #3f3f3f;
                border-radius: 5px;
                padding: 7px 10px;
            }

            QPushButton:hover {
                background-color: #333333;
            }

            QTreeView {
                background-color: #181818;
                color: #cccccc;
                border: none;
                outline: none;
                selection-background-color: #37373d;
                selection-color: #ffffff;
            }

            QTreeView::item {
                padding: 4px;
            }

            QTreeView::item:hover {
                background-color: #2a2a2a;
            }
        """)

        self.sidebar_splitter.addWidget(
            self.file_browser
        )

        # ----------------------------------------------------
        # Chat History
        # ----------------------------------------------------

        self.chat_history = ChatHistory(
            self.storage
        )

        self.chat_history.chat_selected.connect(
            self.load_chat
        )

        self.chat_history.new_chat_requested.connect(
            self.create_new_chat
        )

        self.sidebar_splitter.addWidget(
            self.chat_history
        )

        self.sidebar_splitter.setStretchFactor(
            0,
            1
        )

        self.sidebar_splitter.setStretchFactor(
            1,
            1
        )

        self.splitter.addWidget(
            self.sidebar_splitter
        )

        # ====================================================
        # RIGHT CHAT
        # ====================================================

        chat_container = QWidget()

        chat_container.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
        """)

        chat_layout = QVBoxLayout()

        chat_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        chat_layout.setSpacing(
            0
        )

        # ----------------------------------------------------
        # Messages
        # ----------------------------------------------------

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setFrameShape(
            QScrollArea.NoFrame
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.messages_widget = QWidget()

        self.messages_layout = QVBoxLayout()

        self.messages_layout.setContentsMargins(
            60,
            25,
            60,
            25
        )

        self.messages_layout.setSpacing(
            4
        )

        self.messages_layout.addStretch()

        self.messages_widget.setLayout(
            self.messages_layout
        )

        self.scroll_area.setWidget(
            self.messages_widget
        )

        chat_layout.addWidget(
            self.scroll_area,
            1
        )

        # ----------------------------------------------------
        # Prompt
        # ----------------------------------------------------

        prompt_container = QWidget()

        prompt_layout = QVBoxLayout()

        prompt_layout.setContentsMargins(
            60,
            10,
            60,
            20
        )

        self.chat_input = ChatInput()

        self.chat_input.send_requested.connect(
            self.send_message
        )

        prompt_layout.addWidget(
            self.chat_input
        )

        hint = QLabel(
            "Press Enter to send • "
            "Shift + Enter for a new line"
        )

        hint.setAlignment(
            Qt.AlignCenter
        )

        hint.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #666666;
                border: none;
                font-size: 11px;
                padding-top: 5px;
            }
        """)

        prompt_layout.addWidget(
            hint
        )

        prompt_container.setLayout(
            prompt_layout
        )

        chat_layout.addWidget(
            prompt_container
        )

        chat_container.setLayout(
            chat_layout
        )

        self.splitter.addWidget(
            chat_container
        )

        # ----------------------------------------------------
        # 20 / 80
        # ----------------------------------------------------

        self.splitter.setStretchFactor(
            0,
            0
        )

        self.splitter.setStretchFactor(
            1,
            1
        )

        main_layout.addWidget(
            self.splitter
        )

        self.setLayout(
            main_layout
        )

    # ========================================================
    # Create New Chat
    # ========================================================

    def create_new_chat(self):

        chat_id = self.storage.create_chat(
            "New Chat"
        )

        self.current_chat_id = chat_id

        self.messages = []

        self.clear_messages()

        self.chat_history.refresh(
            selected_chat_id=chat_id
        )

        self.chat_input.editor.setFocus()

    # ========================================================
    # Load Chat
    # ========================================================

    def load_chat(self, chat_id):

        chat = self.storage.load_chat(
            chat_id
        )

        if chat is None:
            return

        self.current_chat_id = chat_id

        self.messages = chat["messages"]

        self.clear_messages()

        # Recreate UI messages

        for message in self.messages:

            self.add_message_widget(
                message["content"],
                message["role"]
            )

        self.scroll_to_bottom()

    # ========================================================
    # Send Message
    # ========================================================

    def send_message(self, message):

        if not message.strip():
            return

        # ------------------------------------------------------------
        # Create chat if necessary
        # ------------------------------------------------------------

        if self.current_chat_id is None:
            self.create_new_chat()

        # ------------------------------------------------------------
        # User message
        # ------------------------------------------------------------

        self.messages.append({
            "role": "user",
            "content": message
        })

        self.add_message_widget(
            message,
            "user"
        )

        # ------------------------------------------------------------
        # Assistant response
        # ------------------------------------------------------------

        response = {
            "type": "text",
            "content": "hello world"
        }

        self.messages.append({
            "role": "assistant",
            "content": response
        })

        if response.get("type") == "table":
            self.add_message_widget(
                "[TABLE]",
                "assistant"
            )
        else:
            self.add_message_widget(
                response,
                "assistant"
            )

        # ------------------------------------------------------------
        # Save
        #
        # ChatStorage decides whether to:
        #
        #   1. use first user message as title
        #   2. preserve manually renamed title
        # ------------------------------------------------------------

        self.storage.save_chat(
            self.current_chat_id,
            self.messages
        )

        # ------------------------------------------------------------
        # Refresh history
        # ------------------------------------------------------------

        self.chat_history.refresh(
            selected_chat_id=self.current_chat_id
        )

        self.scroll_to_bottom()

    # ========================================================
    # Add message widget
    # ========================================================

    def add_message_widget(self, content, role):

        if isinstance(content, dict):

            result_type = content.get("type")

            if result_type == "text":
                self.add_text_message(
                    content.get("content", ""),
                    role
                )

            elif result_type == "table":
                self.add_table_message(
                    content,
                    role
                )

            else:
                self.add_text_message(
                    str(content),
                    role
                )

        else:
            self.add_text_message(
                str(content),
                role
            )

    def add_text_message(self, content, role):

        message_widget = ChatMessage(
            content,
            role
        )

        self.messages_layout.insertWidget(
            self.messages_layout.count() - 1,
            message_widget
        )

    # ========================================================
    # Clear messages
    # ========================================================

    def clear_messages(self):

        while (
            self.messages_layout.count()
            > 1
        ):

            item = self.messages_layout.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

    # ========================================================
    # Select sidebar item
    # ========================================================

    def select_history_item(
        self,
        chat_id
    ):

        for i in range(
            self.chat_history.chat_list.count()
        ):

            item = (
                self.chat_history.chat_list.item(i)
            )

            if item.data(
                Qt.UserRole
            ) == chat_id:

                self.chat_history.chat_list.setCurrentItem(
                    item
                )

                break

    def on_current_file_changed(self, file_path):

        self.chat_input.set_current_file(
            file_path
        )

    def add_table_message(self, result, role):

        table = TableView(result)

        table.page_changed.connect(
            lambda page: self.change_table_page(
                table,
                result,
                page
            )
        )

        self.message_layout.addWidget(table)

    def change_table_page(self, table, result, page):

        new_result = show_table(
            result["dataframe"],
            page=page,
            page_size=result["page_size"]
        )

        table.update_table(new_result)

    # ========================================================
    # Scroll
    # ========================================================

    def scroll_to_bottom(self):

        scrollbar = (
            self.scroll_area.verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )