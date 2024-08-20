#
# editor.py - Создаёт основное окно редактора.
#


# Импортируем:
import os
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

        # Внутренние настройки редактора:
        self.config = core.editor_const.config

        # Настраиваемые общие настройки редактора:
        self.settings = {}

        # Загружаем настройки редактора:
        self.load_settings()

        # Другое:

        self.discord_rpc = engine.DiscordRPCEngine(self.settings)

        self.scene     = None
        self.use_scene = True

        self.camera     = None
        self.controller = None

    # Загружаем настройки редактора:
    def load_settings(self) -> None:
        if os.path.isfile("./data/editor/settings.json"):
            self.settings = files.load_json("./data/editor/settings.json")
        else: self.settings = core.editor_const.settings

    # Сохраняем настройки редактора:
    def save_settings(self) -> None:
        if not os.path.isdir("./data/editor/"): os.makedirs("./data/editor/")
        files.save_json("./data/editor/settings.json", self.settings)

    # Инициализировать открываемую сцену:
    def init_open_scene(self) -> None:
        engine.Debug.log("Editor: Initialization of the opening scene. Opening the scene...", EditorApplication)
        for scene in self.project.scenes:
            if scene.id == 0: self.scene = scene ; break
        engine.Debug.log("Editor: Initialization of the opening scene. Opening the scene: Done!", EditorApplication)

    # Используем функцию из сцены:
    def scene_using(self, func: any, err_text: str) -> None:
        try:
            if self.use_scene: func()
        except Exception as error:
            self.use_scene = False
            engine.Debug.error(
                f"Editor: {err_text} scene \"{self.scene.name}\" [{self.scene.id}] "
                f"failed: ERROR: {error.__class__.__name__}: {error}")

    # Инициализировать окно:
    def init(self) -> None:
        engine.Debug.log("Editor: Initializing the window...", EditorApplication)
        super().__init__(
            title      = f"Pixel Engine - Editor [v0.1] - Project: {self.project.config['name']}",
            icon       = files.load_image("./data/icons/logo/icon-black.png"),
            size       = vec2(*self.config["size"]),
            vsync      = self.config["vsync"],
            fps        = self.config["fps"],
            visible    = False,
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
        engine.Debug.log("Editor: Starting...", EditorApplication)

        # Обновляем статус активности в дискорд:
        self.discord_rpc.update(f"Project: {self.project.config['name']}", "In Editor")

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

        # Сетка:
        self.grid = core.gizmos.Grid(self.camera).create()

        # Запускаем сцену:
        self.scene_using(lambda: self.scene.start(), "Starting")

        engine.Debug.log("Editor: Starting: Done!", EditorApplication)

        # Показываем окно редактора как всё готово:
        self.window.set_visible(True)

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, event_list: list) -> None:
        # Обновляем контроллер камеры:
        self.controller.update(delta_time)

        # Обновляем сцену:
        self.scene_using(lambda: self.scene.update(delta_time, event_list), "Updating")

    # Вызывается каждый кадр (игровая отрисовка):
    def render(self, delta_time: float) -> None:
        self.window.clear(*self.settings["clear-color"][:3])

        # Рисуем сцену:
        self.scene_using(lambda: self.scene.render(delta_time), "Rendering")

        # Рисуем сетку:
        self.grid.render(delta_time, self.settings["clear-color"][:3])

        self.camera.update()
        self.window.display()

    # Вызывается при изменении размера окна:
    def resize(self, width: int, height: int) -> None:
        self.camera.resize(width, height)

        # Меняем размер в сцене:
        self.scene_using(lambda: self.scene.resize(width, height), "Resizing")

    # Вызывается при разворачивании окна:
    def show(self) -> None:
        # Вызываем функцию показа окна в сцене:
        self.scene_using(lambda: self.scene.show(), "Show")

    # Вызывается при сворачивании окна:
    def hide(self) -> None:
        # Вызываем функцию скрытия окна в сцене:
        self.scene_using(lambda: self.scene.hide(), "Hide")

    # Вызывается при закрытии окна:
    def destroy(self) -> None:
        # Освобождаем ресурсы сцены:
        self.scene_using(lambda: self.scene.destroy(), "Destroy")
