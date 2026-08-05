from ursina import *
from ursina.prefabs.health_bar import HealthBar 
from Entity.Entity import Position, Stats, Identity
from Systems.Systems import play_animation
from enum import Enum
from direct.actor.Actor import Actor
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
        self.visual = None

    def spawn(self, x, z, flag: EntityFlag):
        start = Vec3(x, 100, z)
        hit = raycast(start, direction=(0, -1, 0), distance=200)
        
        offset = 1.5
        y = (hit.world_point.y + 0.1 if hit.hit else 0.0) + offset

        entry = self.ecs.create()
        self.ecs.add(entry, Position(x=x, y=y, z=z))

        if flag == EntityFlag.MOB:
            self.ecs.add(entry, Stats(current_health=50.0, max_health=50.0, movementspeed=5, level=5))

            stats = self.ecs.get(entry, Stats)

            self.visual = Entity(
                model='quad',
                texture='white_cube',
                position=(x, 0.5, z),
                collider='box',
                scale=5,
                billboard=True,
                double_sided=True
            )

            self.visual.base_scale = 5

            self.visual.assets = {
                "idle": "assets/entity/Goblin/gif/spr_idle.gif",
                "hurt": "assets/entity/Goblin/gif/spr_hurt.gif",
            }

            play_animation(
                self.visual,
                self.visual.assets["idle"]
            )

            health = HealthBar(
                max_value=stats.max_health,
                value=stats.current_health,
                parent=self.visual,
                scale=(1.2, 0.2),
                color=color.black,
                bar_color=color.green,
                roundness=0,
                show_text=True,
                origin=(-0.5, 0),
                y=0.8,
                billboard=True,
                text_size=.7
            )

            Level = Text(
                parent=self.visual,
                text=f"Lv. {stats.level}",
                position=(0, 0.2, 0),
                scale=2,
                origin=(0, 0),
                billboard=True,
                color=color.yellow
            )

            health.text_entity.origin = (0, 0)
            health.text_entity.z = -0.1
            health.text_entity.color = color.black
            
            self.active_entities[self.visual] = {
                'id': entry,
                'type': EntityFlag.MOB,
                'health': health
            }

        elif flag == EntityFlag.NPC:
            self.visual = Entity(model='cube', color=color.green, position=(x, 0.5, z), collider='box')
            name_text = Text(parent=self.visual, text='Villager', y=0.8, scale=5, color=color.yellow, origin=(0,0), billboard=True)

            print('NPC Spawned')

            self.active_entities[self.visual] = {
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

