import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QSplitter,
    QLabel,
    QTableView,
    QHeaderView
)

# UI components
from ui.file_browser import FileBrowser
from ui.chat_message import ChatMessage
from ui.chat_input import ChatInput
from ui.chat_history import ChatHistory

# services components
from services.chat_storage import ChatStorage
from services.ai_connector import AIConnector
from services.code_executor import CodeExecutor

load_dotenv()

# ========================================================
# Pandas Table Model for PySide6
# ========================================================
class PandasModel(QAbstractTableModel):
    """A model to interface a pandas DataFrame with a QTableView."""
    def __init__(self, df=pd.DataFrame()):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            value = self._df.iloc[index.row(), index.column()]
            return str(value)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._df.columns[section])
            elif orientation == Qt.Vertical:
                return str(self._df.index[section])
        return None

# ========================================================
# Main Screen
# ========================================================
class NotebookScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.ai_connector = AIConnector()
        self.storage = ChatStorage()
        self.code_executor = CodeExecutor()
        self.current_chat_id = None
        self.messages = []
        self.current_df = None
        
        self.setup_ui()

        # Create first chat if none exists
        chats = self.storage.get_chats()
        if chats:
            self.load_chat(chats[0]["id"])
        else:
            self.create_new_chat()

    def get_df(self):
        """Returns the current state of the DataFrame after AI modifications."""
        return self.current_df

    def set_df(self, new_df):
        """Allows the UI to inject a completely new DataFrame and update the table view."""
        self.current_df = new_df
        
        # Update the UI table automatically!
        if self.current_df is not None:
            model = PandasModel(self.current_df)
            self.table_view.setModel(model)
        else:
            self.table_view.setModel(None)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if not hasattr(self, "_splitter_initialized"):
            width = self.splitter.width()
            
            # Left sidebar ~ 20%, Right chat panel ~ 25%
            left_width = int(width * 0.20)
            right_width = int(width * 0.25)
            middle_width = width - left_width - right_width
            
            self.splitter.setSizes([left_width, middle_width, right_width])
            self._splitter_initialized = True

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Global Theme
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
            QPushButton:hover { background-color: #3a3a3a; border-color: #555555; }
            QPushButton:pressed { background-color: #252525; }
            QSplitter::handle { background-color: #333333; }
            QSplitter::handle:hover { background-color: #555555; }
        """)

        # Navigation Bar
        navbar = QWidget()
        navbar.setFixedHeight(50)
        navbar.setStyleSheet("background-color: #181818; border-bottom: 1px solid #333333;")
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(10, 5, 10, 5)

        title = QLabel("My Notebook")
        title.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 0px 12px 0px 5px;
                border: none;
            }
        """)
        nav_layout.addWidget(title)
        nav_layout.addStretch()
        navbar.setLayout(nav_layout)
        main_layout.addWidget(navbar)

        # Main Splitter (3 Sections)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)

        # ====================================================
        # 1. LEFT SIDEBAR
        # ====================================================
        self.sidebar_splitter = QSplitter(Qt.Vertical)
        self.sidebar_splitter.setHandleWidth(1)

        self.file_browser = FileBrowser()
        self.file_browser.current_file_changed.connect(self.on_current_file_changed)
        self.file_browser.setStyleSheet("""
            QWidget { background-color: #181818; color: #cccccc; }
            QTreeView {
                background-color: #181818;
                color: #cccccc;
                border: none;
                outline: none;
                selection-background-color: #37373d;
                selection-color: #ffffff;
            }
            QTreeView::item { padding: 4px; }
            QTreeView::item:hover { background-color: #2a2a2a; }
        """)
        self.sidebar_splitter.addWidget(self.file_browser)

        self.chat_history = ChatHistory(self.storage)
        self.chat_history.chat_selected.connect(self.load_chat)
        self.chat_history.new_chat_requested.connect(self.create_new_chat)
        self.chat_history.chat_deleted.connect(self.on_chat_deleted)
        
        self.sidebar_splitter.addWidget(self.chat_history)
        self.sidebar_splitter.setStretchFactor(0, 1)
        self.sidebar_splitter.setStretchFactor(1, 1)
        self.splitter.addWidget(self.sidebar_splitter)

        # ====================================================
        # 2. MIDDLE WORKSPACE (Replaced Placeholder with Table)
        # ====================================================
        middle_container = QWidget()
        middle_layout = QVBoxLayout()
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(0)

        # Create the Table View
        self.table_view = QTableView()
        self.table_view.setStyleSheet("""
            QTableView {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333333;
                gridline-color: #3f3f3f;
                selection-background-color: #37373d;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 4px;
                border: 1px solid #3f3f3f;
                font-weight: bold;
            }
            QTableCornerButton::section {
                background-color: #2d2d2d;
                border: 1px solid #3f3f3f;
            }
        """)
        
        # Add a nice margin around the table
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(20, 20, 20, 0)
        table_layout.addWidget(self.table_view)
        
        middle_layout.addWidget(table_container, 1)

        # Chat Input Area
        prompt_container = QWidget()
        prompt_layout = QVBoxLayout()
        prompt_layout.setContentsMargins(40, 10, 40, 20)

        self.chat_input = ChatInput()
        self.chat_input.send_requested.connect(self.send_message)
        prompt_layout.addWidget(self.chat_input)

        hint = QLabel("Press Enter to send • Shift + Enter for a new line")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #666666;
                border: none;
                font-size: 11px;
                padding-top: 5px;
            }
        """)
        prompt_layout.addWidget(hint)
        prompt_container.setLayout(prompt_layout)
        middle_layout.addWidget(prompt_container, 0)
        
        middle_container.setLayout(middle_layout)
        self.splitter.addWidget(middle_container)

        # ====================================================
        # 3. RIGHT CHAT PANEL
        # ====================================================
        chat_container = QWidget()
        chat_container.setStyleSheet("QWidget { background-color: #1e1e1e; border-left: 1px solid #333333; }")
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("border: none;")

        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(10)
        self.messages_layout.addStretch()
        
        self.messages_widget.setLayout(self.messages_layout)
        self.scroll_area.setWidget(self.messages_widget)
        chat_layout.addWidget(self.scroll_area, 1)
        chat_container.setLayout(chat_layout)
        
        self.splitter.addWidget(chat_container)

        # Stretch Config (0: no stretch, 1: stretch to fill, 2: no stretch)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 0)
        
        main_layout.addWidget(self.splitter)
        self.setLayout(main_layout)

    def create_new_chat(self):
        chat_id = self.storage.create_chat("New Chat")
        self.current_chat_id = chat_id
        self.messages = []
        self.clear_messages()
        
        self.chat_history.refresh(selected_chat_id=chat_id)
        self.chat_input.editor.setFocus()

    def load_chat(self, chat_id):
        chat = self.storage.load_chat(chat_id)
        if chat is None:
            return

        self.current_chat_id = chat_id
        self.messages = chat["messages"]
        self.clear_messages()

        for message in self.messages:
            # Safely handle JSON strings if stored that way
            content = message["content"]
            if isinstance(content, str) and content.startswith("{"):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    pass
            self.add_message_widget(content, message["role"])
            
        self.scroll_to_bottom()

    def send_message(self, message):
        if not message.strip():
            return

        if self.current_chat_id is None:
            self.create_new_chat()

        self.messages.append({"role": "user", "content": message})
        self.add_message_widget(message, "user")

        # Code and reponse inference 
        raw_response = self.ai_connector.send_chat_message(df=self.current_df, message=message)

        # Code execution
        self.code_executor.set_df(self.current_df)
        execution_response = self.code_executor.execute(ai_response=raw_response)
        
        # This will now automatically update the UI table!
        self.set_df(self.code_executor.get_df())

        response = {
            "type": "text",
            "content": raw_response + "\n\n> " + execution_response
        }
        
        # Save as a JSON string to satisfy ChatStorage write()
        self.messages.append({
            "role": "assistant",
            "content": json.dumps(response)
        })
        self.add_message_widget(response, "assistant")

        self.storage.save_chat(self.current_chat_id, self.messages)
        self.chat_history.refresh(selected_chat_id=self.current_chat_id)
        self.scroll_to_bottom()

    def add_message_widget(self, content, role):
        if isinstance(content, dict):
            self.add_text_message(content.get("content", ""), role)
        else:
            self.add_text_message(str(content), role)

    def add_text_message(self, content, role):
        message_widget = ChatMessage(content, role)
        self.messages_layout.insertWidget(
            self.messages_layout.count() - 1,
            message_widget
        )

    def clear_messages(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def on_chat_deleted(self, deleted_chat_id):
        if self.current_chat_id == deleted_chat_id:
            self.create_new_chat()

    def on_current_file_changed(self, file_path):
        if hasattr(self, 'chat_input'):
            self.chat_input.set_current_file(file_path)
            
        path = Path(file_path)
        # Safety check: ensure it's a CSV file before trying to read it
        if path.is_file() and path.suffix.lower() == '.csv':
            try:
                self.set_df(pd.read_csv(path))
            except Exception as e:
                print(f"Error loading CSV: {e}")

    def scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())