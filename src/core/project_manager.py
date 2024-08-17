#
# project_manager.py - Создаёт класс для работы с файлами проекта и проектом в целом.
#


# Импортируем:
import io
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import time
import json
import pygame
import zipfile
from threading import Thread


# Исключение в работе с проектом:
class ProjectError(Exception): pass


# Исключение в работе с проектом. Проект повреждён:
class ProjectDamagedError(Exception): pass


# Класс менеджера проекта:
class ProjectManager:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.path   = ""
        self.config = None

        # Для загрузки данных проекта:
        self.loaded_data   = []
        self.bad_loaded    = []
        self.unknown_type  = []
        self.load_progbar  = 0
        self.load_process  = ""
        self.load_is_done  = False
        self.error_loading = None

    # Создать проект:
    def create(self, path: str, name: str, description: str, meta: dict) -> "ProjectManager":
        if not description: description = "My Game on the Pixel Engine."

        # Путь до папки проекта:
        project_path = os.path.join(path, name.strip())

        # Создаём папку проекта:
        os.makedirs(project_path, exist_ok=True)

        # Копируем шаблон проекта:
        with zipfile.ZipFile("./data/templates/template.pxpkg", "r") as z:
            z.extractall(project_path)

        # Копируем движок в исходный код проекта:
        with zipfile.ZipFile("./data/templates/engine.pxpkg", "r") as z:
            z.extractall(os.path.join(project_path, "src/"))

        """
            В словаре данных есть определённые типы данных:
            "text"    - Текстовый файл:   Файл который требует декодирования    (Использует функционал ядра).
            "data"    - Файл данных:      Файл который требует декодирования    (Использует функционал ядра).
            "music"   - Музыкальный файл: Файл который не требует декодирования (Использует Music).
            "sound"   - Звуковой файл:    Файл который не требует декодирования (Использует Sound).
            "texture" - Текстурный файл:  Файл который не требует декодирования (Использует Image).
            "font"    - Шрифтный файл:    Файл который не требует декодирования (Использует FontFile).
        """

        # Наш конфигурационный файл:
        config = {
            "name":        name.strip(),         # Название проекта.
            "description": description.strip(),  # Описание проекта.
            "settings": {                        # Настройки. Хранит настройки проекта.
                "title": name.strip(),
                "runapp-icon": ".proj/icons/logo/icon-black.png",
                "build-icon":  ".proj/icons/logo/icon.ico",
                "win-size": [960, 540],
                "min-win-size": [0, 0],
                "max-win-size": [-1, -1],
                "vsync": False,
                "fps": 60,
                "titlebar": True,
                "resizable": True,
                "fullscreen": False,
                "samples": 8,
                "console-disabled": True,
                "version": "v1.0",
                "company": "-"
            },
            "data": [],    # Данные. Список файлов проекта. Файлы из списка подгружаются при запуске редактора.
            "meta": meta,  # Метаданные. Хранит разные данные которые использует движок при запуске проекта.
            "cache": []    # Кэш. Хранит любую информацию, которую надо сохранить, не меняя структуру конф.файла.
        }

        # Создаём конфигурационный файл в папке проекта:
        with open(os.path.join(project_path, ".proj/project.json"), "w+", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        self.config = config
        self.path = project_path
        return self

    # Загрузить проект:
    def load(self, path: str) -> "ProjectManager":
        conf_path = os.path.join(path, ".proj/project.json")

        # Проверка, существует ли путь:
        if not os.path.isdir(path):
            raise ProjectError("The path does not exist.")

        # Проверка, существует ли папка проекта:
        if not os.path.isdir(os.path.join(path, ".proj/")):
            raise ProjectError("The specified directory is not a project.")

        # Проверка, существует ли конфигурационный файл:
        if not os.path.isfile(conf_path):
            raise ProjectDamagedError("Project configuration file was not found. Most likely, project was damaged.")

        # Загружаем конфигурационный файл:
        try:
            with open(conf_path, "r+", encoding="utf-8") as f:
                self.config = json.load(f)
        except Exception as error:
            raise ProjectDamagedError(f"Project configuration file was damaged: {error}")

        self.path = path
        return self

    # Сохранить проект:
    def save(self) -> "ProjectManager":
        # Пересоздаём конфигурационный файл:
        with open(os.path.join(self.path, ".proj/project.json", encoding="utf-8"), "w+") as f:
            json.dump(self.config, f, indent=4)
        return self

    # Загрузить данные проекта:
    def load_data(self) -> "ProjectManager":
        # Загрузка данных в отдельном потоке:
        def thread_load_files(self) -> None:
            try:
                # Обнуляем список плохих файлов:
                self.bad_loaded = []

                # Список файлов с типами и путями:
                files = self.config["data"]

                # Проход 1 - Подсчёт общего размера данных и проверка существования файлов:
                self.engine.Debug.log("Loading project data: Pass 1 - Analysis of uploaded data...", ProjectManager)
                self.load_process, total_size, valid_files = "Pass 1 - Analysis of uploaded data", 0, []
                for file_info in files:
                    for type, path in file_info.items():
                        full_path = os.path.join(self.path, path)
                        if os.path.isfile(full_path):
                            total_size += os.path.getsize(full_path)
                            valid_files.append([{type: path}, os.path.getsize(full_path)])
                        else: self.bad_loaded.append(file_info)
                        self.load_progbar += 100/len(files)
                        time.sleep((1/len(files))/4)
                if self.bad_loaded:
                    self.engine.Debug.log(
                        f"Loading project data: Pass 1: File not found: {self.bad_loaded}",
                        ProjectManager
                    )

                # Сортировка списка по размеру файла от большего к меньшему:
                valid_files = [i[0] for i in sorted(valid_files, key=lambda x: x[1], reverse=True)]

                # Обнуляем шкалу прогресса:
                self.load_progbar = 0

                # Проход 2 - Основной цикл загрузки:
                self.engine.Debug.log("Loading project data: Pass 2 - Loading data...", ProjectManager)
                self.load_process = "Pass 2 - Loading data" ; time.sleep(1)
                for file_info in valid_files:
                    for type, path in file_info.items():
                        self.load_process = path
                        full_path = os.path.join(os.getcwd(), self.path, path)
                        file_size = os.path.getsize(full_path)
                        file_data = bytearray()  # Наш загружаемый файл.
                        # Автоматический размер чанка данных (от 4кб до 64кб):
                        chunk_size = int(min(max(4096, file_size // 100), 65536))

                        self.engine.Debug.log(
                            f"Loading project data: [Type: {type} | Chunk size={chunk_size} | Loading: {full_path}]",
                            ProjectManager
                        )

                        # Загружаем файл:

                        # Текстовый файл:
                        if type == "text":
                            with open(full_path, "rb") as f:
                                while True:
                                    chunk = f.read(chunk_size)
                                    if not chunk: break
                                    file_data.extend(chunk)
                                    self.load_progbar += (len(chunk)/total_size)*100
                            self.loaded_data.append({"type": type, "path": path, "data": file_data.decode("utf-8")})

                        # Файл данных:
                        elif type == "data":
                            with open(full_path, "rb") as f:
                                while True:
                                    chunk = f.read(chunk_size)
                                    if not chunk: break
                                    file_data.extend(chunk)
                                    self.load_progbar += (len(chunk)/total_size)*100
                            self.loaded_data.append({"type": type, "path": path, "data": file_data})

                        # Музыкальный файл:
                        elif type == "music":
                            with open(full_path, "rb") as f:
                                while True:
                                    chunk = f.read(chunk_size)
                                    if not chunk: break
                                    file_data.extend(chunk)
                                    self.load_progbar += (len(chunk)/total_size)*100
                            music = self.engine.gdf.audio.Music().load(io.BytesIO(file_data))
                            self.loaded_data.append({"type": type, "path": path, "data": music})

                        # Звуковой файл:
                        elif type == "sound":
                            sound = self.engine.gdf.audio.Sound().load(full_path)
                            self.load_progbar += (file_size/total_size)*100
                            self.loaded_data.append({"type": type, "path": path, "data": sound})

                        # Файл изображения:
                        elif type == "texture":
                            with open(full_path, "rb") as f:
                                while True:
                                    chunk = f.read(chunk_size)
                                    if not chunk: break
                                    file_data.extend(chunk)
                                    self.load_progbar += (len(chunk)/total_size)*100
                            self.load_process = f"Converting: {os.path.basename(full_path)}"
                            image = self.engine.gdf.graphics.Image((0, 0), pygame.image.load(io.BytesIO(file_data)))
                            self.loaded_data.append({"type": type, "path": path, "data": image})

                        # Файл шрифта:
                        elif type == "font":
                            font = self.engine.gdf.graphics.FontFile(full_path)
                            with open(full_path, "rb") as f:
                                while True:
                                    chunk = f.read(chunk_size)
                                    if not chunk: break
                                    file_data.extend(chunk)
                                    self.load_progbar += (len(chunk)/total_size)*100
                            font.data = file_data
                            self.loaded_data.append({"type": type, "path": path, "data": font})

                        # Неизвестный тип файла:
                        else: self.unknown_type.append(file_info)

                if self.unknown_type:
                    self.engine.Debug.log(f"Loading project data: Unknown types: {self.unknown_type}", ProjectManager)

                # Говорим что всё загружено:
                self.engine.Debug.log("Loading project data: Done!", ProjectManager)
                self.load_progbar = 100
                self.load_process = "Done!"
                time.sleep(1.0)
                self.load_process = "Preparation of uploaded data..."
                self.load_is_done = True
            except Exception as error:
                self.engine.Debug.error(f"Loading project data: ERROR: {error}", ProjectManager)
                self.error_loading = error

        # Запускаем загрузку данных:
        Thread(target=thread_load_files, args=(self,), daemon=True).start()
