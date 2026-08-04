from ursina import *
from Entity import Position, Stats
from enum import Enum
import random

class EntityFlag(Enum):
    NPC = 1
    MOB = 2
    BOSS = 3
    UNIQUE = 4
    WORLD_BOSS = 5

class SpawnerManager:
    def __init__(self, manager):
        self.ecs = manager
        self.active_entities = {}
        self.respawn_timer = 0.0
        self.respawn_delay = 3.0

    def spawn(self, x, z, flag: EntityFlag):
        entry = self.ecs.create_entity()
        self.ecs.add_component(entry, Position(x=x, y=0.5, z=z))

        if flag == EntityFlag.MOB:
            self.ecs.add_component(entry, Stats(health=50.0))
            visual = Entity(model='cube', color=color.red, position=(x, 0.5, z), collider='box')

            health_background = Entity(parent=visual, model='quad', color=color.dark_gray, scale=(1.2, 0.2), y=0.8, billboard=True)
            health_bar = Entity(parent=health_background, model='quad', color=color.green, scale=(1, 1), origin=(-0.5, 0), x=-0.5, z=-0.01)
            health_text = Text(parent=visual, text='50 / 50', y=0.8, z=-0.02, scale=3, color=color.dark_gray, origin=(0,0), billboard=True)

            print('Mob Spawned')
            
            self.active_entities[visual] = {
                'id': entry,
                'type': EntityFlag.MOB,
                'health_bar': health_bar,
                'health_text': health_text
            }

        elif flag == EntityFlag.NPC:
            visual = Entity(model='cube', color=color.green, position=(x, 0.5, z), collider='box')
            name_text = Text(parent=visual, text='Villager', y=0.8, scale=5, color=color.yellow, origin=(0,0), billboard=True)

            print('NPC Spawned')

            self.active_entities[visual] = {
                'id': entry,
                'type': EntityFlag.NPC
            }
        
    def auto(self, amount, cmin, cmax, flag: EntityFlag):
        for _ in range(amount):
            x = random.uniform(cmin, cmax)
            z = random.uniform(cmin, cmax)
        
            self.spawn(x, z, flag)

    def update(self):
        count = 0

        for entity, data in self.active_entities.items():
            if data['type'] == EntityFlag.MOB:
                count += 1

        if count == 0:
            self.respawn_timer += time.dt

            if self.respawn_timer >= self.respawn_delay:
                self.auto(amount=5, cmin=-10, cmax=10, flag=EntityFlag.MOB)
                self.respawn_timer = 0.0
        else:
            self.respawn_timer = 0.0

