import sys
import time

try:
    import win32gui
    import win32process
    import psutil
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

class ActivityDetector:
    """
    Activity Detection Module exposing clean interfaces:
    - detectActivity()
    - getCurrentApplication()
    - getIdleTime()
    - getActiveDuration()
    """
    def __init__(self):
        self.last_activity = "idle"
        self.activity_start_time = time.time()
        self.manual_override_activity = None

    def set_manual_override(self, activity_name):
        """Allows test/developer panel to simulate specific activities."""
        self.manual_override_activity = activity_name
        self.activity_start_time = time.time()

    def clear_manual_override(self):
        self.manual_override_activity = None

    def getIdleTime(self):
        """Get system idle time in seconds on Windows."""
        if sys.platform == "win32":
            try:
                import ctypes
                class LASTINPUTINFO(ctypes.Structure):
                    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]
                lii = LASTINPUTINFO()
                lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
                if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                    return millis / 1000.0
            except Exception:
                pass
        return 0.0

    def getCurrentApplication(self):
        """Returns the active window title and process name."""
        if not HAS_WIN32 or sys.platform != "win32":
            return "Active", "System"

        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return "Unknown Window", "system"

            title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process_name = ""
            try:
                proc = psutil.Process(pid)
                process_name = proc.name().lower()
            except Exception:
                pass
            return title, process_name
        except Exception:
            return "Active Window", "system"

    def detectActivity(self):
        """
        Classifies active computer window context into:
        coding, document, gaming, youtube, browser, presentation, file_manager, idle, other
        """
        if self.manual_override_activity:
            return self.manual_override_activity, f"Simulated {self.manual_override_activity.capitalize()}"

        idle_sec = self.getIdleTime()
        if idle_sec > 180:  # 3 minutes idle
            current_act = "idle"
            desc = "System Idle"
            self._track_duration(current_act)
            return current_act, desc

        title, process_name = self.getCurrentApplication()
        title_lower = title.lower()

        # 1. Coding / Programming
        coding_apps = ["code.exe", "devenv.exe", "pycharm64.exe", "idea64.exe", "clion64.exe", "sublime_text.exe", "notepad++.exe", "nvim.exe", "atom.exe", "cursor.exe"]
        coding_keywords = ["visual studio code", "pycharm", "intellij", "sublime text", "workspace", ".py", ".cpp", ".js", ".ts", ".html", "git", "cursor", "replit"]
        if any(app in process_name for app in coding_apps) or any(kw in title_lower for kw in coding_keywords):
            current_act = "coding"
            desc = f"Coding ({process_name if process_name else 'IDE'})"
            self._track_duration(current_act)
            return current_act, desc

        # 2. YouTube / Video watching
        video_apps = ["vlc.exe", "mpc-hc.exe", "kmplayer.exe", "potplayer.exe", "wmplayer.exe", "netflix.exe"]
        video_keywords = ["youtube", "netflix", "prime video", "hotstar", "twitch", "vlc", "movie", "video", ".mp4", ".mkv", ".avi"]
        if any(app in process_name for app in video_apps) or any(kw in title_lower for kw in video_keywords):
            current_act = "youtube"
            desc = "Watching Video / YouTube"
            self._track_duration(current_act)
            return current_act, desc

        # 3. Studying / Document Reading
        doc_apps = ["winword.exe", "excel.exe", "acrord32.exe", "acrobat.exe", "foxitreader.exe", "sumatrapdf.exe", "wps.exe", "wordpad.exe", "notepad.exe"]
        doc_keywords = ["pdf", "docx", "doc", "xlsx", "txt", "reader", "reading", "document", "powerpnt", "slides", "presentation", "sheet", "note"]
        if any(app in process_name for app in doc_apps) or any(kw in title_lower for kw in doc_keywords):
            current_act = "document"
            desc = "Studying / Reading Document"
            self._track_duration(current_act)
            return current_act, desc

        # 4. Gaming
        game_apps = ["steam.exe", "epicgameslauncher.exe", "unity.exe", "unreal.exe"]
        game_keywords = ["steam", "epic games", "game", "unity", "unreal", "minecraft", "roblox", "gta", "valorant", "league of legends"]
        if any(app in process_name for app in game_apps) or any(kw in title_lower for kw in game_keywords):
            current_act = "game"
            desc = "Gaming"
            self._track_duration(current_act)
            return current_act, desc

        # 5. Browsing
        browser_apps = ["chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe", "vivaldi.exe"]
        if any(app in process_name for app in browser_apps):
            current_act = "browser"
            desc = f"Web Browsing ({process_name})"
            self._track_duration(current_act)
            return current_act, desc

        # 6. File Manager
        if "explorer.exe" in process_name:
            current_act = "file_manager"
            desc = "File Explorer"
            self._track_duration(current_act)
            return current_act, desc

        current_act = "other"
        desc = title if title else (process_name if process_name else "Active")
        self._track_duration(current_act)
        return current_act, desc

    def _track_duration(self, new_activity):
        if new_activity != self.last_activity:
            self.last_activity = new_activity
            self.activity_start_time = time.time()

    def getActiveDuration(self):
        """Returns duration of current activity in minutes."""
        return max(1, int((time.time() - self.activity_start_time) / 60.0))
