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
        engine.Debug.log("Editor: Editor class has been created.", EditorApplication)

        # Для лаунчера редактора:
        self.project = None

        # Основное:
        self.editor_config = core.editor_const.config

    # Инициализировать открываемую сцену:
    def init_open_scene(self) -> None:
        engine.Debug.log("Editor: Initialization of the opening scene. Opening the scene...", EditorApplication)

    # Инициализировать окно:
    def init(self) -> None:
        engine.Debug.log("Editor: Initializing the window...", EditorApplication)
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
        engine.Debug.log("Editor: Initializing the window: Done!", EditorApplication)

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
