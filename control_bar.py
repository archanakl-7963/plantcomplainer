import os
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QApplication
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QFont, QColor

class PlantControlBar(QWidget):
    """
    Sleek, 1-Click ON/OFF Control Switch Widget.
    Stays visible on top of screen and taskbar so the user can easily toggle the plant ON or OFF anytime!
    """
    def __init__(self, plant_state, popup, tray=None, parent=None):
        super().__init__(parent)
        self.plant_state = plant_state
        self.popup = popup
        self.tray = tray
        self.is_on = True
        
        self.setWindowTitle("🌱 Plant Complainer Switch")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(390, 52)
        
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        icon_path = os.path.join(assets_dir, "plant_on.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self._build_ui()
        self._position_top_right()
        
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        container = QWidget(self)
        container.setStyleSheet("""
            QWidget {
                background-color: #064E3B;
                border: 2px solid #10B981;
                border-radius: 20px;
            }
        """)
        c_layout = QHBoxLayout(container)
        c_layout.setContentsMargins(12, 4, 12, 4)
        
        title = QLabel("🌱 Plant Complainer", container)
        title.setStyleSheet("color: #ECFDF5; font-size: 13px; font-weight: bold; border: none;")
        c_layout.addWidget(title)
        
        sing_btn = QPushButton("🎵 Sing", container)
        sing_btn.setFixedSize(75, 32)
        sing_btn.setCursor(Qt.PointingHandCursor)
        sing_btn.setStyleSheet("""
            QPushButton {
                background-color: #D97706; color: #FFFBEB;
                font-size: 12px; font-weight: bold; border-radius: 14px; border: none;
            }
            QPushButton:hover { background-color: #F59E0B; }
        """)
        sing_btn.clicked.connect(self.sing_song)
        c_layout.addWidget(sing_btn)

        self.toggle_btn = QPushButton("🟢 ON", container)
        self.toggle_btn.setFixedSize(75, 32)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_state)
        c_layout.addWidget(self.toggle_btn)
        
        close_btn = QPushButton("❌", container)
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("QPushButton { background: transparent; color: #EF4444; font-size: 13px; font-weight: bold; border: none; } QPushButton:hover { color: #F87171; }")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(QApplication.quit)
        c_layout.addWidget(close_btn)
        
        layout.addWidget(container)
        self.update_btn_style()

    def sing_song(self):
        if hasattr(QApplication.instance(), 'complaint_loop') and QApplication.instance().complaint_loop:
            QApplication.instance().complaint_loop.sing_song()


    def update_btn_style(self):
        if self.is_on:
            self.toggle_btn.setText("🟢 ON")
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10B981; color: #064E3B;
                    font-size: 13px; font-weight: bold; border-radius: 14px; border: none;
                }
                QPushButton:hover { background-color: #34D399; }
            """)
        else:
            self.toggle_btn.setText("🔴 OFF")
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444; color: #FFFFFF;
                    font-size: 13px; font-weight: bold; border-radius: 14px; border: none;
                }
                QPushButton:hover { background-color: #F87171; }
            """)

    def toggle_state(self):
        self.is_on = not self.is_on
        self.update_btn_style()
        
        if self.tray:
            self.tray.is_active = self.is_on
            self.tray._update_state(self.is_on)
            
        if self.is_on:
            if self.popup:
                self.popup.show()
                self.popup.raise_()
        else:
            if self.popup:
                self.popup.hide()

    def _position_top_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = max(10, screen.width() - self.width() - 20)
        y = 20
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
