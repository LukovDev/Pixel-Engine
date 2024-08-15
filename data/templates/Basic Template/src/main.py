#
# main.py - Основной запускаемый файл программы.
#


# Импортируем:
import os
import sys
import json
import pkgutil
import engine
from engine import *


# Ошибка во время загрузки инициализационных данных игры:
class GameLoadInitDataError(Exception): pass


# Ошибка во время работы игры:
class GameRuntimeError(Exception): pass


# Класс игры:
class GameClass(gdf.graphics.Window):
    def __init__(self) -> None:
        self.init_path = ""
        self.config = {}

        # Загружаем конфигурационный файл проекта:
        if os.path.isdir("./.proj/") and os.path.isfile("./.proj/project.json"):
            # Выполняется если запуск происходит из исходного кода.
            self.init_path = "./.proj/"
            with open("./.proj/project.json", "r+") as f: self.config = json.load(f)
        else:
            try:
                with open(os.path.join(sys._MEIPASS, ".proj/project.json"), "r+") as f: self.config = json.load(f)
                self.init_path = os.path.join(sys._MEIPASS, ".proj/")
            except Exception as error:
                raise GameLoadInitDataError(f"The game cannot find its initialization data: {error}")

        # Создаём окно и переходим в игровой цикл:
        self.init()

    # Создать окно:
    def init(self) -> None:
        runapp_icon_path = self.config["settings"]["runapp-icon"]
        if runapp_icon_path[0] == "/" or runapp_icon_path[0] == "\\": runapp_icon_path = runapp_icon_path[1:]

        max_win_size = self.config["settings"]["max-win-size"]
        if max_win_size[0] == -1: max_win_size[0] = float("inf")
        if max_win_size[1] == -1: max_win_size[1] = float("inf")

        super().__init__(
            title      = self.config["settings"]["title"],
            icon       = files.load_image(os.path.join(self.init_path, runapp_icon_path)),
            size       = vec2(*self.config["settings"]["win-size"]),
            vsync      = self.config["settings"]["vsync"],
            fps        = self.config["settings"]["fps"],
            visible    = True,
            titlebar   = self.config["settings"]["titlebar"],
            resizable  = self.config["settings"]["resizable"],
            fullscreen = self.config["settings"]["fullscreen"],
            min_size   = vec2(*self.config["settings"]["min-win-size"]),
            max_size   = vec2(*max_win_size),
            samples    = self.config["settings"]["samples"]
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

        ...

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
    if os.path.isdir(os.path.dirname(sys.argv[0])): os.chdir(os.path.dirname(sys.argv[0]))  # 1.
    if os.getcwd()[len(os.getcwd())-len("src"):] == "src": os.chdir("../")                  # 2.

    """
        1. Изменяет текущую рабочую директорию на директорию, содержащую исполняемый файл скрипта.
        2. Проверяет, что текущая рабочая директория содержит последние символы "src".
           Если это условие выполняется, то рабочая директория изменяется на директорию выше.
           Это может быть полезно, если скрипт находится в поддиректории с именем "src", и
           нужно перейти в родительскую директорию для выполнения определённых действий.
    """


# Запускаем игру:
def launch_game() -> None:
    try:
        GameClass()
    except Exception as error:
        engine.CrashHandler(GameClass, error)


# Основная функция:
def main() -> None:
    first_steps()
    launch_game()


# Если этот скрипт запускают:
if __name__ == "__main__":
    main()
