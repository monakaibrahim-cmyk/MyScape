from dataclasses import dataclass
from typing import Dict, Type, TypeVar, Optional, Any

C = TypeVar('C')

@dataclass
class Identity:
    name: str = "UNKNOWN"
    model: str = ""

@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

@dataclass
class Stats:
    current_health: float = 0.0
    max_health: float = 0.0
    current_mana: float = 0.0
    max_mana: float = 0.0
    movementspeed: int = 0
    attackspeed: float = 0.0
    level: int = 0
    stamina: float = 0.0
    strength: float = 0.0
    dexterity: float = 0.0
    agility: float = 0.0
    intelligence: float = 0.0

class EntityManager:
    def __init__(self) -> None:
        self.id: int = 0
        self.entities: Dict[int, Dict[Type[Any], Any]] = {}

    def create(self) -> int:
        id = self.id
        self.entities[id] = {}
        self.id += 1
        
        return id

    def add(self, id: int, component: Any) -> None:
        if id in self.entities:
            component_type = type(component)
            self.entities[id][component_type] = component
    
    def get(self, id: int, component_type: Type[C]) -> Optional[C]:
        entity = self.entities.get(id, {})

        return entity.get(component_type)

    def query(self, component_type: Type[C]) -> Dict[int, C]:
        return {
            id: components[component_type]
            for id, components in self.entities.items()
            if component_type in components
        }

