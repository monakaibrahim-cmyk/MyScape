from ursina import *
from ursina.prefabs.health_bar import HealthBar 
from Entity.Entity import *
from Entity.Spawner import *
from Entity.Player import *
from Map.MapManager import *
from Systems.Systems import *

window.vsync = False

app = Ursina()
manager = EntityManager()

region = MapManager(size=100)
region.build_debug_map()

Player = PlayerManager(manager)
Player.spawn(x=0, y=0.5, z=0)

Player.entity.animations = {
    "idle": "assets/player/spr_idle.gif",
    "walk": "assets/player/spr_walking.gif",
    "attack": "assets/player/spr_attack.gif",
}

Player.entity.visual = Entity(
    model='quad',
    texture='white_cube',
    collider='box',
    scale=5,
    billboard=True,
    double_sided=True
)

Player.entity.level_text = Text(
    parent=Player.entity.visual,
    text=f"Lv. {Player.entity.stats.level}",
    position=(0, 0.2, 0),
    scale=2,
    origin=(0, 0),
    billboard=True,
    color=color.yellow
)

Player.entity.visual.base_scale = 5

play_animation(
    Player.entity.visual,
    Player.entity.animations["idle"]
)

# add_entity_debug_marker(Player.entity.visual)

pivot = Entity(y=1)
camera.parent = pivot

pivot.rotation_x = 45
camera.position = (0, 0, -20)

interface = Entity(
    parent=camera.ui,
    model='quad',
    color=color.hsv(0, 0, 1, 0),
    scale=(0.35, 0.08),
    position=(0, -0.42),
    z=0.1
)

Player.entity.hp_bar = HealthBar(
    max_value=Player.entity.stats.max_health,
    value=Player.entity.stats.current_health,
    parent=interface,
    position=(0, 0.5),
    scale=(1, 0.5),
    color=color.black,
    bar_color=color.green,
    roundness=0,
    origin=(-0.5, 0),
    x=-0.5,
    z=-0.01,
    billboard=True,
    text_size=2
)

Player.entity.xp_bar = HealthBar(
    max_value=Player.entity.experience.required,
    value=Player.entity.experience.current,
    parent=interface,
    position=(0, -0.25),
    scale=(1, 0.5),
    color=color.black,
    bar_color=color.magenta,
    roundness=0,
    show_text=True,
    origin=(-0.5, 0),
    x=-0.5,
    z=-0.01,
    billboard=True,
    text_size=2
)

spawner = SpawnerManager(manager)
spawner.auto(amount=5, cmin=-10, cmax=10, flag=EntityFlag.MOB)

target = None
combat_target = None
attack_cooldown = 0.0

def input(key):
    global target, combat_target

    if key == 'left mouse down':
        if mouse.hovered_entity in spawner.active_entities:
            combat_target = mouse.hovered_entity
            target = None

            marker = Entity(parent=combat_target, model='quad', color=color.red, rotation_x=90, position=(0, 0.1, 0), scale=1.5)
            destroy(marker, delay=0.3)

        elif mouse.hovered_entity == region.ground:
            target = mouse.world_point
            target.y = Player.entity.visual.y
            combat_target = None

            marker = Entity(model='quad', color=color.yellow, rotation_x=90, position=target, scale=0.5)
            destroy(marker, delay=0.3)

    if key == 'scroll up' and camera.z < -2:
        camera.z += 2

    if key == 'scroll down' and camera.z > -120:
        camera.z -= 2

def update():
    global target, combat_target, attack_cooldown

    spawner.update()

    pivot.position = Player.entity.visual.position + Vec3(0, 1, 0)

    if attack_cooldown > 0:
        attack_cooldown -= time.dt

    if combat_target:
        if combat_target not in spawner.active_entities:
            combat_target = None
        else:
            distance = (combat_target.position - Player.entity.visual.position).length()

            if distance > 3.0:
                handle_player_movement(
                    Player.entity.visual,
                    combat_target.position,
                    manager,
                    Player.entity.id,
                    time.dt,
                    Player
                )
            else:
                if attack_cooldown <= 0:
                    perform_task(scene, Player, TaskFlag.ATTACK, entity=combat_target, spawner=spawner, manager=manager)
                    attack_cooldown = Player.entity.stats.attackspeed
    elif target:
        target = handle_player_movement(
            Player.entity.visual,
            target,
            manager,
            Player.entity.id,
            time.dt,
            Player
        )
    else:
        play_animation(
            Player.entity.visual,
            Player.entity.animations["idle"]
        )

    if held_keys['right mouse']:
        pivot.rotation_y += mouse.velocity.x * 150
        pivot.rotation_x -= mouse.velocity.y * 150
        pivot.rotation_x = clamp(pivot.rotation_x, -10, 80)

    update_player_ui(manager, Player)
   
if __name__ == '__main__':
    app.run()

