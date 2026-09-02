from kivy.app import App
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from data.data import Data


class MapViewer(FloatLayout):
    def __init__(self, image_source, **kwargs):
        super().__init__(**kwargs)

        # Создаем Scatter. Оставляем только перемещение
        self.scatter = Scatter(
            do_rotation=False,
            do_scale=False,
            auto_bring_to_front=False,
            size_hint=(None, None)  # Указываем явно
        )

        # Создаем изображение без fit_mode и size_hint
        self.img = Image(source=image_source, size_hint=(None, None))

        self.scatter.add_widget(self.img)
        self.add_widget(self.scatter)

        # Привязываемся к изменению размеров САМОГО виджета MapViewer.
        # Это гарантирует, что размеры экрана уже известны и актуальны.
        self.bind(size=self._update_layout)

    def _update_layout(self, instance, value):
        # Проверяем, загрузилась ли текстура у картинки
        if not self.img.texture:
            # Если текстура еще не готова, подпишемся на её появление один раз
            self.img.bind(texture=self._on_texture_ready)
            return

        img_w, img_h = self.img.texture.size

        # 1. Задаем физический размер виджетов равным исходному разрешению картинки
        self.img.size = (img_w, img_h)
        self.scatter.size = (img_w, img_h)

        # 2. Вычисляем масштаб на основе РЕАЛЬНЫХ размеров родительского контейнера (self.width / self.height)
        win_w, win_h = self.size

        scale_x = win_w / img_w
        scale_y = win_h / img_h

        # Эффект Cover: берем максимальный коэффициент, чтобы заполнить всё пространство
        start_scale = max(scale_x, scale_y)
        self.scatter.scale = start_scale

        # 3. Центрируем Scatter
        scaled_w = img_w * start_scale
        scaled_h = img_h * start_scale

        self.scatter.pos = (
            (win_w - scaled_w) / 2,
            (win_h - scaled_h) / 2
        )

    def _on_texture_ready(self, instance, texture):
        # Как только текстура загрузилась, отписываемся от события и обновляем слой
        if texture:
            self.img.unbind(texture=self._on_texture_ready)
            self._update_layout(self, self.size)


class Editor(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level = 0  # TODO: !
        self.data = Data()

    def build(self):
        return MapViewer(image_source=self.data.get_level_image(self.level))
