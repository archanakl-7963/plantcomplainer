import sys
import os

# Add root directory to sys.path and change working directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from services.plant_state import PlantState
from services.complaint_engine import ComplaintEngine
from services.context_detector import ContextDetector
from services.voice_engine import VoiceEngine
from services.audio_manager import AudioManager
from ui.main_window import MainWindow
from ui.tray import PlantTrayIcon
from ui.first_run import FirstRunWizardDialog

def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("Plant Complainer")
    
    icon_path = os.path.normpath(os.path.join(ROOT_DIR, "assets", "plant_on.png"))
    if os.path.exists(icon_path):
        from PySide6.QtGui import QIcon
        app.setWindowIcon(QIcon(icon_path))
        
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray

    # Initialize Core Services
    plant_state = PlantState()
    complaint_engine = ComplaintEngine()
    context_detector = ContextDetector()
    voice_engine = VoiceEngine()
    audio_manager = AudioManager()

    # Check for First Run Experience
    voices_default_dir = os.path.join(ROOT_DIR, "voices", "default")
    has_samples = os.path.exists(voices_default_dir) and len(os.listdir(voices_default_dir)) > 0

    if not has_samples:
        wizard = FirstRunWizardDialog(voice_engine, audio_manager, plant_state)
        wizard.exec()

    from ui.popup import FloatingPlantPopup
    from services.complaint_loop import ComplaintLoop
    
    # Create the persistent floating plant popup
    popup = FloatingPlantPopup(plant_state, audio_manager)
    _ = popup.winId() # Force Win32 native HWND creation
    
    # Create System Tray Icon (located right next to Wi-Fi and Bluetooth)
    from ui.tray import PlantTrayIcon
    tray = PlantTrayIcon(plant_state, popup)
    tray.show()
    
    # Create 1-Click ON/OFF Control Switch Bar
    from ui.control_bar import PlantControlBar
    control_bar = PlantControlBar(plant_state, popup, tray=tray)
    control_bar.show()
    
    # Start the continuous complaint loop
    complaint_loop = ComplaintLoop(
        plant_state, 
        complaint_engine, 
        context_detector, 
        voice_engine, 
        audio_manager, 
        popup,
        tray=tray
    )

    # Attach to app object to prevent garbage collection
    app.popup = popup
    app.tray = tray
    app.control_bar = control_bar
    app.complaint_loop = complaint_loop

    sys.exit(app.exec())



if __name__ == "__main__":
    main()


