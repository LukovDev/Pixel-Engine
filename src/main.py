#
# main.py - Основной запускаемый файл программы.
#


# Импортируем:
import sys
import time

import engine
from engine import *
from engine.gdf.graphics import *

from editor import EditorApplication


# Класс лаунчера редактора:
class EditorLauncher(Window):
    def __init__(self) -> None:
        self.input        = None
        self.background   = None
        self.icons        = None
        self.exit_hovered = False
        self.project      = None
        self.progress_bar = 0.0
        self.sprite_pbar  = Sprite2D()
        self.editor       = EditorApplication()

        # Создаём окно:
        self.init()

    # Создать окно:
    def init(self) -> None:
        super().__init__(
            title      = "Opening project",
            icon       = files.load_image("./data/icons/logo/icon-black.png"),
            size       = vec2(960, 540),
            vsync      = False,
            fps        = 60,
            visible    = False,
            titlebar   = False,
            resizable  = False,
            fullscreen = False,
            min_size   = vec2(0, 0),
            max_size   = vec2(float("inf"), float("inf")),
            samples    = 16
        )

    # Открыть редактор:
    def open_editor(self) -> None:
        self.window.set_visible(False)  # Скрываем это окно.
        self.window.clear(0, 0, 0)      # Очищаем окно для редактора.

        # Передаём данные проекта редактору:
        self.editor.init_project_data(self.project)

        # Инициализируем сцену:
        self.editor.init_open_scene()

        # Запускаем редактор:
        self.editor.init()

        # Завершаем работу:
        sys.exit()

    # Вызывается при создании окна:
    def start(self) -> None:
        # Обработчик ввода:
        self.input = gdf.input.InputHandler(self.window)

        # Загружаем фон:
        self.background = Sprite2D(files.load_texture("./data/sprites/cover.png").set_pixelized())

        # Загружаем иконки:
        self.icons = {
            "exit": files.load_sprite("./data/icons/mini-icon/none.png")
        }

        # Загружаем данные о проекте:
        self.project = {
            "name": "Untitled",
            "description": "Its your new game!",
            "settings": {
                "version": "v1.0",
                "company": ""
            },
            "data": [
                "/.proj/scenes/main.pscn",
                "/.proj/objects/square.pobj",
                "/.proj/objects/camera.pobj",
                "/.proj/metadata.pmeta"
            ],
            "meta": {
                "engine-version": "v0.1",
                "gdf-version": "v1.0",
                "editor-version": "v0.1"
            },
            "cache": [
            ]
        }

        # Обновляем заголовок окна:
        self.window.set_title(f"Opening project: {self.project['name']}")

        # Отображаем окно:
        self.window.set_visible(True)

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, event_list: list) -> None:
        self.progress_bar += delta_time*100  # Пока что просто увеличиваем до 100% за секунду.

        # Ограничиваем прогресс бар:
        self.progress_bar = min(self.progress_bar, 100)

        # Обрабатываем нажатие на крестик:
        size = self.window.get_size()
        if gdf.utils.Intersects.point_rectangle(self.input.get_mouse_pos(), [size.x-32, 32-24, 24, 24]):
            self.exit_hovered = True
            if self.input.get_mouse_up()[0]: self.window.exit()
        else: self.exit_hovered = False

        # Если мы загрузили все необходимые данные, запускаем редактор:
        if self.progress_bar >= 100:
            self.open_editor()

    # Вызывается каждый кадр (игровая отрисовка):
    def render(self, delta_time: float) -> None:
        self.window.clear(0, 0, 0)
        size = self.window.get_size()

        # Рисуем обложку:
        self.background.render(*-size.xy//2, *size.xy)

        # Рисуем крестик для закрытия:
        self.icons["exit"].render(size.x//2-32, size.y//2-32, 24, 24, color=[0.65]*3 if self.exit_hovered else [1.0]*3)

        # Рисуем прогресс бар:
        self.sprite_pbar.render(*-size.xy//2, (self.progress_bar/100)*size.x, 4)

        self.window.display()

    # Вызывается при изменении размера окна:
    def resize(self, width: int, height: int) -> None:
        pass

    # Вызывается при разворачивании окна:
    def show(self) -> None:
        pass

    # Вызывается при сворачивании окна:
    def hide(self) -> None:
        pass

    # Вызывается при закрытии окна:
    def destroy(self) -> None:
        pass


# Основная функция:
def main() -> None:
    EditorLauncher()


# Если этот скрипт запускают:
if __name__ == "__main__":
    main()
