from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
)


class TableView(QWidget):

    page_changed = Signal(int)

    def __init__(self, result, parent=None):
        super().__init__(parent)

        self.result = result

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # --------------------------------------------------
        # Table
        # --------------------------------------------------

        self.table = QTableWidget()

        columns = self.result["columns"]
        data = self.result["data"]

        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(columns))

        self.table.setHorizontalHeaderLabels(columns)

        for row_index, row in enumerate(data):

            for column_index, value in enumerate(row):

                item = QTableWidgetItem(
                    "" if value is None else str(value)
                )

                self.table.setItem(
                    row_index,
                    column_index,
                    item
                )

        self.table.resizeColumnsToContents()

        layout.addWidget(self.table)

        # --------------------------------------------------
        # Pagination
        # --------------------------------------------------

        pagination_layout = QHBoxLayout()

        self.previous_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")

        self.page_label = QLabel()

        self.previous_button.clicked.connect(
            self.previous_page
        )

        self.next_button.clicked.connect(
            self.next_page
        )

        pagination_layout.addWidget(
            self.previous_button
        )

        pagination_layout.addStretch()

        pagination_layout.addWidget(
            self.page_label
        )

        pagination_layout.addStretch()

        pagination_layout.addWidget(
            self.next_button
        )

        layout.addLayout(pagination_layout)

        self.update_pagination()

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    def update_pagination(self):

        page = self.result["page"]
        total_pages = self.result["total_pages"]

        self.page_label.setText(
            f"Page {page} / {total_pages}"
        )

        self.previous_button.setEnabled(
            self.result["has_previous"]
        )

        self.next_button.setEnabled(
            self.result["has_next"]
        )

    def previous_page(self):

        if self.result["has_previous"]:

            self.page_changed.emit(
                self.result["page"] - 1
            )

    def next_page(self):

        if self.result["has_next"]:

            self.page_changed.emit(
                self.result["page"] + 1
            )

    def update_table(self, result):

        self.result = result

        columns = result["columns"]
        data = result["data"]

        self.table.clear()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        for row_index, row in enumerate(data):

            for column_index, value in enumerate(row):

                item = QTableWidgetItem(
                    "" if value is None else str(value)
                )

                self.table.setItem(
                    row_index,
                    column_index,
                    item
                )

        self.table.resizeColumnsToContents()

        self.update_pagination()