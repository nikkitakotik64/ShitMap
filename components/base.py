from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image


class MapViewer(FloatLayout):
    max_scale = 10.0
    min_scale = 1.0  # Начальный заглушечный масштаб

    def __init__(self, image_source, pos=(-1, -1), zoom=-1, **kwargs):
        super().__init__(**kwargs)

        self.scatter = Scatter(
            do_rotation=False,
            auto_bring_to_front=False,
            size_hint=(None, None)
        )

        self.img = Image(source=image_source, size_hint=(None, None))
        self.scatter.add_widget(self.img)
        self.add_widget(self.scatter)

        self._initial_pos = pos
        self._initial_zoom = zoom
        self._initialized_transforms = False

        self.bind(size=self._update_layout)
        self.scatter.bind(scale=self._limit_zoom)
        self.scatter.bind(pos=self._limit_position)

    def get_info(self):
        return self.scatter.pos, self.scatter.scale

    def _limit_position(self, instance, pos_value):
        self.scatter.unbind(pos=self._limit_position)

        win_w, win_h = self.size
        img_w, img_h = self.img.size
        current_scale = instance.scale

        scaled_w = img_w * current_scale
        scaled_h = img_h * current_scale

        x, y = pos_value
        new_x = x
        new_y = y

        # Лево / Право
        if scaled_w <= win_w:
            new_x = (win_w - scaled_w) / 2
        elif x + scaled_w < win_w:
            new_x = win_w - scaled_w
        elif x > 0:
            new_x = 0

        # Верх / Низ
        if scaled_h <= win_h:
            new_y = (win_h - scaled_h) / 2
        elif y + scaled_h < win_h:
            new_y = win_h - scaled_h
        elif y > 0:
            new_y = 0

        instance.pos = (new_x, new_y)
        self.scatter.bind(pos=self._limit_position)

    def _limit_zoom(self, instance, value):
        if value < self.min_scale:
            self.scatter.scale = self.min_scale
        elif value > self.max_scale:
            self.scatter.scale = self.max_scale

    def _update_layout(self, _, __):
        if not self.img.texture:
            self.img.bind(texture=self._on_texture_ready)
            return

        img_w, img_h = self.img.texture.size
        self.img.size = (img_w, img_h)
        self.scatter.size = (img_w, img_h)

        win_w, win_h = self.size

        # Расчет минимального масштаба для эффекта Cover
        scale_x = win_w / img_w
        scale_y = win_h / img_h
        self.min_scale = max(scale_x, scale_y)

        if not self._initialized_transforms:
            # 1. Полностью отписываемся от лимитов на время инициализации
            self.scatter.unbind(scale=self._limit_zoom)
            self.scatter.unbind(pos=self._limit_position)

            # 2. Устанавливаем масштаб (кастомный или Cover)
            if self._initial_zoom != -1:
                self.scatter.scale = self._initial_zoom
            else:
                self.scatter.scale = self.min_scale

            # 3. Устанавливаем позицию (кастомную или авто-центрирование)
            if self._initial_pos != (-1, -1):
                self.scatter.pos = self._initial_pos
            else:
                scaled_w = img_w * self.scatter.scale
                scaled_h = img_h * self.scatter.scale
                self.scatter.pos = (
                    (win_w - scaled_w) / 2,
                    (win_h - scaled_h) / 2
                )

            self._initialized_transforms = True

            # 4. Возвращаем бинды обратно
            self.scatter.bind(scale=self._limit_zoom)
            self.scatter.bind(pos=self._limit_position)

            # ВАЖНО: Больше НЕ вызываем self._limit_position здесь вручную,
            # чтобы не перезаписать ваши кастомные координаты!
        else:
            # Срабатывает только при изменении размеров окна (например, поворот экрана)
            self._limit_position(self.scatter, self.scatter.pos)

    def _on_texture_ready(self, _, texture):
        if texture:
            self.img.unbind(texture=self._on_texture_ready)
            self._update_layout(self, self.size)
