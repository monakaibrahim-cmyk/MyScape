from dataclasses import dataclass
from typing import Optional
from Entity.Entity import EntityManager, Stats

@dataclass
class Experience:
    current: int = 0
    required: int = 0

class ExperienceSystem:
    def __init__(self, Manager: EntityManager):
        self.manager = Manager

    def calculate(self, required: int) -> int:
        return int(required * 0.5)

    def add(self, uid: int, amount: int):
        experience = self.manager.get(uid, Experience)
        stats = self.manager.get(uid, Stats)

        if not experience and stats:
            return

        experience.current += amount

        while experience.current >= experience.required:
            experience.current -= experience.required
            stats.level += 1
            stats.max_health += 20.0
            stats.current_health = stats.max_health

            experience.required = self.calculate(experience.required)
        