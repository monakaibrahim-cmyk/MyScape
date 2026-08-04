from ursina import *
from Entity import *
from Spawner import *
from MapManager import *
from Systems import *
from direct.actor.Actor import Actor

app = Ursina()
manager = EntityManager()

region = MapManager(size=100)
region.build_debug_map()

player = manager.create_entity()
manager.add_component(player, Position(x=0, y=0.5, z=0))
manager.add_component(player, Stats(health=100.0))
manager.add_component(player, Speed(value=5))

player_visual = Entity(scale=0.5)
player_model = Actor('assets/player/godotman.glb')
player_model.reparent_to(player_visual)

player_model.setH(180)

add_entity_debug_marker(player_visual)

camera_pivot = Entity(y=1)
camera.parent = camera_pivot

camera_pivot.rotation_x = 45
camera.position = (0, 0, -20)

interface = Entity(parent=camera.ui, model='quad', color=color.dark_gray, scale=(0.4, 0.05), position=(0, -0.42), z=0.1)
health_bar = Entity(parent=interface, model='quad', color=color.green, scale=(1, 1), position=(0, 0), origin=(-0.5, 0), x=-0.5, z=-0.01)
health_text = Text(parent=camera.ui, text='HP: 100', position=(0, -0.42), origin=(0, 0), color=color.dark_gray, z=-0.1)

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
            target.y = player_visual.y
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

    camera_pivot.position = player_visual.position + Vec3(0, 1, 0)

    if attack_cooldown > 0:
        attack_cooldown -= time.dt

    if combat_target:
        if combat_target not in spawner.active_entities:
            combat_target = None
        else:
            distance = (combat_target.position - player_visual.position).length()

            if distance > 3.0:
                handle_player_movement(player_visual, combat_target.position, manager, player, time.dt, player_model)
            else:
                if player_model.getCurrentAnim() == 'run':
                    player_model.loop('idle')

                if attack_cooldown <= 0:
                    perform_task(scene, player_model, player_visual, TaskFlag.ATTACK, entity=combat_target, spawner=spawner, manager=manager)
                    attack_cooldown = 1.0
    elif target:
        target = handle_player_movement(player_visual, target, manager, player, time.dt, player_model)
    else:
        if player_model.getCurrentAnim() not in ['idle', 'attack']:
            player_model.loop('idle')

    if held_keys['right mouse']:
        camera_pivot.rotation_y += mouse.velocity.x * 150
        camera_pivot.rotation_x -= mouse.velocity.y * 150
        camera_pivot.rotation_x = clamp(camera_pivot.rotation_x, -10, 80)

    update_player_ui(manager, player, health_text, health_bar)
   
if __name__ == '__main__':
    app.run()

