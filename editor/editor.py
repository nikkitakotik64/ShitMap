from kivy.app import App
from kivy.uix.image import Image
from data.data import Data


class Editor(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level = 0  # TODO: !
        self.data = Data()

    def build(self):
        return Image(source=self.data.get_level_image(self.level))
