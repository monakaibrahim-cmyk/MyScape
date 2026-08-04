from dataclasses import dataclass
from typing import Dict, Type, TypeVar, Optional, Any

C = TypeVar('C')

@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

@dataclass
class Speed:
    value: int = 5

@dataclass
class Stats:
    health: float = 100.0
    mana: float = 50.0
    stamina: float = 50.0
    strength: float = 15.0
    dexterity: float = 15.0
    agility: float = 15.0
    intelligence: float = 15.0

class EntityManager:
    def __init__(self) -> None:
        self.id: int = 0
        self.entities: Dict[int, Dict[Type[Any], Any]] = {}

    def create_entity(self) -> int:
        id = self.id
        self.entities[id] = {}
        self.id += 1
        
        return id

    def add_component(self, id: int, component: Any) -> None:
        if id in self.entities:
            component_type = type(component)
            self.entities[id][component_type] = component
    
    def get_component(self, id: int, component_type: Type[C]) -> Optional[C]:
        entity = self.entities.get(id, {})

        return entity.get(component_type)

    def query_by_component(self, component_type: Type[C]) -> Dict[int, C]:
        return {
            id: components[component_type]
            for id, components in self.entities.items()
            if component_type in components
        }

