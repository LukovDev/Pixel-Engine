#
# editor.py - Создаёт основное окно редактора.
#


# Импортируем:
import core
import engine
from engine import *
from engine.gdf.graphics import *

if __name__ == "__main__": from main import main ; main()


# Класс редактора:
class EditorApplication(Window):
    def __init__(self) -> None:
        self.project     = None
        self.loaded_data = {}

    # Инициализировать данные проекта:
    def init_project_data(self, project: core.ProjectManager) -> None:
        self.project = project
    
    # Инициализировать открываемую сцену:
    def init_open_scene(self) -> None:
        pass

    # Инициализировать окно:
    def init(self) -> None:
        super().__init__(
            title      = f"Pixel Engine - Editor [v0.1] - Project: {self.project.config['name']}",
            icon       = files.load_image("./data/icons/logo/icon-black.png"),
            size       = vec2(960, 540),
            vsync      = False,
            fps        = 60,
            visible    = True,
            titlebar   = True,
            resizable  = True,
            fullscreen = False,
            min_size   = vec2(960, 540)//1.5,
            max_size   = vec2(float("inf"), float("inf")),
            samples    = 16
        )

    # Вызывается при создании окна:
    def start(self) -> None:
        pass

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, event_list: list) -> None:
        pass

    # Вызывается каждый кадр (игровая отрисовка):
    def render(self, delta_time: float) -> None:
        self.window.clear(0, 0, 0)

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
