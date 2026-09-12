from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QPainterPath

class PlantView(QWidget):
    """
    Custom-drawn interactive Plant Avatar displaying state-based visual reactions:
    - Healthy
    - Happy
    - Thirsty
    - Sad
    - Wilting
    - Excited
    - Annoyed
    - Dramatic
    Features gentle bobbing and talk animation while speech plays.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 220)
        self.expression = "happy"
        self.is_talking = False
        self.animation_step = 0
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_anim_tick)
        self.anim_timer.start(150)

    def set_expression(self, expr):
        self.expression = expr.lower() if expr else "happy"
        self.update()

    def set_talking(self, talking_bool):
        self.is_talking = talking_bool
        self.update()

    def _on_anim_tick(self):
        self.animation_step = (self.animation_step + 1) % 10
        if self.is_talking or self.expression == "excited":
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.scale(1.35, 1.35)

        # Gentle bobbing offset when talking or excited
        bounce_offset = 0
        if self.is_talking:
            bounce_offset = -3 if (self.animation_step % 2 == 0) else 0
        elif self.expression == "excited":
            bounce_offset = -4 if (self.animation_step % 2 == 0) else 1

        # 1. Terracotta Pot
        pot_brush = QBrush(QColor("#D97706"))
        painter.setBrush(pot_brush)
        painter.setPen(QPen(QColor("#78350F"), 3))
        
        pot_path = QPainterPath()
        pot_path.moveTo(35, 100 + bounce_offset)
        pot_path.lineTo(125, 100 + bounce_offset)
        pot_path.lineTo(110, 150 + bounce_offset)
        pot_path.lineTo(50, 150 + bounce_offset)
        pot_path.closeSubpath()
        painter.drawPath(pot_path)

        # 2. Soil
        painter.setBrush(QBrush(QColor("#451A03")))
        painter.drawEllipse(32, 92 + bounce_offset, 96, 18)

        # 3. Stem
        drooping = self.expression in ["thirsty", "sad", "wilting", "dramatic"]
        stem_color = QColor("#CA8A04") if drooping else QColor("#16A34A")
        painter.setPen(QPen(stem_color, 7))

        if drooping:
            painter.drawArc(65, 38 + bounce_offset, 60, 60, 0 * 16, 180 * 16)
        else:
            painter.drawLine(80, 95 + bounce_offset, 80, 48 + bounce_offset)

        # 4. Leaves
        leaf_color = QColor("#EAB308") if drooping else QColor("#22C55E")
        painter.setBrush(QBrush(leaf_color))
        painter.setPen(QPen(QColor("#15803D"), 2))
        
        if self.expression == "excited":
            painter.drawEllipse(38, 52 + bounce_offset, 40, 22) # Raised leaves
            painter.drawEllipse(82, 52 + bounce_offset, 40, 22)
        else:
            painter.drawEllipse(40, 60 + bounce_offset, 38, 20)
            painter.drawEllipse(82, 60 + bounce_offset, 38, 20)

        # 5. Plant Flower / Head
        if self.expression == "angry":
            head_color = QColor("#EF4444")
        elif self.expression in ["happy", "excited"]:
            head_color = QColor("#F59E0B")
        elif self.expression in ["sad", "wilting", "dramatic"]:
            head_color = QColor("#38BDF8")
        else:
            head_color = QColor("#4ADE80")

        # Petals for Happy/Excited
        if self.expression in ["happy", "excited"]:
            painter.setBrush(QBrush(QColor("#FBBF24")))
            painter.setPen(QPen(QColor("#D97706"), 1.5))
            painter.drawEllipse(44, 20 + bounce_offset, 16, 16)
            painter.drawEllipse(100, 20 + bounce_offset, 16, 16)
            painter.drawEllipse(72, 4 + bounce_offset, 16, 16)
            painter.drawEllipse(72, 44 + bounce_offset, 16, 16)

        painter.setBrush(QBrush(head_color))
        painter.setPen(QPen(QColor("#166534"), 3))
        painter.drawEllipse(56, 18 + bounce_offset, 48, 48)

        # 6. Face Expression (Eyes & Mouth)
        painter.setPen(QPen(QColor("#064E3B") if self.expression != "angry" else QColor("#7F1D1D"), 3.5))
        painter.setBrush(QBrush(QColor("#064E3B")))

        if self.expression in ["cute", "happy", "excited"]:
            painter.drawArc(65, 28 + bounce_offset, 10, 10, 0, 180 * 16)
            painter.drawArc(85, 28 + bounce_offset, 10, 10, 0, 180 * 16)
            if self.is_talking:
                # Talking open mouth animation
                mouth_size = 12 if (self.animation_step % 2 == 0) else 6
                painter.drawEllipse(73, 40 + bounce_offset, 14, mouth_size)
            else:
                painter.drawArc(71, 40 + bounce_offset, 18, 14, 180 * 16, 180 * 16)

        elif self.expression == "annoyed":
            painter.drawLine(64, 32 + bounce_offset, 74, 32 + bounce_offset)
            painter.drawLine(86, 32 + bounce_offset, 96, 32 + bounce_offset)
            painter.drawLine(71, 46 + bounce_offset, 89, 46 + bounce_offset)

        elif self.expression in ["dramatic", "sad", "thirsty", "wilting"]:
            painter.drawArc(65, 33 + bounce_offset, 9, 9, 0, 180 * 16)
            painter.drawArc(85, 33 + bounce_offset, 9, 9, 0, 180 * 16)
            painter.setBrush(QBrush(QColor("#38BDF8")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(94, 38 + bounce_offset, 7, 12) # Tear drops
            painter.drawEllipse(59, 38 + bounce_offset, 7, 12)
            painter.setPen(QPen(QColor("#064E3B"), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(73, 42 + bounce_offset, 14, 14)
