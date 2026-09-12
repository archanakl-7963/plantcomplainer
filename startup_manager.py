import sys
import os

if sys.platform == "win32":
    import winreg
    HAS_WINREG = True
else:
    HAS_WINREG = False

REG_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "PlantComplainer"

class StartupManager:
    @staticmethod
    def set_startup(enable=True):
        if not HAS_WINREG:
            return False

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_PATH, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                main_py = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
                pythonw = sys.executable.replace("python.exe", "pythonw.exe")
                cmd = f'"{pythonw}" "{main_py}"'
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"[StartupManager] Error setting registry: {e}")
            return False

    @staticmethod
    def is_startup_enabled():
        if not HAS_WINREG:
            return False
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_PATH, 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True if val else False
        except Exception:
            return False
