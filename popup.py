import os
import sys
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QBrush, QPen, QPainterPath, QIcon

class PlantAvatarWidget(QWidget):
    """Custom drawn large cute plant avatar expressing distinct emotions with animated flying bees."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(240, 240)
        self.expression = "cute"
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Animated bees state
        self.bee_angle = 0.0
        self.bee_timer = QTimer(self)
        self.bee_timer.timeout.connect(self._animate_bees)
        self.bee_timer.start(40) # ~25 FPS smooth animation

    def _animate_bees(self):
        self.bee_angle += 0.07
        if self.bee_angle > 62.83:
            self.bee_angle = 0.0
        self.update()

    def set_expression(self, expr):
        self.expression = expr.lower() if expr else "cute"
        self.update()

    def paintEvent(self, event):
        import math
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.scale(1.5, 1.5) # Scale from 160x160 design to 240x240

        # Large Terracotta Pot
        pot_brush = QBrush(QColor("#D97706"))
        painter.setBrush(pot_brush)
        painter.setPen(QPen(QColor("#78350F"), 3))
        
        pot_path = QPainterPath()
        pot_path.moveTo(35, 100)
        pot_path.lineTo(125, 100)
        pot_path.lineTo(110, 150)
        pot_path.lineTo(50, 150)
        pot_path.closeSubpath()
        painter.drawPath(pot_path)

        # Soil
        painter.setBrush(QBrush(QColor("#451A03")))
        painter.drawEllipse(32, 92, 96, 18)

        # Stem
        stem_pen = QPen(QColor("#16A34A") if self.expression not in ["thirsty", "sad", "drama_queen"] else QColor("#CA8A04"), 7)
        painter.setPen(stem_pen)

        if self.expression in ["thirsty", "sad", "drama_queen"]:
            painter.drawArc(65, 38, 60, 60, 0 * 16, 180 * 16)
        else:
            painter.drawLine(80, 95, 80, 48)

        # Leaves
        leaf_color = QColor("#22C55E") if self.expression not in ["thirsty", "sad"] else QColor("#EAB308")
        painter.setBrush(QBrush(leaf_color))
        painter.setPen(QPen(QColor("#15803D"), 2))
        painter.drawEllipse(40, 60, 38, 20)
        painter.drawEllipse(82, 60, 38, 20)

        # Plant Head / Flower
        if self.expression == "angry":
            head_color = QColor("#EF4444")
        elif self.expression == "happy":
            head_color = QColor("#F59E0B")  # Golden blooming flower
        elif self.expression in ["sad", "drama_queen"]:
            head_color = QColor("#38BDF8")  # Teary blue flower
        else:
            head_color = QColor("#4ADE80")

        painter.setBrush(QBrush(head_color))
        painter.setPen(QPen(QColor("#166534"), 3))
        painter.drawEllipse(56, 18, 48, 48)

        # 1. HAPPY EMOTION: Flower Petals & Smile
        if self.expression == "happy":
            painter.setBrush(QBrush(QColor("#FBBF24")))
            painter.setPen(QPen(QColor("#D97706"), 1.5))
            painter.drawEllipse(44, 20, 16, 16)
            painter.drawEllipse(100, 20, 16, 16)
            painter.drawEllipse(72, 4, 16, 16)
            painter.drawEllipse(72, 44, 16, 16)
            painter.setBrush(QBrush(QColor("#4ADE80")))
            painter.drawEllipse(56, 18, 48, 48)

        # Face Eyes & Mouth
        painter.setPen(QPen(QColor("#064E3B") if self.expression != "angry" else QColor("#7F1D1D"), 3.5))
        painter.setBrush(QBrush(QColor("#064E3B")))

        if self.expression in ["cute", "happy"]:
            painter.drawArc(65, 28, 10, 10, 0, 180 * 16)
            painter.drawArc(85, 28, 10, 10, 0, 180 * 16)
            painter.drawArc(71, 40, 18, 14, 180 * 16, 180 * 16)

        elif self.expression == "annoyed":
            painter.drawLine(64, 32, 74, 32)
            painter.drawLine(86, 32, 96, 32)
            painter.drawLine(71, 46, 89, 46)

        elif self.expression == "angry":
            painter.drawLine(61, 25, 76, 34)
            painter.drawLine(99, 25, 84, 34)
            painter.drawEllipse(68, 33, 6, 6)
            painter.drawEllipse(86, 33, 6, 6)
            painter.drawArc(71, 44, 18, 14, 0, 180 * 16)

        elif self.expression in ["drama_queen", "sad", "thirsty"]:
            painter.drawArc(65, 33, 9, 9, 0, 180 * 16)
            painter.drawArc(85, 33, 9, 9, 0, 180 * 16)
            painter.setBrush(QBrush(QColor("#38BDF8")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(94, 38, 7, 12)
            painter.drawEllipse(59, 38, 7, 12)
            painter.setPen(QPen(QColor("#064E3B"), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(73, 42, 14, 14)

        # --- ANIMATED BEES FLYING AROUND PLANT ---
        for i in range(3):
            phase = self.bee_angle + (i * 2.094)
            radius_x = 52 + i * 9
            radius_y = 22 + i * 5
            
            cx = 80 + math.cos(phase) * radius_x
            cy = 40 + math.sin(phase) * radius_y + math.sin(phase * 2.5) * 5

            # Yellow Bee Body
            painter.setBrush(QBrush(QColor("#FACC15")))
            painter.setPen(QPen(QColor("#78350F"), 1.5))
            painter.drawEllipse(int(cx - 7), int(cy - 5), 14, 10)

            # Black Stripes
            painter.setBrush(QBrush(QColor("#1F2937")))
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(cx - 2), int(cy - 5), 3, 10)
            painter.drawRect(int(cx + 3), int(cy - 4), 2, 8)

            # Fluttering Wings
            wing_flutter = math.sin(phase * 16) * 4
            painter.setBrush(QBrush(QColor(240, 249, 255, 210)))
            painter.setPen(QPen(QColor("#38BDF8"), 1))
            painter.drawEllipse(int(cx - 5), int(cy - 10 + wing_flutter), 6, 7)
            painter.drawEllipse(int(cx + 1), int(cy - 10 - wing_flutter), 6, 7)

            # Bee Eye
            painter.setBrush(QBrush(QColor("#000000")))
            painter.drawEllipse(int(cx - 6), int(cy - 2), 2, 2)


class SpeechBubbleWidget(QWidget):
    """Custom comic-style speech bubble."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text = ""
        self.emotion = "cute"
        self.bubble_color = QColor("#10B981")
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(50, 30, 30, 30) # Left margin fits the triangle pointer
        
        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        
    def set_content(self, text, emotion):
        self.text = text
        self.emotion = emotion.lower()
        
        if self.emotion == "angry":
            color = "#B91C1C"
            font_color = "#FEF2F2"
        elif self.emotion in ["sad", "thirsty", "drama_queen"]:
            color = "#0369A1"
            font_color = "#F0F9FF"
        elif self.emotion == "happy":
            color = "#B45309"
            font_color = "#FFFBEB"
        else:
            color = "#047857"
            font_color = "#F0FDF4"
            
        self.label.setText(f"«{self.text}»")
        self.label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {font_color};")
        self.bubble_color = QColor(color)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        rect = self.rect().adjusted(25, 5, -5, -5)
        path.addRoundedRect(rect, 25, 25)
        
        # Left pointing triangle
        triangle = QPainterPath()
        triangle.moveTo(25, 50)
        triangle.lineTo(0, 75)
        triangle.lineTo(25, 95)
        triangle.closeSubpath()
        path.addPath(triangle)
        
        painter.setBrush(QBrush(QColor(self.bubble_color.red(), self.bubble_color.green(), self.bubble_color.blue(), 235)))
        painter.setPen(QPen(self.bubble_color.darker(150), 4))
        painter.drawPath(path.simplified())


class ScreenBee:
    def __init__(self, screen_w, screen_h):
        import random
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.x = float(random.randint(100, max(200, screen_w - 100)))
        self.y = float(random.randint(100, max(200, screen_h - 100)))
        self.vx = random.choice([-3.0, -2.0, 2.0, 3.0])
        self.vy = random.choice([-2.5, -1.5, 1.5, 2.5])
        self.angle = random.uniform(0, 6.28)
        self.wing_phase = random.uniform(0, 6.28)

    def update(self, plant_pos=None):
        import math, random
        self.wing_phase += 0.45
        self.angle += 0.06

        drift_x = math.cos(self.angle * 1.2) * 1.5
        drift_y = math.sin(self.angle * 1.6) * 1.5

        if plant_pos and random.random() < 0.6:
            tx = plant_pos.x() + 100 + math.cos(self.angle) * 120
            ty = plant_pos.y() + 80 + math.sin(self.angle) * 80
            self.x += (tx - self.x) * 0.05 + drift_x
            self.y += (ty - self.y) * 0.05 + drift_y
        else:
            self.x += self.vx + drift_x
            self.y += self.vy + drift_y

            if self.x < 20 or self.x > self.screen_w - 40:
                self.vx *= -1
            if self.y < 20 or self.y > self.screen_h - 40:
                self.vy *= -1


class ScreenDragonfly:
    """
    Animated metallic dragonfly that flies in fast, sharp zigzag motions across the screen.
    """
    def __init__(self, screen_w, screen_h):
        import random
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.x = float(random.randint(100, max(200, screen_w - 100)))
        self.y = float(random.randint(100, max(200, screen_h - 100)))
        
        self.angle = random.uniform(0, 6.28)
        self.speed = random.uniform(5.0, 7.5)
        self.zigzag_timer = 0
        self.zigzag_interval = random.randint(8, 18)
        self.wing_phase = random.uniform(0, 6.28)

    def update(self, plant_pos=None):
        import math, random
        self.wing_phase += 0.7
        self.zigzag_timer += 1

        # Sudden sharp 45°-90° zigzag turns
        if self.zigzag_timer >= self.zigzag_interval:
            self.zigzag_timer = 0
            self.zigzag_interval = random.randint(8, 20)
            turn = random.choice([-1.2, -0.7, 0.7, 1.2])
            self.angle += turn

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Screen boundaries bounce turn
        if self.x < 40:
            self.x = 40
            self.angle = random.uniform(-1.0, 1.0)
        elif self.x > self.screen_w - 50:
            self.x = self.screen_w - 50
            self.angle = random.uniform(2.1, 4.1)

        if self.y < 40:
            self.y = 40
            self.angle = random.uniform(0.5, 2.6)
        elif self.y > self.screen_h - 50:
            self.y = self.screen_h - 50
            self.angle = random.uniform(-2.6, -0.5)


class ScreenBeesOverlay(QWidget):
    """
    100% Transparent, Click-Through Overlay for Screen-Wide Flying Bees & Dragonflies.
    Bears zero impact on user mouse input.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowTransparentForInput |
            Qt.WindowSystemMenuHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.bees = [ScreenBee(screen.width(), screen.height()) for _ in range(6)]
        self.dragonflies = [ScreenDragonfly(screen.width(), screen.height()) for _ in range(5)]
        self.plant_pos = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(35) # ~30 FPS flight loop

    def update_plant_position(self, pos):
        self.plant_pos = pos

    def _on_tick(self):
        for bee in self.bees:
            bee.update(self.plant_pos)
        for df in self.dragonflies:
            df.update(self.plant_pos)
        self.update()

    def paintEvent(self, event):
        import math
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Draw Bees
        for bee in self.bees:
            bx, by = int(bee.x), int(bee.y)

            # Yellow Bee Body
            painter.setBrush(QBrush(QColor("#FACC15")))
            painter.setPen(QPen(QColor("#78350F"), 1.5))
            painter.drawEllipse(bx - 9, by - 6, 18, 12)

            # Black Stripes
            painter.setBrush(QBrush(QColor("#1F2937")))
            painter.setPen(Qt.NoPen)
            painter.drawRect(bx - 3, by - 6, 3, 12)
            painter.drawRect(bx + 3, by - 5, 2, 10)

            # Fluttering Translucent Wings
            wing_flutter = int(math.sin(bee.wing_phase) * 5)
            painter.setBrush(QBrush(QColor(240, 249, 255, 210)))
            painter.setPen(QPen(QColor("#38BDF8"), 1))
            painter.drawEllipse(bx - 7, by - 12 + wing_flutter, 7, 9)
            painter.drawEllipse(bx + 1, by - 12 - wing_flutter, 7, 9)

            # Bee Eye
            painter.setBrush(QBrush(QColor("#000000")))
            painter.drawEllipse(bx - 7, by - 2, 3, 3)

        # 2. Draw Zigzag Metallic Blue Dragonflies
        for df in self.dragonflies:
            dx, dy = int(df.x), int(df.y)
            
            painter.save()
            painter.translate(dx, dy)
            painter.rotate(math.degrees(df.angle))

            # Segmented Metallic Tail
            painter.setBrush(QBrush(QColor("#06B6D4")))
            painter.setPen(QPen(QColor("#0891B2"), 1.5))
            painter.drawEllipse(-18, -2, 5, 4)
            painter.drawEllipse(-12, -2, 5, 4)
            painter.drawEllipse(-6, -2, 5, 4)

            # Thorax & Head
            painter.setBrush(QBrush(QColor("#0EA5E9")))
            painter.setPen(QPen(QColor("#0284C7"), 1.5))
            painter.drawEllipse(0, -4, 9, 8)

            # Compound Eyes
            painter.setBrush(QBrush(QColor("#0369A1")))
            painter.drawEllipse(6, -5, 4, 4)
            painter.drawEllipse(6, 1, 4, 4)

            # Double Translucent Fluttering Wings
            w_flut = int(math.sin(df.wing_phase) * 4)
            painter.setBrush(QBrush(QColor(224, 242, 254, 220)))
            painter.setPen(QPen(QColor("#38BDF8"), 1))

            # Front Pair Wings
            painter.drawEllipse(-2, -14 + w_flut, 6, 12)
            painter.drawEllipse(-2, 2 - w_flut, 6, 12)

            # Rear Pair Wings
            painter.drawEllipse(-7, -12 - w_flut, 5, 10)
            painter.drawEllipse(-7, 2 + w_flut, 5, 10)

            painter.restore()



class FloatingPlantPopup(QWidget):
    """
    100% Transparent Frameless Desktop Character Popup.
    """
    dismissed = Signal()
    audio_finished_signal = Signal()

    def __init__(self, plant_state, audio_manager, parent=None):
        super().__init__(parent)
        self.plant_state = plant_state
        self.audio_manager = audio_manager

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Window |
            Qt.WindowSystemMenuHint
        )
        self.setWindowTitle("🌱 Plant Complainer")
        
        assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        icon_path = os.path.join(assets_dir, "plant_on.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        
        self.setFixedSize(650, 300)
        self._build_ui()

        # Instantiate Screen-Wide Flying Bees Overlay
        self.bees_overlay = ScreenBeesOverlay()
        self.bees_overlay.show()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.avatar = PlantAvatarWidget(self)
        main_layout.addWidget(self.avatar, 0, Qt.AlignBottom)

        self.speech_bubble = SpeechBubbleWidget(self)
        main_layout.addWidget(self.speech_bubble, 1, Qt.AlignTop)

    def _position_popup(self):
        import random
        from PySide6.QtCore import QPoint
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 40
        min_x = screen.left() + margin
        max_x = max(min_x, screen.right() - self.width() - margin)
        min_y = screen.top() + margin
        max_y = max(min_y, screen.bottom() - self.height() - margin)

        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        self.move(x, y)

        if hasattr(self, 'bees_overlay') and self.bees_overlay:
            self.bees_overlay.update_plant_position(QPoint(x, y))
            self.bees_overlay.show()



    def show_complaint(self, complaint_obj, audio_path=None, context_name="System"):
        text = complaint_obj.get("text", "Edaa...")
        irr = complaint_obj.get("irritation", "cute")

        self.avatar.set_expression(irr)
        self.speech_bubble.set_content(text, irr)

        self._position_popup()
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
        self.raise_()
        
        if audio_path and os.path.exists(audio_path):
            self.audio_manager.play_audio(audio_path, callback=self._on_audio_finished)

    def _on_audio_finished(self):
        self.audio_finished_signal.emit()

    def contextMenuEvent(self, event):
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        
        menu = QMenu(self)
        menu.setStyleSheet("background-color: #064E3B; color: white; padding: 5px;")
        
        sing_action = QAction("🎵 Sing a Malayalam Song", self)
        sing_action.triggered.connect(self._trigger_sing)
        menu.addAction(sing_action)
        menu.addSeparator()

        quit_action = QAction("🚪 Quit Plant Complainer", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        
        menu.exec_(event.globalPos())

    def _trigger_sing(self):
        if hasattr(QApplication.instance(), 'complaint_loop') and QApplication.instance().complaint_loop:
            QApplication.instance().complaint_loop.sing_song()

