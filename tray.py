from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QAction
from PySide6.QtCore import Qt

class PlantTrayIcon(QSystemTrayIcon):
    def __init__(self, plant_state=None, popup=None, parent=None):
        actual_parent = popup if popup is not None else parent
        super().__init__(actual_parent)
        self.plant_state = plant_state
        self.popup = popup
        self.is_active = True
        self.toggle_action = None

        self._update_state(True)
        self._build_menu()
        self.activated.connect(self._on_tray_activated)

    def _create_plant_icon(self, active=True):
        import os
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        icon_path = os.path.join(assets_dir, "plant_on.png" if active else "plant_off.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
            
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Pot
        pot_color = QColor("#D97706") if active else QColor("#6B7280")
        painter.setBrush(QBrush(pot_color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(8, 20, 16, 10)

        # Stem & Leaf
        leaf_color = QColor("#22C55E") if active else QColor("#9CA3AF")
        painter.setBrush(QBrush(leaf_color))
        painter.drawEllipse(10, 8, 12, 14)
        painter.end()

        return QIcon(pixmap)

    def _update_state(self, active):
        self.is_active = active
        self.setIcon(self._create_plant_icon(active))
        if active:
            self.setToolTip("🌱 Plant Complainer: ON (Click to turn OFF)")
        else:
            self.setToolTip("💤 Plant Complainer: OFF (Click to turn ON)")

    def toggle_active(self):
        new_state = not self.is_active
        self._update_state(new_state)

        if self.toggle_action:
            if new_state:
                self.toggle_action.setText("🟢 Turn OFF (Sleeping)")
            else:
                self.toggle_action.setText("🔴 Turn ON (Active)")

        if not new_state:
            if self.popup:
                self.popup.hide()
            self.showMessage("Plant Complainer", "🌱 Turned OFF (Muted)", QSystemTrayIcon.Information, 2000)
        else:
            if self.popup:
                self.popup.show()
                self.popup.raise_()
            self.showMessage("Plant Complainer", "🌱 Turned ON!", QSystemTrayIcon.Information, 2000)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_active()

    def _build_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #064E3B; color: #ECFDF5; border: 1px solid #10B981;
                font-family: 'Segoe UI', sans-serif; font-size: 13px;
            }
            QMenu::item:selected { background-color: #10B981; color: #064E3B; font-weight: bold; }
        """)

        sing_action = menu.addAction("🎵 Sing a Malayalam Song")
        sing_action.triggered.connect(self._trigger_sing)

        self.toggle_action = menu.addAction("🟢 Turn OFF (Sleeping)")
        self.toggle_action.triggered.connect(self.toggle_active)

        menu.addSeparator()

        exit_action = menu.addAction("🚪 Exit / Quit App")
        exit_action.triggered.connect(QApplication.quit)

        self.setContextMenu(menu)

    def _trigger_sing(self):
        if hasattr(QApplication.instance(), 'complaint_loop') and QApplication.instance().complaint_loop:
            QApplication.instance().complaint_loop.sing_song()

