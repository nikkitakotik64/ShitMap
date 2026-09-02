from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from data.data import Data, FLOORS
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from components.base import MapViewer
from kivy.core.window import Window


class Editor(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level = 2  # Текущий этаж по умолчанию
        self.data = Data()
        self.map_viewer = None  # Ссылка на виджет карты, чтобы обновлять его

    def build(self):
        # Главный контейнер всего экрана
        main_layout = FloatLayout()

        # 1. Создаем и добавляем карту на весь экран
        self.map_viewer = MapViewer(
            image_source=self.data.get_level_image(self.level)
        )
        width, height = Window.size
        main_layout.add_widget(self.map_viewer)

        # 2. Создаем вертикальный контейнер для кнопок этажей
        # Размещаем его справа по центру
        button_panel = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(
                0.05 * width,
                0.23 * height,
            ),
            pos_hint={
                "right": 0.98,
                "center_y": 0.5,
            },  # Справа с небольшим отступом, по центру вертикали
            spacing=0.005 * height,  # Расстояние между кнопками
        )

        # 3. Генерируем 5 кнопок
        for floor_num in FLOORS:
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

    def change_floor(self, floor_num, _, button_panel):
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