from PySide6.QtCore import Qt, QDir, Signal
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QTreeView,
    QFileSystemModel,
    QMenu,
)


class FileBrowser(QWidget):

    # Emits the full path of the selected file.
    # Emits None when no file is selected.
    current_file_changed = Signal(object)

    def __init__(self):

        super().__init__()

        self.current_folder = None
        self.current_file = None

        self.setup_ui()

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

        # ====================================================
        # Select Folder
        # ====================================================

        self.select_button = QPushButton(
            "📁  Select Folder"
        )

        self.select_button.clicked.connect(
            self.select_folder
        )

        layout.addWidget(
            self.select_button
        )

        # ====================================================
        # File Model
        # ====================================================

        self.model = QFileSystemModel()

        # Only show:
        #
        #   folders
        #   .csv
        #   .parquet
        #
        self.model.setNameFilters([
            "*.csv",
            "*.parquet",
        ])

        self.model.setNameFilterDisables(
            False
        )

        self.model.setFilter(
            QDir.AllDirs
            |
            QDir.NoDotAndDotDot
            |
            QDir.Files
        )

        # ====================================================
        # Tree
        # ====================================================

        self.tree = QTreeView()

        self.tree.setModel(
            self.model
        )

        # Hide unnecessary columns
        self.tree.setColumnHidden(
            1,
            True
        )

        self.tree.setColumnHidden(
            2,
            True
        )

        self.tree.setColumnHidden(
            3,
            True
        )

        self.tree.setHeaderHidden(
            True
        )

        # Disable normal double-click opening
        self.tree.doubleClicked.connect(
            self.handle_double_click
        )

        # Right-click menu
        self.tree.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.tree.customContextMenuRequested.connect(
            self.show_context_menu
        )

        layout.addWidget(
            self.tree
        )

        self.setLayout(
            layout
        )

    # ========================================================
    # Select Folder
    # ========================================================

    def select_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Project Folder"
        )

        if not folder:
            return

        self.current_folder = folder

        index = self.model.setRootPath(
            folder
        )

        self.tree.setRootIndex(
            index
        )

        # Clear current file when changing project folder
        self.clear_current_file()

    # ========================================================
    # Double Click
    # ========================================================

    def handle_double_click(self, index):

        path = self.model.filePath(index)

        # Do nothing for files.
        #
        # Folder navigation is handled by QTreeView.
        if self.model.isDir(index):
            return

    # ========================================================
    # Right Click
    # ========================================================

    def show_context_menu(self, position):

        index = self.tree.indexAt(position)

        if not index.isValid():
            return

        # Only react to files
        if self.model.isDir(index):
            return

        path = self.model.filePath(index)

        # Make sure it is CSV or Parquet
        if not self.is_supported_file(path):
            return

        menu = QMenu(self)

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

            QMenu::separator {
                height: 1px;
                background-color: #444444;
                margin: 4px 8px;
            }
        """)

        # ----------------------------------------------------
        # Current file
        # ----------------------------------------------------

        if path == self.current_file:

            remove_action = menu.addAction(
                "✕  Remove from current use"
            )

            action = menu.exec(
                self.tree.mapToGlobal(position)
            )

            if action == remove_action:
                self.clear_current_file()

            return

        # ----------------------------------------------------
        # New current file
        # ----------------------------------------------------

        use_action = menu.addAction(
            "✓  Use as current file"
        )

        action = menu.exec(
            self.tree.mapToGlobal(position)
        )

        if action == use_action:
            self.set_current_file(path)

    # ========================================================
    # Supported File
    # ========================================================

    def is_supported_file(self, path):

        path_lower = path.lower()

        return (
            path_lower.endswith(".csv")
            or
            path_lower.endswith(".parquet")
        )

    # ========================================================
    # Set Current File
    # ========================================================

    def set_current_file(self, path):

        if not self.is_supported_file(path):
            return

        # Only ONE file can be active.
        self.current_file = path

        # Select it in the tree
        index = self.model.index(path)

        if index.isValid():
            self.tree.setCurrentIndex(index)

        # Tell NotebookScreen / chat input
        self.current_file_changed.emit(
            path
        )

    # ========================================================
    # Clear Current File
    # ========================================================

    def clear_current_file(self):

        if self.current_file is None:
            return

        self.current_file = None

        self.tree.clearSelection()

        self.current_file_changed.emit(
            None
        )

    # ========================================================
    # Get Current File
    # ========================================================

    def get_current_file(self):

        return self.current_file