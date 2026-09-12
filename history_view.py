from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel
from PySide6.QtCore import Qt
from storage.state_manager import StateManager

class HistoryWindow(QDialog):
    """
    Log Window showing recent Malayalam gossips, complaints, and care interactions.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📜 Plant Companion - Interaction & Gossip History")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog { background-color: #064E3B; color: white; font-family: 'Segoe UI', sans-serif; }
            QListWidget { background-color: #047857; color: white; border-radius: 8px; padding: 5px; font-size: 13px; }
            QListWidget::item { border-bottom: 1px solid #059669; padding: 6px; }
            QPushButton { background-color: #059669; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #10B981; }
        """)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("📜 Recent Malayalam Complaints & Gossip Log", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #A7F3D0;")
        layout.addWidget(title)

        self.list_widget = QListWidget(self)
        self._load_history()
        layout.addWidget(self.list_widget)

        btn_close = QPushButton("Close Log", self)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _load_history(self):
        history = StateManager.get_history()
        if not history:
            item = QListWidgetItem("No recent plant gossip recorded yet.")
            self.list_widget.addItem(item)
            return

        for entry in history:
            text = entry.get("text", "")
            ctx = entry.get("context", "System")
            mood = entry.get("mood", "NORMAL")
            item_str = f"[{ctx} | {mood}] «{text}»"
            item = QListWidgetItem(item_str)
            self.list_widget.addItem(item)
