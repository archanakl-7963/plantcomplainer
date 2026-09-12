import sys
import time

try:
    import win32gui
    import win32process
    import psutil
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

class ContextDetector:
    def __init__(self):
        self.last_input_time = time.time()

    def get_idle_seconds(self):
        """Get system idle time on Windows."""
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

    def detect_context(self):
        """
        Classifies active computer window context into:
        coding, browser, youtube, presentation, document, file_manager, game, idle, other
        """
        idle_sec = self.get_idle_seconds()
        if idle_sec > 180:  # 3 minutes idle
            return "idle", "System Idle"

        if not HAS_WIN32 or sys.platform != "win32":
            return "other", "System Active"

        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return "other", "Unknown Window"

            title = win32gui.GetWindowText(hwnd).lower()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            process_name = ""
            try:
                proc = psutil.Process(pid)
                process_name = proc.name().lower()
            except Exception:
                pass

            # 1. Coding context
            coding_apps = ["code.exe", "devenv.exe", "pycharm64.exe", "idea64.exe", "clion64.exe", "sublime_text.exe", "notepad++.exe", "nvim.exe", "atom.exe", "cursor.exe"]
            coding_keywords = ["visual studio code", "pycharm", "intellij", "sublime text", "workspace", ".py", ".cpp", ".js", ".ts", ".html", "git", "cursor", "replit"]
            if any(app in process_name for app in coding_apps) or any(kw in title for kw in coding_keywords):
                return "coding", f"Coding ({process_name})"

            # 2. YouTube / Video context
            video_apps = ["vlc.exe", "mpc-hc.exe", "kmplayer.exe", "potplayer.exe", "wmplayer.exe", "netflix.exe"]
            video_keywords = ["youtube", "netflix", "prime video", "hotstar", "twitch", "vlc", "movie", "video", ".mp4", ".mkv", ".avi"]
            if any(app in process_name for app in video_apps) or any(kw in title for kw in video_keywords):
                return "youtube", "Watching Video/YouTube"

            # 3. Document / Reading context
            doc_apps = ["winword.exe", "excel.exe", "acrord32.exe", "acrobat.exe", "foxitreader.exe", "sumatrapdf.exe", "wps.exe", "wordpad.exe", "notepad.exe"]
            doc_keywords = ["pdf", "docx", "doc", "xlsx", "txt", "reader", "reading", "document", "powerpnt", "slides", "presentation", "sheet", "note"]
            if any(app in process_name for app in doc_apps) or any(kw in title for kw in doc_keywords):
                return "document", "Reading Document/Files"

            # 4. Browser context
            browser_apps = ["chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe", "vivaldi.exe"]
            if any(app in process_name for app in browser_apps):
                return "browser", f"Web Browsing ({process_name})"

            # 5. Presentation
            if "powerpnt.exe" in process_name or "slides" in title or "presentation" in title:
                return "presentation", "Presentation Mode"

            # 6. File Manager
            if "explorer.exe" in process_name:
                return "file_manager", "File Explorer"

            # 7. Games
            game_keywords = ["steam", "epicgames", "game", "unity", "unreal", "minecraft", "roblox"]
            if any(kw in title for kw in game_keywords):
                return "game", "Gaming"

            return "other", title if title else process_name
        except Exception as e:
            return "other", f"Active ({e})"
