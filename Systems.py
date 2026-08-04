from ursina import *
from Spawner import *
from Entity import *
from enum import Enum

class TaskFlag(Enum):
    WALK = 1
    RUN = 2
    ATTACK = 3
    GATHER = 4
    REST = 5
    HEAL = 6
    SLEEP = 7
    SIT = 8
    EAT = 9
    DRINK = 10
    TALK = 11

# debug
def add_entity_debug_marker(parent):
    """Attaches a 3D axis marker to an entity (Red=X, Green=Y, Blue=Z)."""
    Entity(parent=parent, model='sphere', color=color.white, scale=0.15)

    Entity(parent=parent, model='cube', color=color.red, scale=(1.5, 0.04, 0.04), position=(0.75, 0, 0))
    Entity(parent=parent, model='sphere', color=color.red, scale=(0.15, 0.35, 0.15), position=(1.5, 0, 0), rotation_z=-90)

    Entity(parent=parent, model='cube', color=color.green, scale=(0.04, 1.5, 0.04), position=(0, 0.75, 0))
    Entity(parent=parent, model='sphere', color=color.green, scale=(0.15, 0.35, 0.15), position=(0, 1.5, 0))

    Entity(parent=parent, model='cube', color=color.blue, scale=(0.04, 0.04, 1.5), position=(0, 0, 0.75))
    Entity(parent=parent, model='sphere', color=color.blue, scale=(0.15, 0.35, 0.15), position=(0, 0, 1.5), rotation_x=90)

def perform_task(scene, player_model, player_visual, flag: TaskFlag, entity = None, spawner = None, manager = None):
    """Handles Task to be performed"""

    if flag == TaskFlag.ATTACK:
        entity_data = spawner.active_entities[entity]
        id = entity_data['id']
        stats = manager.get_component(id, Stats)

        if stats and stats.health > 0:
            player_visual.look_at(entity)
            player_visual.rotation_x = 0
            player_visual.rotation_z = 0
            player_model.play('attack')

            stats.health -= 10
            entity.blink(color.white, duration=0.1)

            spawn_position = entity.position + Vec3(0, 1.5, -0.5)
            damage = Text(parent=scene, text='-10', position=spawn_position, origin=(0, 0), color=color.red, scale=25, billboard=True)
            damage.animate_y(damage.y + 2, duration=1)
            destroy(damage, delay=1)

            hp_bar = entity_data['health_bar']
            hp_text = entity_data['health_text']
            health_percentage = stats.health / 50.0
            hp_bar.scale_x = health_percentage

            if health_percentage <= 0.5:
                hp_bar.color = color.yellow
                hp_text.color = color.white

            if health_percentage <= 0.2:
                hp_bar.color = color.red
                hp_text.color = color.white

            hp_text.text = f'{int(stats.health)} / 50'

            if stats.health <= 0:
                destroy(entity)
                del spawner.active_entities[entity]


def handle_player_movement(visual, target, manager, id, dt, player_model):
    """Handles the math for walking to a clicked destination."""
    speed = manager.get_component(id, Speed)
    direction = target - visual.position

    if direction.length() > 0.1:
        direction = direction.normalized()
        visual.position += direction * speed.value * dt

        visual.look_at(target)
        visual.rotation_x = 0 
        visual.rotation_z = 0

        if player_model.getCurrentAnim() != 'run':
            player_model.loop('run')

        data = manager.get_component(id, Position)

        if data:
            data.x, data.y, data.z = visual.x, visual.y, visual.z

        return target
    else:
        if player_model.getCurrentAnim() != 'idle':
            player_model.loop('idle')

        return None

def update_player_ui(manager, id, health_text, health_bar):
    """Keeps the bottom screen UI synced with player data."""
    stats = manager.get_component(id, Stats)

    if stats:
        health_text.text = f'HP: {int(stats.health)}'
        health_bar.scale_x = stats.health / 100.0
