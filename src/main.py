#
# main.py - Основной запускаемый файл программы.
#


# Импортируем:
import os
import sys

import core
import engine
from engine import *
from engine.gdf.graphics import *

from editor import EditorApplication


# Класс лаунчера редактора:
class EditorLauncher(Window):
    def __init__(self) -> None:
        engine.Debug.log("LaunchEditor: Class created...", EditorLauncher)
        self.input        = None
        self.background   = None
        self.icons        = None
        self.exit_hovered = False
        self.project      = None
        self.texts        = None
        self.run_key      = False
        self.sprite_pbar  = Sprite2D()
        self.error_inter  = None

        engine.Debug.log("LaunchEditor: Creating Editor class...", EditorLauncher)
        self.editor = EditorApplication()

        # Создаём окно:
        self.init()

    # Создать окно:
    def init(self) -> None:
        engine.Debug.log("LaunchEditor: Initializing the window...", EditorLauncher)
        super().__init__(
            title      = "Editor Launcher",
            icon       = files.load_image("./data/icons/logo/icon-black.png"),
            size       = vec2(960, 540),
            vsync      = False,
            fps        = 30,
            visible    = False,
            titlebar   = False,
            resizable  = False,
            fullscreen = False,
            min_size   = vec2(0, 0),
            max_size   = vec2(float("inf"), float("inf")),
            samples    = 16
        )

    # Инициализируем загруженные данные:
    def init_loaded_data(self) -> None:
        # Превращаем все ложные текстуры (изображения) в нормальные настоящие текстуры:
        for dictdata in self.project.data:
            if dictdata["type"] == "texture": dictdata["data"] = Texture(dictdata["data"])
            self.window.render(0)  # Обновляем окно лаунчера редактора чтобы оно сильно не зависало.

    # Открыть редактор:
    def open_editor(self) -> None:
        self.editor.project = self.project

        # Инициализируем загруженные данные:
        engine.Debug.log("LaunchEditor: Initializing the uploaded data...", EditorLauncher)
        self.init_loaded_data()
        engine.Debug.log("LaunchEditor: Initializing the uploaded data: Done!", EditorLauncher)

        self.window.exit()  # Закрываем окно.

        # Обнуляем загрузочные данные:
        self.project.load_progbar, self.project.load_process = 0, ""

        # Инициализируем сцену:
        engine.Debug.log("LaunchEditor: Initialization of the opening scene...", EditorLauncher)
        self.editor.init_open_scene()
        engine.Debug.log("LaunchEditor: Initialization of the opening scene: Done!", EditorLauncher)

        # Запускаем редактор:
        engine.Debug.log("LaunchEditor: Launch the editor. Switching to the editor...", EditorLauncher)
        try:
            self.editor.init()
        except Exception as error:
            engine.CrashHandler(EditorApplication, error)

    # Вызывается при создании окна:
    def start(self) -> None:
        engine.Debug.log("LaunchEditor: Initializing the window: Done!", EditorLauncher)

        # Служебная информация:
        engine.Debug.log(f"Platform: {engine.gdf.get_platform()}")
        engine.Debug.log(f"Python Version: {engine.get_python_version()}")
        engine.Debug.log(f"OpenGL Version: {self.window.get_opengl_version()}")
        engine.Debug.log(f"OpenGL Renderer: {self.window.get_opengl_renderer()}")

        # Обработчик ввода:
        self.input = gdf.input.InputHandler(self.window)

        # Загружаем фон:
        self.background = Sprite2D(files.load_texture("./data/sprites/cover.png").set_pixelized())

        # Загружаем иконки:
        self.icons = {
            "exit": files.load_sprite("./data/icons/mini-icon/none.png")
        }

        # Шрифт:
        self.font = FontGenerator(files.load_font("./data/fonts/sans-serif.ttf"))

        # Загружаем данные о проекте:
        engine.Debug.log("LaunchEditor: Loading project config file...", EditorLauncher)
        self.project = engine.ProjectManager().load("./data/templates/New Project/")
        engine.Debug.log("LaunchEditor: Loading project config file: Done!", EditorLauncher)

        # Тексты:
        prjname = self.project.config["name"].strip()
        prjdesc = self.project.config["description"].strip()
        self.texts = {
            "project":     [prjname[:24]+"..." if len(prjname) > 24 else prjname, 18],
            "description": [prjdesc[:48]+"..." if len(prjdesc) > 48 else prjdesc, 9],
            "loading":     ["Loading file: ", 12],
        }

        # Преобразовываем тексты:
        for (key, val) in self.texts.items():
            self.texts[key] = self.font.get_texture_text(val[0], val[1])

        # Загружаем данные проекта:
        engine.Debug.log("LaunchEditor: Loading project data...", EditorLauncher)
        self.project.load_data()

        # Обновляем заголовок окна:
        self.window.set_title(f"Opening project: {self.project.config['name']}")

        # Отображаем окно:
        self.window.set_visible(True)

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, event_list: list) -> None:
        if self.project.error_loading is not None:
            engine.CrashHandler(core.ProjectManager.load_data, self.project.error_loading)
            sys.exit()

        # Обрабатываем нажатие на крестик:
        size = self.window.get_size()
        if gdf.utils.Intersects.point_rectangle(self.input.get_mouse_pos(), [size.x-32, 32-24, 24, 24]):
            self.exit_hovered = True
            if self.input.get_mouse_up()[0]:
                if not self.project.load_is_done:
                    engine.Debug.warning("Loading project data: Data loading was interrupted by closing the program.")
                self.window.exit()
        else: self.exit_hovered = False

        # Если мы загрузили все необходимые данные, запускаем редактор:
        if self.project.load_is_done:
            # Ключ нужен чтобы отрисовать кадр когда шкала на 100% заполнена и только потом открываем редактор.
            if self.run_key: self.open_editor()
            else: self.run_key = True

    # Вызывается каждый кадр (игровая отрисовка):
    def render(self, delta_time: float) -> None:
        self.window.clear(0, 0, 0)
        size = self.window.get_size()

        # Рисуем обложку:
        self.background.render(*-size.xy//2, *size.xy)

        # Рисуем крестик для закрытия:
        self.icons["exit"].render(size.x//2-32, size.y//2-32, 24, 24, color=[0.65]*3 if self.exit_hovered else [1.0]*3)

        # Рисуем шкалу прогресса:
        self.sprite_pbar.render(*-size.xy//2, size.x, 5, color=[0.075, 0.075, 0.075])       # Подложка фона.
        self.sprite_pbar.render(*-size.xy//2, size.x, 4, color=[0.125, 0.125, 0.125])       # Фон шкалы прогресса.
        self.sprite_pbar.render(*-size.xy//2, (min(self.project.load_progbar, 100)/100)*size.x, 4)  # Шкала прогресса.

        # Рисуем текст:

        # Название проекта:
        y = 286
        Sprite2D(self.texts["project"]).render(-size.x//2+(128-self.texts["project"].width//2), -size.y//2+y)

        # Описание проекта:
        y = 264
        Sprite2D(self.texts["description"]).render(-size.x//2+(128-self.texts["description"].width//2), -size.y//2+y)

        # Текст загрузки данных:
        x, y = 16, 36
        load_prcs = self.project.load_process
        load_prcs = "..."+load_prcs[-46:] if len(load_prcs) > 48 else load_prcs
        Sprite2D(self.texts["loading"]).render(-size.x//2+x, -size.y//2+y+self.texts["loading"].height)
        Sprite2D(self.font.get_texture_text(load_prcs, 9)).render(-size.x//2+x, -size.y//2+y)

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


# Первые шаги запуска, без которых ну никак:
def first_steps() -> None:
    # Настраивает рабочие пути каталогов для нормальной работы программы:
    if os.path.isdir(os.path.dirname(sys.argv[0])): os.chdir(os.path.dirname(sys.argv[0]))           # 1.
    if os.getcwd()[len(os.getcwd())-len("src"):] == "src": os.chdir("../")                           # 2.
    if os.path.isdir("./data/") and not os.path.isdir("./data/editor/"): os.mkdir("./data/editor/")  # 3.
    if os.path.isdir("./data/") and not os.path.isdir("./data/logs/"):   os.mkdir("./data/logs/")    # 4.

    """
        1. Изменяет текущую рабочую директорию на директорию, содержащую исполняемый файл скрипта.
        2. Проверяет, что текущая рабочая директория содержит последние символы "src".
           Если это условие выполняется, то рабочая директория изменяется на директорию выше.
           Это может быть полезно, если скрипт находится в поддиректории с именем "src", и
           нужно перейти в родительскую директорию для выполнения определённых действий.
        3. Если папки editor нет в папке data, то создаём её. В папке editor хранятся данные и настройки редактора.
        4. Если папки logs нет в папке data, то создаём её. В папке logs хранится отладка работы движка и редактора.
    """


# Запускаем редактор:
def launch_editor() -> None:
    try:
        EditorLauncher()
    except Exception as error:
        engine.CrashHandler(EditorLauncher, error)


# Основная функция:
def main() -> None:
    engine.Debug.log("Program started...")

    engine.Debug.log("First Steps: Performing the first steps of initializing the launch...")
    first_steps()
    engine.Debug.log("First Steps: Done!")

    engine.Debug.log("LaunchEditor: Launching the editor launch preparation program...")
    launch_editor()

    engine.Debug.log("Closing the program...")
    sys.exit()


# Если этот скрипт запускают:
if __name__ == "__main__":
    if os.path.isfile("./build/config.json") or "--console-support" in sys.argv:
        if "--console-support" in sys.argv: engine.Debug.init_debug()
        elif not engine.gdf.files.load_json("./build/config.json")["console-disabled"]: engine.Debug.init_debug()
    main()
