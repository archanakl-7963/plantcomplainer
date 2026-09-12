import time
from .plant_mood import PlantMood

class PlantState:
    """
    Virtual State System tracking plant needs, health, happiness, and dynamic mood.
    """
    def __init__(self):
        self.water_level = 75.0          # 0-100
        self.sunlight_level = 70.0       # 0-100
        self.health = 100.0              # 0-100
        self.happiness = 85.0           # 0-100
        self.attention_level = 80.0       # 0-100
        
        self.last_watered = time.time()
        self.last_sunlight = time.time()
        self.last_interaction = time.time()
        self.last_complaint_time = 0
        
        self.active_context = "idle"
        self.active_context_duration = 0
        
        # User settings
        self.enable_voice = True
        self.enable_context_detection = True
        self.enable_random_gossip = True
        self.auto_complaints = True
        self.volume = 100
        self.complaint_interval_sec = 15  # Default 15 seconds
        self.dramatic_level = 5           # 1-10 scale
        self.sarcasm_level = 5            # 1-10 scale
        self.gossip_frequency = 5         # 1-10 scale
        self.active_voice_profile = "default"

    @property
    def mood(self):
        neglect_sec = time.time() - self.last_interaction
        return PlantMood.calculate_mood(
            self.water_level,
            self.sunlight_level,
            self.health,
            self.happiness,
            self.attention_level,
            neglect_sec
        )

    def update_decay(self, seconds_elapsed=15.0):
        """Simulates plant needs decay over time."""
        # Water decay: ~5% per 10 minutes -> 0.125% per 15 sec
        water_decay = (seconds_elapsed / 60.0) * 0.5
        self.water_level = max(0.0, self.water_level - water_decay)
        
        # Sunlight decay: ~4% per 10 minutes -> 0.10% per 15 sec
        sun_decay = (seconds_elapsed / 60.0) * 0.4
        self.sunlight_level = max(0.0, self.sunlight_level - sun_decay)
        
        # Attention decay
        att_decay = (seconds_elapsed / 60.0) * 0.6
        self.attention_level = max(0.0, self.attention_level - att_decay)

        # Health & Happiness updates
        if self.water_level < 20 or self.sunlight_level < 20:
            self.health = max(0.0, self.health - 0.2)
            self.happiness = max(0.0, self.happiness - 0.3)
        else:
            self.health = min(100.0, self.health + 0.1)
            self.happiness = min(100.0, self.happiness + 0.1)

    def water(self):
        """Action: User waters the plant."""
        self.water_level = min(100.0, self.water_level + 45.0)
        self.happiness = min(100.0, self.happiness + 20.0)
        self.health = min(100.0, self.health + 10.0)
        self.last_watered = time.time()
        self.last_interaction = time.time()

    def give_sunlight(self):
        """Action: User gives sunlight to the plant."""
        self.sunlight_level = min(100.0, self.sunlight_level + 45.0)
        self.happiness = min(100.0, self.happiness + 15.0)
        self.last_sunlight = time.time()
        self.last_interaction = time.time()

    def interact(self):
        """Action: User interacts/talks with the plant."""
        self.attention_level = min(100.0, self.attention_level + 30.0)
        self.happiness = min(100.0, self.happiness + 10.0)
        self.last_interaction = time.time()

    def to_dict(self):
        return {
            "water_level": self.water_level,
            "sunlight_level": self.sunlight_level,
            "health": self.health,
            "happiness": self.happiness,
            "attention_level": self.attention_level,
            "last_watered": self.last_watered,
            "last_sunlight": self.last_sunlight,
            "last_interaction": self.last_interaction,
            "enable_voice": self.enable_voice,
            "enable_context_detection": self.enable_context_detection,
            "enable_random_gossip": self.enable_random_gossip,
            "auto_complaints": self.auto_complaints,
            "complaint_interval_sec": self.complaint_interval_sec,
            "dramatic_level": self.dramatic_level,
            "sarcasm_level": self.sarcasm_level,
            "gossip_frequency": self.gossip_frequency
        }

    def from_dict(self, data):
        if not data:
            return
        self.water_level = data.get("water_level", self.water_level)
        self.sunlight_level = data.get("sunlight_level", self.sunlight_level)
        self.health = data.get("health", self.health)
        self.happiness = data.get("happiness", self.happiness)
        self.attention_level = data.get("attention_level", self.attention_level)
        self.last_watered = data.get("last_watered", self.last_watered)
        self.last_sunlight = data.get("last_sunlight", self.last_sunlight)
        self.last_interaction = data.get("last_interaction", self.last_interaction)
        self.enable_voice = data.get("enable_voice", self.enable_voice)
        self.enable_context_detection = data.get("enable_context_detection", self.enable_context_detection)
        self.enable_random_gossip = data.get("enable_random_gossip", self.enable_random_gossip)
        self.auto_complaints = data.get("auto_complaints", self.auto_complaints)
        self.complaint_interval_sec = data.get("complaint_interval_sec", self.complaint_interval_sec)
        self.dramatic_level = data.get("dramatic_level", self.dramatic_level)
        self.sarcasm_level = data.get("sarcasm_level", self.sarcasm_level)
        self.gossip_frequency = data.get("gossip_frequency", self.gossip_frequency)
