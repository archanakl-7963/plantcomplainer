import time

class ContextAnalyzer:
    """
    Context Analysis Engine that combines:
    ACTIVITY + DURATION + PLANT NEED + MOOD + TIME + RECENT INTERACTION
    into a unified context object for complaint and gossip generation.
    """
    @staticmethod
    def get_time_of_day():
        hour = time.localtime().tm_hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "late_night"

    @staticmethod
    def analyze(plant_state, activity_detector):
        activity_name, activity_desc = activity_detector.detectActivity()
        duration_mins = activity_detector.getActiveDuration()
        time_of_day = ContextAnalyzer.get_time_of_day()
        neglect_duration_sec = time.time() - plant_state.last_interaction

        # Primary plant need
        primary_need = "none"
        if plant_state.water_level < 10:
            primary_need = "critical_water"
        elif plant_state.water_level < 30:
            primary_need = "thirsty"
        elif plant_state.sunlight_level < 25:
            primary_need = "sunlight"
        elif plant_state.attention_level < 25 or neglect_duration_sec > 1800:
            primary_need = "neglected"
        elif plant_state.water_level > 90:
            primary_need = "overwatered"

        return {
            "activity": activity_name,
            "activity_desc": activity_desc,
            "duration_mins": duration_mins,
            "primary_need": primary_need,
            "mood": plant_state.mood,
            "time_of_day": time_of_day,
            "neglect_duration_sec": neglect_duration_sec,
            "water_level": plant_state.water_level,
            "sunlight_level": plant_state.sunlight_level,
            "health": plant_state.health,
            "happiness": plant_state.happiness
        }
