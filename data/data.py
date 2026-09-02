import os
from data.map_levels.levels import LEVEL_IMAGES

FLOORS = (-1, 1, 2, 3, 4)

folder = os.path.dirname(__file__).replace("\\", "/")


class Data:
    path = folder + '/'
    maps_path = path + 'map_levels/'

    def __init__(self):
        pass

    def get_level_image(self, level: int) -> str:
        return self.maps_path + LEVEL_IMAGES[level]
