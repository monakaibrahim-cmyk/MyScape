from dataclasses import dataclass
from typing import Optional
from Entity.Entity import EntityManager, Position, Stats, Identity
from Systems.Experience import Experience

@dataclass
class PlayerInfo:
    name: str = "Player"
    gold: int = 0

class PlayerHandle:
    def __init__(self, uid: int, Manager: EntityManager):
        self.id = uid
        self.manager = Manager
        self.visual = None
        
    @property
    def info(self) -> Optional[PlayerInfo]:
        return self.manager.get(self.id, PlayerInfo)

    @property
    def stats(self) -> Optional[Stats]:
        return self.manager.get(self.id, Stats)

    @property
    def experience(self) -> Optional[Experience]:
        return self.manager.get(self.id, Experience)

    @property
    def position(self) -> Optional[Position]:
        return self.manager.get(self.id, Position)

class PlayerManager:
    def __init__(self, Manager: EntityManager) -> None:
        self.manager = Manager
        self.entity: Optional[PlayerHandle] = None

    def spawn(self, x: float = 0.0, y: float = 0.5, z: float = 0.0) -> None:
        uid = self.manager.create()

        self.manager.add(uid, Position(x=x, y=y, z=z))

        self.manager.add(uid, Identity(
            name="Player",
            model='assets/player/spr_idle.gif'
        ))
        
        self.manager.add(uid, PlayerInfo(
            name="Player",
            gold=0
        ))
        
        self.manager.add(uid, Stats(
            current_health=100.0,
            max_health=100.0,
            current_mana=50.0,
            max_mana=50.0,
            movementspeed=5,
            attackspeed=1.0,
            level=1
        ))

        self.manager.add(uid, Experience(
            current=0,
            required=100
        ))

        self.entity = PlayerHandle(uid, self.manager)


