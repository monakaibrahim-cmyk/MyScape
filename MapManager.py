from ursina import *
from enum import Enum

class Regions(Enum):
    # todo <- i don't have any idea what to name the regions of the map
    TEST = 1

class MapManager:
    def __init__(self, size=100):
        self.size = size
        self.border_thickness = 0.1
        self.edge_position = (self.size / 2) - (self.border_thickness / 2)
        self.ground = None
        
    def build_debug_map(self):
        self.ground = Entity(model='plane', scale=(self.size, 1, self.size), color=color.dark_gray, collider='box')
        
        Entity(model=Grid(self.size, self.size), scale=(self.size, self.size), color=color.rgba(255, 255, 255, 40), rotation_x=90, y=0.01)

        Entity(model='quad', color=color.green, scale=(0.05, self.size), rotation_x=90, y=0.02)
        Entity(model='quad', color=color.red, scale=(self.size, 0.05), rotation_x=90, y=0.02)
        
        Entity(model='quad', color=color.green, scale=(self.size, self.border_thickness), rotation_x=90, position=(0, 0.02, self.edge_position), collider='box')
        Entity(model='quad', color=color.green, scale=(self.size, self.border_thickness), rotation_x=90, position=(0, 0.02, -self.edge_position), collider='box')
        Entity(model='quad', color=color.green, scale=(self.border_thickness, self.size), rotation_x=90, position=(self.edge_position, 0.02, 0), collider='box')
        Entity(model='quad', color=color.green, scale=(self.border_thickness, self.size), rotation_x=90, position=(-self.edge_position, 0.02, 0), collider='box')

