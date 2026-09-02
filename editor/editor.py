from kivy.app import App
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from data.data import Data
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


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


class Editor(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level = 0  # Текущий этаж по умолчанию
        self.data = Data()
        self.map_viewer = None  # Ссылка на виджет карты, чтобы обновлять его

    def build(self):
        # Главный контейнер всего экрана
        main_layout = FloatLayout()

        # 1. Создаем и добавляем карту на весь экран
        self.map_viewer = MapViewer(
            image_source=self.data.get_level_image(self.level)
        )
        main_layout.add_widget(self.map_viewer)

        # 2. Создаем вертикальный контейнер для кнопок этажей
        # Размещаем его справа по центру
        button_panel = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            # TODO: привязать панель к размерам экрана
            size=(
                80,
                250,
            ),  # Ширина панели 80 пикселей, высота 250 (5 кнопок по 50px)
            pos_hint={
                "right": 0.98,
                "center_y": 0.5,
            },  # Справа с небольшим отступом, по центру вертикали
            spacing=5,  # Расстояние между кнопками
        )

        # 3. Генерируем 5 кнопок (от 0 до 4)
        for floor_num in range(5):
            btn = Button(
                text=str(floor_num),
                size_hint=(1, 1),
                background_color=(
                    (0.2, 0.6, 1, 1) if floor_num == self.level else (1, 1, 1, 1)
                ),
            )
            # Привязываем метод переключения и передаем номер этажа через lambda
            btn.bind(
                on_release=lambda instance, f=floor_num: self.change_floor(
                    f, instance, button_panel
                )
            )
            button_panel.add_widget(btn)

        # Добавляем панель с кнопками поверх карты
        main_layout.add_widget(button_panel)

        return main_layout

    def change_floor(self, floor_num, pressed_button, button_panel):
        """Метод для переключения этажа и обновления картинки."""
        if self.level == floor_num:
            return  # Если нажали на уже активный этаж, ничего не делаем

        self.level = floor_num

        # Обновляем подсветку кнопок: активная — синяя, остальные — белые
        for btn in button_panel.children:
            if btn.text == str(floor_num):
                btn.background_color = (0.2, 0.6, 1, 1)
            else:
                btn.background_color = (1, 1, 1, 1)

        # Удаляем старую карту из разметки
        parent = self.map_viewer.parent
        parent.remove_widget(self.map_viewer)

        # Создаем новую карту с новым изображением этажа
        new_image_source = self.data.get_level_image(self.level)
        self.map_viewer = MapViewer(image_source=new_image_source)

        # Добавляем новую карту на самый нижний слой (индекс 1, чтобы кнопки остались сверху)
        parent.add_widget(self.map_viewer, index=1)