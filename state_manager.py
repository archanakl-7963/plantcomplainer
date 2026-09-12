import os
import json

STATE_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "plant_state.json"))
HISTORY_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "history.json"))

class StateManager:
    """
    Handles local JSON persistence for plant state, interaction history, and settings.
    """
    def __init__(self, file_path=None):
        self.file_path = file_path or STATE_FILE

    def save_state(self, plant_state):
        try:
            target = self.file_path if hasattr(self, 'file_path') else STATE_FILE
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                json.dump(plant_state.to_dict(), f, indent=2)
        except Exception as e:
            print(f"[StateManager] Save state error: {e}")

    def load_state(self, plant_state=None):
        if plant_state is None:
            from plant.plant_state import PlantState
            plant_state = PlantState()

        target = self.file_path if hasattr(self, 'file_path') else STATE_FILE
        if os.path.exists(target):
            try:
                with open(target, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    plant_state.from_dict(data)
            except Exception as e:
                print(f"[StateManager] Load state error: {e}")
        return plant_state

    @staticmethod
    def add_history_entry(complaint_text, context_name="System", mood="NORMAL"):
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            history = StateManager.get_history()
            entry = {
                "timestamp": os.popen('time /t').read().strip() if os.name == 'nt' else "Now",
                "text": complaint_text,
                "context": context_name,
                "mood": mood
            }
            history.insert(0, entry)
            history = history[:50] # Keep last 50 entries
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[StateManager] Add history error: {e}")

    @staticmethod
    def get_history():
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

