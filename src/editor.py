#
# editor.py - Создаёт основное окно редактора.
#


# Импортируем:
import core
import engine
from engine import *
from engine.gdf.audio import *
from engine.gdf.graphics import *
from engine.gdf.net import *
from engine.gdf.physics import *
from engine.gdf.controllers import *
from engine.gdf import files
from engine.gdf.input import *
from engine.gdf.math import *
from engine.gdf.utils import *

if __name__ == "__main__": from main import main ; main()


# Класс редактора:
class EditorApplication(Window):
    def __init__(self) -> None:
        engine.Debug.log("Editor: Editor class has been created.", EditorApplication)

        # Для лаунчера редактора:
        self.project = None

        # Основное:
        self.config   = core.editor_const.config
        self.settings = core.editor_const.settings

        self.camera     = None
        self.controller = None

    # Инициализировать открываемую сцену:
    def init_open_scene(self) -> None:
        engine.Debug.log("Editor: Initialization of the opening scene. Opening the scene...", EditorApplication)

    # Инициализировать окно:
    def init(self) -> None:
        engine.Debug.log("Editor: Initializing the window...", EditorApplication)
        super().__init__(
            title      = f"Pixel Engine - Editor [v0.1] - Project: {self.project.config['name']}",
            icon       = files.load_image("./data/icons/logo/icon-black.png"),
            size       = vec2(*self.config["size"]),
            vsync      = self.config["vsync"],
            fps        = self.config["fps"],
            visible    = True,
            titlebar   = self.config["titlebar"],
            resizable  = self.config["resizable"],
            fullscreen = self.config["fullscreen"],
            min_size   = vec2(*self.config["min-size"]),
            max_size   = vec2(*self.config["max-size"]),
            samples    = self.config["samples"]
        )

    # Вызывается при создании окна:
    def start(self) -> None:
        engine.Debug.log("Editor: Initializing the window: Done!", EditorApplication)

        # Обработчик ввода:
        self.input = InputHandler(self.window)

        # 2D камера:
        self.camera = Camera2D(
            *self.window.get_size().xy,
            position = vec2(0, 0),
            angle    = 0.0,
            zoom     = 1.0,
            meter    = self.settings["meter"]
        )

        # Контроллер камеры:
        self.controller = CameraController2D(self.input, self.camera)

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, event_list: list) -> None:
        # Обновляем контроллер камеры:
        self.controller.update(delta_time)

    # Вызывается каждый кадр (игровая отрисовка):
    def render(self, delta_time: float) -> None:
        self.camera.update()
        self.window.clear(*self.settings["clear-color"][:3])

        Draw2D.line([1, 0, 0], vec2(-1000, 0), vec2(+1000, 0), 1)
        Draw2D.line([0, 1, 0], vec2(0, -1000), vec2(0, +1000), 1)
        Draw2D.point([1, 1, 1], vec2(0, 0), 4)

        self.window.display()

    # Вызывается при изменении размера окна:
    def resize(self, width: int, height: int) -> None:
        self.camera.resize(width, height)

    # Вызывается при разворачивании окна:
    def show(self) -> None:
        pass

    # Вызывается при сворачивании окна:
    def hide(self) -> None:
        pass

    # Вызывается при закрытии окна:
    def destroy(self) -> None:
        pass
