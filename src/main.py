#
# main.py - Основной запускаемый файл программы.
#


# Импортируем:
import os
import sys
import time
from threading import Thread

import core
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
        self.texts        = None
        self.progress_bar = 0.0
        self.run_key      = False
        self.load_process = ""
        self.sprite_pbar  = Sprite2D()
        self.editor       = EditorApplication()
        self.error_inter  = None

        # Создаём окно:
        self.init()

    # Создать окно:
    def init(self) -> None:
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

    # Загрузка данных в отдельном потоке:
    def thread_load_files(self) -> None:
        try:
            # Если нет данных для загрузки:
            if len(self.project.config["data"]) == 0:
                self.progress_bar = 100
                self.load_process = "Done!"
                return

            # Шаг шкалы прогресса с каждым новым файлом:
            increment = 100 / len(self.project.config["data"])

            # Обнуляем список плохих файлов:
            self.editor.loaded_data["bad-loaded"] = []

            # Получаем пути к файлам с их размерами:
            files_with_sizes = []
            for file in self.project.config["data"]:
                file_path = os.path.join(self.project.path, file)
                if not os.path.isfile(file_path): self.editor.loaded_data["bad-loaded"].append(file) ; continue
                files_with_sizes.append((file, os.path.getsize(file_path)))

            # Проходимся по списку файлов на загрузку:
            for file in [file for file, _ in sorted(files_with_sizes, key=lambda x: x[1], reverse=True)]:
                self.load_process = file
                file_path = os.path.join(self.project.path, file)
                file_size = os.path.getsize(file_path)
                chunk_size = int(min(max(4096, file_size // 100), 65536))  # Автоматический размер. Чанк от 1КБ до 64КБ.
                file_data = bytearray()  # Наш загружаемый файл.

                # Если файл не существует:
                if not os.path.isfile(file_path):
                    self.editor.loaded_data["bad-loaded"].append(file)
                    self.load_process = f"FILE NOT FOUND: {file}"
                    continue

                # Загружаем файл:
                with open(file_path, "rb+") as f:
                    loaded_size = 0  # Сколько уже загружено.
                    while True:
                        chunk = f.read(chunk_size)  # Загружаем по chunk_size данных.
                        if not chunk: break         # Если кусок данных пуст, то прерываем чтение.
                        file_data.extend(chunk)     # Добавляем кусок данных в наш загружаемый файл.
                        loaded_size += len(chunk)
                        self.progress_bar += (len(chunk)/file_size)*increment

                # Сохраняем данные в пакете загруженных данных в редакторе:
                self.editor.loaded_data[file] = file_data

            # Если список плохих файлов не пуст:
            if len(self.editor.loaded_data["bad-loaded"]) > 0:
                self.progress_bar += increment * len(self.editor.loaded_data["bad-loaded"])

            # Говорим что всё загружено:
            self.load_process = "Done!"
        except Exception as error:
            self.error_inter = [self.thread_load_files, error]

    # Открыть редактор:
    def open_editor(self) -> None:
        time.sleep(1.0)  # Небольшая задержка чтобы показать что всё готово к запуску.

        self.window.set_visible(False)  # Скрываем это окно.
        self.window.clear(0, 0, 0)      # Очищаем окно для редактора.

        # Передаём данные проекта редактору:
        self.editor.init_project_data(self.project)

        # Инициализируем сцену:
        self.editor.init_open_scene()

        # Запускаем редактор:
        try:
            self.editor.init()
        except Exception as error:
            engine.CrashHandler(EditorApplication, error)

        # Завершаем работу программы:
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

        # Шрифт:
        self.font = FontGenerator("./data/fonts/sans-serif.ttf")

        # Загружаем данные о проекте:
        self.project = core.ProjectManager().load("./data/templates/New Project/")

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

        # Запускаем отдельный поток для загрузки данных:
        Thread(target=self.thread_load_files, daemon=True).start()

        # Обновляем заголовок окна:
        self.window.set_title(f"Opening project: {self.project.config['name']}")

        # Отображаем окно:
        self.window.set_visible(True)

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, event_list: list) -> None:
        if self.error_inter is not None:
            engine.CrashHandler(*self.error_inter)
            sys.exit()

        # Если мы загрузили все необходимые данные, запускаем редактор:
        if self.progress_bar >= 100:
            # Ключ нужен чтобы отрисовать кадр когда шкала на 100% заполнена и только потом открываем редактор.
            if self.run_key: self.open_editor()
            else: self.run_key = True

        # Обрабатываем нажатие на крестик:
        size = self.window.get_size()
        if gdf.utils.Intersects.point_rectangle(self.input.get_mouse_pos(), [size.x-32, 32-24, 24, 24]):
            self.exit_hovered = True
            if self.input.get_mouse_up()[0]: self.window.exit()
        else: self.exit_hovered = False

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
        self.sprite_pbar.render(*-size.xy//2, (min(self.progress_bar, 100)/100)*size.x, 4)  # Шкала прогресса.

        # Рисуем текст:

        # Название проекта:
        Sprite2D(self.texts["project"]).render(-size.x//2+(128-self.texts["project"].width//2), -size.y//2+299)

        # Описание проекта:
        Sprite2D(self.texts["description"]).render(-size.x//2+(128-self.texts["description"].width//2), -size.y//2+275)

        # Описание проекта:
        load_prcs = "..."+self.load_process[-46:] if len(self.load_process) > 48 else self.load_process
        Sprite2D(self.texts["loading"]).render(-size.x//2+16, -size.y//2+48)
        Sprite2D(self.font.get_texture_text(load_prcs, 9)).render(-size.x//2+16, -size.y//2+36)

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

    """
        1. Изменяет текущую рабочую директорию на директорию, содержащую исполняемый файл скрипта.
        2. Проверяет, что текущая рабочая директория содержит последние символы "src".
           Если это условие выполняется, то рабочая директория изменяется на директорию выше.
           Это может быть полезно, если скрипт находится в поддиректории с именем "src", и
           нужно перейти в родительскую директорию для выполнения определённых действий.
        3. Если папки editor нет в папке data, то создаём её. В папке editor хранятся данные и настройки редактора.
    """


# Запускаем редактор:
def launch_editor() -> None:
    try:
        EditorLauncher()
    except Exception as error:
        engine.CrashHandler(EditorLauncher, error)


# Основная функция:
def main() -> None:
    first_steps()
    launch_editor()


# Если этот скрипт запускают:
if __name__ == "__main__":
    main()
