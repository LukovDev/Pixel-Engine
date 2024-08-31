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

from . import gdf
from .debug import Debug
from .scene import GameScene
from .object import GameObject
from .component import Components


# Класс загруженных данных проекта:
class ProjectData:
    def __init__(self, path: str, type: str, data: any) -> None:
        self.path = path
        self.type = type
        self.data = data


# Исключение в работе с проектом:
class ProjectError(Exception): pass


# Исключение в работе с проектом. Проект повреждён:
class ProjectDamagedError(Exception): pass


# Класс менеджера проекта:
class ProjectManager:
    def __init__(self) -> None:
        self.path   = ""
        self.config = None

        # Для загрузки данных сцен:
        self.scenes      = []
        self.bad_scenes  = []
        self.bad_objects = []

        # Для загрузки данных проекта:
        self.data         = []
        self.bad_loaded   = []
        self.unknown_type = []

        # В целом для загрузки всех данных проекта:
        self.load_progbar  = 0
        self.load_process  = ""
        self.load_stage    = [0, 3]
        self.load_is_done  = False
        self.error_loading = None

    # Создать проект:
    def create(self, path: str, name: str, description: str, meta: dict) -> "ProjectManager":
        if not description: description = "My Game on the Pixel Engine."

        # Путь до папки проекта:
        project_path = os.path.join(path, name.strip())

        # Создаём папку проекта:
        os.makedirs(project_path, exist_ok=True)

        # Проверяем, существует ли пакет шаблона проекта:
        if not os.path.isfile("./data/templates/template.pxpkg"):
            raise ProjectError(
                "The required template package (template.pxpkg) is missing to generate the project. "
                "The editor files are corrupted. Recommended to reinstall the program."
            )

        # Проверяем, существует ли пакет движка проекта:
        if not os.path.isfile("./data/templates/engine.pxpkg"):
            raise ProjectError(
                "The required engine package (engine.pxpkg) is missing to generate the project. "
                "The editor files are corrupted. Recommended to reinstall the program."
            )

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
            "image"   - Файл изображения: Файл который не требует декодирования (Использует Image).
            "texture" - Текстурный файл:  Файл который не требует декодирования (Использует Image а потом Texture).
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
            "scenes": [  # Список сцен.
                {
                    "id": 0,               # Идентификатор сцены и её порядковый номер.
                    "name": "Main Scene",  # Название сцены.
                    "objects": []          # Список объектов.
                }
            ],
            "data": [],    # Данные. Список файлов проекта. Файлы из списка подгружаются при запуске редактора.
            "meta": meta,  # Метаданные. Хранит разные данные которые использует движок при запуске проекта.
            "cache": []    # Кэш. Хранит любую информацию, которую надо сохранить, не меняя структуру конфиг файла.
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
        # Проверяем, существует ли проект:
        if not os.path.isdir(self.path):
            raise ProjectError("The project could not be saved. The project folder has been moved or deleted.")

        # Проверяем, существует ли проект:
        if not os.path.isdir(os.path.join(self.path, ".proj")):
            raise ProjectError("The project could not be saved. The project folder is corrupted.")

        Debug.log("Saving project config...", ProjectManager)

        # Сохраняем данные о сценах, объектах и компонентах (конвертируя данные в json структуру):
        try:
            Debug.log("Saving project config: Converting scenes and its contents to json format...", ProjectManager)
            scenes = []
            for scn in self.scenes:
                # Получаем данные из сцены:
                scene_data = scn.__dict__.copy()

                # Не добавляем скрытые переменны (по типу _objects_dict_):
                scene_data = {i[0]: i[1] for i in scene_data.items() if i[0].__class__ == str and i[0][0] != "_"}

                objects = []
                Debug.log(
                    f"Saving project config: Converting scenes: Scene: \"{scn.name}\" [{scn.id}]...",
                    ProjectManager)

                for obj in scn.objects:
                    Debug.log(
                        f"Saving project config: Converting scenes: Scene: \"{scn.name}\" [{scn.id}]: "
                        f"Converting GameObject: \"{obj.name}\" [{obj.id}]...", ProjectManager)

                    object_data = obj.__dict__.copy()
                    # Не добавляем скрытые переменны (по типу _projmng_):
                    object_data = {i[0]: i[1] for i in object_data.items() if i[0].__class__ == str and i[0][0] != "_"}

                    components = {comp.__class__.__name__: comp.get_parameters() for comp in obj.components}
                    object_data["components"] = components
                    objects.append(object_data)

                    Debug.log(
                        f"Saving project config: Converting scenes: Scene: \"{scn.name}\" [{scn.id}]: "
                        f"Converting GameObject: \"{obj.name}\" [{obj.id}]: Done!", ProjectManager)

                # Добавляем сцену в список сцен:
                scene_data["objects"] = objects
                scenes.append(scene_data)

                Debug.log(
                    f"Saving project config: Converting scenes: Scene: \"{scn.name}\" [{scn.id}]: Done!",
                    ProjectManager)

            # Сохраняем сцены в конфигурации:
            self.config["scenes"] = scenes
        except Exception as error:
            errtext = f"An error occurred when converting scenes: {error.__class__.__name__}: {error}"
            Debug.error(errtext)
            raise ProjectError(errtext)

        # Загружаем старые данные, чтобы если при сохранении новых данных возникнет ошибка, записать старые данные:
        with open(os.path.join(self.path, ".proj/project.json"), "r+", encoding="utf-8") as f:
            old_config = json.load(f)

        # Пересоздаём конфигурационный файл:
        try:
            # Сохраняем новые данные:
            with open(os.path.join(self.path, ".proj/project.json"), "w+", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)

            Debug.log("Saving project config: Done!", ProjectManager)
        except Exception as error:
            # Записываем старые данные:
            with open(os.path.join(self.path, ".proj/project.json"), "w+", encoding="utf-8") as f:
                json.dump(old_config, f, indent=4)

            errtext = f"An error occurred while saving the project configuration: {error.__class__.__name__}: {error}"
            Debug.error(errtext)
            raise ProjectError(errtext)

        return self

    # Загрузить все данные проекта:
    def load_all_data(self) -> "ProjectManager":
        pass

    # Загрузить данные проекта:
    def load_data(self) -> "ProjectManager":
        # Загрузка данных в отдельном потоке:
        def thread_load_files() -> None:
            try:
                # Обнуляем список плохих файлов:
                self.bad_loaded = []

                # Обнуляем шкалу прогресса:
                self.load_progbar  = 0
                self.load_stage[0] = 1

                # Проход 1 - Генерация сцен, объектов и компонентов:
                Debug.log("Loading project data: Stage 1: Scene generation...", ProjectManager)
                self.load_process = "Stage 1: Scene generation..." ; time.sleep(0.25)
                for scene in self.config["scenes"]:
                    try:
                        Debug.log(
                            f"Loading project data: Stage 1: Scene generation: "
                            f"\"{scene['name']}\" [{scene['id']}]", ProjectManager)

                        # Создаём сцену:
                        gamescene = GameScene(scene["id"], scene["name"])

                        # Проходимся по объектам:
                        for obj in scene["objects"]:
                            try:
                                Debug.log(
                                    f"Loading project data: Stage 1: Scene generation: Creating object: "
                                    f"\"{obj['name']}\" [{obj['id']}]", ProjectManager)

                                # Но для начала надо сгенерировать список компонентов объекта:
                                components = []
                                for cname, cparams in obj["components"].items():
                                    components.append(getattr(Components, cname)(self, **cparams))

                                # Создаём игровой объект и добавляем в сцену:
                                gamescene.add(GameObject(*[v for k, v in obj.items() if k != "components"], components))
                            except Exception as error:
                                self.bad_objects.append({"scene-id": scene["id"], "object-id": obj["id"]})
                                Debug.error(
                                    f"Loading project data: Stage 1: Scene generation: "
                                    f"Creating object: ERROR: {error.__class__.__name__}: {error}",
                                    ProjectManager)

                        # Добавляем сцену в список сцен:
                        self.scenes.append(gamescene)
                    except Exception as error:
                        self.bad_scenes.append({"scene-id": scene["id"]})
                        Debug.error(
                            f"Loading project data: Stage 1: Scene generation: "
                            f"ERROR: {error.__class__.__name__}: {error}",
                            ProjectManager)
                    self.load_progbar += 100/len(self.config["scenes"])
                    time.sleep((1/len(self.config["scenes"]))/4)

                # Обнуляем шкалу прогресса:
                self.load_progbar  = 0
                self.load_stage[0] = 2

                # Проход 2 - Подсчёт общего размера данных и проверка существования файлов:
                Debug.log("Loading project data: Stage 2 - Analysis of uploaded data...", ProjectManager)
                self.load_process, total_size, valid_files = "Stage 2 - Analysis of uploaded data", 0, []
                for file_info in self.config["data"]:
                    for type, path in file_info.items():
                        full_path = os.path.join(self.path, path)
                        if os.path.isfile(full_path):
                            total_size += os.path.getsize(full_path)
                            valid_files.append([{type: path}, os.path.getsize(full_path)])
                        else: self.bad_loaded.append(file_info)
                        self.load_progbar += 100/len(self.config["data"])
                        time.sleep((1/len(self.config["data"]))/4)
                if self.bad_loaded:
                    Debug.error(
                        f"Loading project data: Stage 2: File not found: {self.bad_loaded}",
                        ProjectManager
                    )

                # Сортировка списка по размеру файла от большего к меньшему:
                valid_files = [i[0] for i in sorted(valid_files, key=lambda x: x[1], reverse=True)]

                # Обнуляем шкалу прогресса:
                self.load_progbar  = 0
                self.load_stage[0] = 3

                # Проход 3 - Основной цикл загрузки:
                Debug.log("Loading project data: Stage 3 - Loading data...", ProjectManager)
                self.load_process = "Stage 3 - Loading data"
                for file_info in valid_files:
                    for type, path in file_info.items():
                        self.load_process = path
                        full_path = os.path.join(os.getcwd(), self.path, path)
                        file_size = os.path.getsize(full_path)
                        file_data = bytearray()  # Наш загружаемый файл.
                        # Автоматический размер чанка данных (от 4кб до 64кб):
                        chunk_size = int(min(max(4096, file_size // 100), 65536))

                        Debug.log(
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
                            self.data.append({"type": type, "path": path, "data": file_data.decode("utf-8")})

                        # Файл данных:
                        elif type == "data":
                            with open(full_path, "rb") as f:
                                while True:
                                    chunk = f.read(chunk_size)
                                    if not chunk: break
                                    file_data.extend(chunk)
                                    self.load_progbar += (len(chunk)/total_size)*100
                            self.data.append({"type": type, "path": path, "data": file_data})

                        # Музыкальный файл:
                        elif type == "music":
                            with open(full_path, "rb") as f:
                                while True:
                                    chunk = f.read(chunk_size)
                                    if not chunk: break
                                    file_data.extend(chunk)
                                    self.load_progbar += (len(chunk)/total_size)*100
                            music = gdf.audio.Music().load(io.BytesIO(file_data))
                            self.data.append({"type": type, "path": path, "data": music})

                        # Звуковой файл:
                        elif type == "sound":
                            sound = gdf.audio.Sound().load(full_path)
                            self.load_progbar += (file_size/total_size)*100
                            self.data.append({"type": type, "path": path, "data": sound})

                        # Файл изображения / текстуры (во время загрузки они одинаковые):
                        elif type == "image" or type == "texture":
                            with open(full_path, "rb") as f:
                                while True:
                                    chunk = f.read(chunk_size)
                                    if not chunk: break
                                    file_data.extend(chunk)
                                    self.load_progbar += (len(chunk)/total_size)*100
                            self.load_process = f"Converting: {os.path.basename(full_path)}"
                            Debug.log(
                                f"Loading project data: Converting: {os.path.basename(full_path)}...", ProjectManager)
                            image = gdf.graphics.Image((0, 0), pygame.image.load(io.BytesIO(file_data)))
                            self.data.append({"type": type, "path": path, "data": image})

                        # Файл шрифта:
                        elif type == "font":
                            font = gdf.graphics.FontFile(full_path)
                            with open(full_path, "rb") as f:
                                while True:
                                    chunk = f.read(chunk_size)
                                    if not chunk: break
                                    file_data.extend(chunk)
                                    self.load_progbar += (len(chunk)/total_size)*100
                            font.data = file_data
                            self.data.append({"type": type, "path": path, "data": font})

                        # Неизвестный тип файла:
                        else: self.unknown_type.append(file_info)

                if self.unknown_type:
                    Debug.log(f"Loading project data: Unknown types: {self.unknown_type}", ProjectManager)

                # Говорим что всё загружено:
                Debug.log("Loading project data: Done!", ProjectManager)
                self.load_progbar = 100
                self.load_process = "Done!" ; time.sleep(0.5)
                self.load_process = "Preparation of uploaded data..."
                self.load_is_done = True
            except Exception as error:
                Debug.error(f"Loading project data: ERROR: {error}", ProjectManager)
                self.error_loading = error

        # Запускаем загрузку данных:
        Thread(target=thread_load_files, daemon=True).start()

    # Получить загруженные данные из проекта используя путь:
    def get_data(self, path: str) -> ProjectData:
        data_dict = {os.path.normpath(d["path"]): d for d in self.data}
        path = os.path.normpath(path)
        if path in data_dict:
            return ProjectData(path, data_dict[path]["type"], data_dict[path]["data"])
        return ProjectData("", "unknown", None)
