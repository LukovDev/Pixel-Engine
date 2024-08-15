#
# project_manager.py - Создаёт класс для работы с файлами проекта и проектом в целом.
#


# Импортируем:
import os
import json


# Исключение в работе с проектом:
class ProjectError(Exception): pass


# Исключение в работе с проектом. Проект повреждён:
class ProjectDamagedError(Exception): pass


# Класс менеджера проекта:
class ProjectManager:
    def __init__(self) -> None:
        self.config = None
        self.path = ""

    # Создать проект:
    def create(self, path: str, name: str, description: str, meta: dict) -> "ProjectManager":
        if not description: description = "My Game on the Pixel Engine game engine."

        # Создаём папку чтобы пометить что она является проектом:
        os.makedirs(os.path.join(path, ".proj/"), exist_ok=True)

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

        # Создаём конфигурационный файл:
        with open(os.path.join(path, ".proj/project.json"), "w+", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        self.config = config
        self.path = path
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
        with open(conf_path, "r+", encoding="utf-8") as f:
            self.config = json.load(f)

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
        return self