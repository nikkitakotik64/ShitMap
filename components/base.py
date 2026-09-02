from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image


class MapViewer(FloatLayout):
    max_scale = 10.0
    min_scale = -1.0

    def __init__(self, image_source, **kwargs):
        super().__init__(**kwargs)

        # Создаем Scatter. Оставляем только перемещение
        self.scatter = Scatter(
            do_rotation=False,
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

        # Привязываемся на событие трансформации
        self.scatter.bind(scale=self._limit_zoom)
        self.scatter.bind(pos=self._limit_position)

    def _limit_position(self, instance, pos_value):
        # Отключаем рекурсивный вызов метода во время корректировки позиции
        self.scatter.unbind(pos=self._limit_position)

        win_w, win_h = self.size
        img_w, img_h = self.img.size
        current_scale = instance.scale

        # Вычисляем текущие размеры картинки на экране с учетом зума
        scaled_w = img_w * current_scale
        scaled_h = img_h * current_scale

        x, y = pos_value
        print(x, y, scaled_w, scaled_h, win_w, win_h)
        new_x = x
        new_y = y

        # лево право
        if scaled_w == win_w:
            new_x = (win_w - scaled_w) / 2
        elif x + scaled_w < win_w: # если правая граница окна левее границы экрана
            new_x = win_w - scaled_w
        elif x > 0:  # если левая граница окна правее границы экрана
            new_x = 0

        # верх низ
        if scaled_h == win_h:
            new_y = (win_h - scaled_h) / 2
        elif y > 0:
            new_y = 0
        elif y < win_h - scaled_h:
            new_y = win_h - scaled_h

        # Применяем скорректированные координаты
        instance.pos = (new_x, new_y)

        # Возвращаем прикрепление обратно
        self.scatter.bind(pos=self._limit_position)

    def _limit_zoom(self, _, __):
        # Если масштаб ушел за минимальный предел
        if self.scatter.scale < self.min_scale:
            self.scatter.scale = self.min_scale

        # Если масштаб ушел за максимальный предел
        elif self.scatter.scale > self.max_scale:
            self.scatter.scale = self.max_scale

    def _update_layout(self, _, __):
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
        self.min_scale = max(scale_x, scale_y)
        self.scatter.scale = self.min_scale

        # 3. Центрируем Scatter
        scaled_w = img_w * self.min_scale
        scaled_h = img_h * self.min_scale

        self.scatter.pos = (
            (win_w - scaled_w) / 2,
            (win_h - scaled_h) / 2
        )

    def _on_texture_ready(self, _, texture):
        # Как только текстура загрузилась, отписываемся от события и обновляем слой
        if texture:
            self.img.unbind(texture=self._on_texture_ready)
            self._update_layout(self, self.size)

