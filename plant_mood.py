class PlantMood:
    HAPPY = "HAPPY"
    NORMAL = "NORMAL"
    THIRSTY = "THIRSTY"
    SAD = "SAD"
    ANNOYED = "ANNOYED"
    DRAMATIC = "DRAMATIC"
    JEALOUS = "JEALOUS"
    EXCITED = "EXCITED"
    LONELY = "LONELY"
    SLEEPY = "SLEEPY"

    @staticmethod
    def calculate_mood(water_level, sunlight_level, health, happiness, attention_level, neglect_seconds=0):
        """
        Dynamically calculates plant mood based on current stats and neglect duration.
        """
        if water_level < 20:
            if neglect_seconds > 1800:
                return PlantMood.DRAMATIC
            return PlantMood.THIRSTY

        if sunlight_level < 20:
            return PlantMood.SAD

        if attention_level < 20 or neglect_seconds > 3600:
            return PlantMood.LONELY

        if water_level > 90:
            return PlantMood.ANNOYED

        if happiness > 80 and health > 80:
            return PlantMood.HAPPY

        if happiness > 90:
            return PlantMood.EXCITED

        if neglect_seconds > 900:
            return PlantMood.JEALOUS

        return PlantMood.NORMAL
