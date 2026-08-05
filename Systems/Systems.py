from ursina import *
from Entity.Spawner import *
from Entity.Entity import *
from Entity.Player import *
from Systems.Experience import ExperienceSystem
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

_animation_cache = {}

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

def perform_task(scene, Player: PlayerManager, flag: TaskFlag, entity = None, spawner = None, manager = None):
    """Handles Task to be performed"""

    if not entity or str(entity) == 'deleted' or entity not in spawner.active_entities:
        return

    if flag == TaskFlag.ATTACK:
        entity_data = spawner.active_entities[entity]
        id = entity_data['id']
        stats = manager.get(id, Stats)

        if stats and stats.current_health > 0:
            direction = entity.position - Player.entity.visual.position

            face_target(
                Player.entity.visual,
                entity.position
            )

            play_animation(
                Player.entity.visual,
                Player.entity.animations["attack"],
                loop=False,
                force=True,
                on_complete=lambda: play_animation(
                    Player.entity.visual,
                    Player.entity.animations["idle"]
                )
            )

            stats.current_health -= 10

            face_target(
                entity,
                Player.entity.visual.position
            )

            if hasattr(entity, 'sequence') and entity.sequence:
                entity.sequence.kill()

            play_animation(
                entity,
                entity.assets["hurt"]
            )

            invoke(
                lambda: play_animation(
                    entity,
                    entity.assets["idle"]
                ),
                delay=0.4
            )

            health = entity_data['health']
            percentage = stats.current_health / stats.max_health
            health.value = stats.current_health

            if health.max_value > 0:
                health.bar.scale_x = health.value / health.max_value

            health.text_entity.origin = (0, 0)
            health.text_entity.z = -0.1

            if percentage <= 0.5:
                health.bar_color = color.yellow
                health.text_entity.color = color.white

            if percentage <= 0.2:
                health.bar_color = color.red
                health.text_entity.color = color.white

            health.text_entity.text = f'{int(stats.current_health)} / {int(stats.max_health)}'

            if stats.current_health <= 0:
                experience = ExperienceSystem(manager)

                experience.add(Player.entity.id, 10)

                if hasattr(entity, 'sequence') and entity.sequence:
                    entity.sequence.kill()

                if health:
                    destroy(health)

                if entity in spawner.active_entities:
                    del spawner.active_entities[entity]

                destroy(entity)

def play_animation(entity, gif, fps=12, loop=True, force=False, on_complete=None):
    if not force and getattr(entity, "current_animation", None) == gif:
        return

    entity.current_animation = gif

    if hasattr(entity, "sequence") and entity.sequence:
        entity.sequence.kill()

    if gif not in _animation_cache:
        anim = Animation(
            gif,
            fps=fps,
            loop=True,
            autoplay=False,
            billboard=True
        )

        frames = anim.frames[:-1] if len(anim.frames) > 1 else anim.frames
        times = anim.frame_times[:-1] if len(anim.frames) > 1 else anim.frame_times

        _animation_cache[gif] = (frames, times)

        destroy(anim)

    frames, times = _animation_cache[gif]

    entity.texture = frames[0]

    sequence = Sequence(loop=loop, auto_destroy=False)

    for frame, wait in zip(frames, times):
        sequence.append(Func(setattr, entity, 'texture', frame))
        sequence.append(Wait(wait))

    if on_complete:
        sequence.append(Func(on_complete))

    entity.sequence = sequence
    sequence.start()

def face_target(sprite, target):
    direction = target.x - sprite.x

    if direction < 0:
        sprite.scale_x = -abs(sprite.base_scale)
    else:
        sprite.scale_x = abs(sprite.base_scale)

def handle_player_movement(visual, target, manager, id, dt, Player):
    """Handles the math for walking to a clicked destination."""

    speed = manager.get(id, Stats)
    direction = target - visual.position

    if direction.length() > 0.1:
        direction = direction.normalized()

        face_target(visual, target)

        visual.position += direction * speed.movementspeed * dt

        play_animation(
            visual,
            Player.entity.animations["walk"],
            loop=True
        )

        data = manager.get(id, Position)

        if data:
            data.x, data.y, data.z = visual.x, visual.y, visual.z

        return target
    else:
        play_animation(
            visual,
            Player.entity.animations["idle"]
        )

        return None

def update_player_ui(manager, Player):
    """Keeps the bottom screen UI synced with player data."""
    stats = manager.get(Player.entity.id, Stats)
    experience = manager.get(id, Experience)

    hp = Player.entity.hp_bar
    xp = Player.entity.xp_bar

    hp.text_entity.origin = (0, 0)
    hp.text_entity.z = -0.1
    xp.text_entity.origin = (0, 0)
    xp.text_entity.z = -0.1

    if experience and stats:
        hp.value = stats.current_health

        if hp.max_value > 0:
            hp.bar.scale_x = hp.value / hp.max_value

        hp.text_entity.text = f'{int(stats.current_health)}/{int(stats.max_health)}'
        hp.text_entity.color = color.white if (stats.current_health / stats.max_health) <= 0.2 else color.black
        
        xp.max_value = experience.required
        xp.value = experience.current

        if experience.required > 0:
            xp.bar.scale_x = xp.value / xp.max_value
            
            percentage = clamp(experience.current / experience.required, 0, 1)
            xp.text_entity.text = f'{int(experience.current)}/{int(experience.required)}'

            if percentage >= 0.5:
                xp.text_entity.color = color.black
            else:
                xp.text_entity.color = color.white

            Player.entity.level_text.text = f"Lv. {experience.level}"