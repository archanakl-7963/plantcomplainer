import time
from .context_analyzer import ContextAnalyzer
from .gossip_generator import GossipGenerator

class PriorityLevel:
    CRITICAL = 4   # water < 10, health < 15
    HIGH = 3       # water < 25, sunlight < 20, long neglect
    MEDIUM = 2     # long gaming, long coding, studying, youtube
    LOW = 1        # random gossip, casual observations

class ComplaintEngine:
    """
    Priority & Cooldown Manager for Plant Complaints.
    Enforces CRITICAL > HIGH > MEDIUM > LOW, prevents spamming,
    and manages complaint interval / cooldowns.
    """
    def __init__(self):
        self.last_complaint_time = 0
        self.last_complaint_text = ""
        self.history = []

    def get_priority_level(self, context):
        need = context.get("primary_need", "none")
        water = context.get("water_level", 100)
        health = context.get("health", 100)
        duration = context.get("duration_mins", 0)

        if water < 10 or health < 15 or need == "critical_water":
            return PriorityLevel.CRITICAL

        if water < 25 or context.get("sunlight_level", 100) < 20 or need == "neglected":
            return PriorityLevel.HIGH

        if duration > 30 and context.get("activity") in ["gaming", "coding", "youtube", "document"]:
            return PriorityLevel.MEDIUM

        return PriorityLevel.LOW

    def should_trigger(self, context, plant_state, force=False):
        if force:
            return True

        if not plant_state.auto_complaints:
            return False

        now = time.time()
        priority = self.get_priority_level(context)

        # Critical alerts can bypass normal cooldown
        if priority == PriorityLevel.CRITICAL:
            if now - self.last_complaint_time >= 5:  # 5 sec emergency buffer
                return True

        cooldown_sec = plant_state.complaint_interval_sec
        if now - self.last_complaint_time >= cooldown_sec:
            return True

        return False

    def select_complaint(self, plant_state, activity_detector, force=False):
        """
        Generates and returns the best matching complaint object:
        { "text": str, "priority": int, "context": str, "mood": str }
        """
        context = ContextAnalyzer.analyze(plant_state, activity_detector)

        if not self.should_trigger(context, plant_state, force=force):
            return None

        priority = self.get_priority_level(context)
        text = GossipGenerator.generate(context)

        # Avoid immediate exact repetition
        attempts = 0
        while text == self.last_complaint_text and attempts < 5:
            text = GossipGenerator.generate(context)
            attempts += 1

        self.last_complaint_time = time.time()
        self.last_complaint_text = text
        self.history.append(text)
        if len(self.history) > 20:
            self.history.pop(0)

        return {
            "text": text,
            "priority": priority,
            "context": context.get("activity_desc", "System"),
            "mood": plant_state.mood
        }
