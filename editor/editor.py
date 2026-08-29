from kivy.app import App
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from data.data import Data


class MapViewer(FloatLayout):
    def __init__(self, image_source, **kwargs):
        super().__init__(**kwargs)

        # Создаем Scatter. Оставляем только перемещение (do_scale=False отключает зум пальцами)
        self.scatter = Scatter(
            do_rotation=False,
            do_scale=False,
            auto_bring_to_front=False
        )

        # Создаем изображение
        self.img = Image(source=image_source)
        self.img.fit_mode = 'cover'

        # Автоматически настраиваем размеры и масштаб при загрузке картинки
        self.img.bind(texture=self._init_image_size)

        self.scatter.add_widget(self.img)
        self.add_widget(self.scatter)

    def _init_image_size(self, instance, texture):
        if not texture:
            return

        # 1. Задаем физический размер для Scatter и Image равным размеру картинки
        img_w, img_h = texture.size
        self.scatter.size = (img_w, img_h)
        self.img.size = (img_w, img_h)
        self.img.size_hint = (None, None)

        # 2. Вычисляем масштаб, чтобы картинка заполнила весь экран БЕЗ черных рамок
        win_w, win_h = Window.size
        scale_x = win_w / img_w
        scale_y = win_h / img_h

        # max заставит картинку растянуться так, чтобы полностью закрыть экран (эффект Cover)
        start_scale = max(scale_x, scale_y)
        self.scatter.scale = start_scale

        # 3. Центрируем Scatter на экране с учетом нового масштаба
        # (чтобы центр картинки совпал с центром экрана)
        scaled_w = img_w * start_scale
        scaled_h = img_h * start_scale

        self.scatter.pos = (
            (win_w - scaled_w) / 2,
            (win_h - scaled_h) / 2
        )


class Editor(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level = 0  # TODO: !
        self.data = Data()

    def build(self):
        return MapViewer(image_source=self.data.get_level_image(self.level))
