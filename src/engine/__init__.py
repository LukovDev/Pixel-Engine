#
# engine - В основном является обёрткой ядра gdf и реализует дополнительный функционал.
#


# Импортируем:
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import platform


# Импортируем ядро:
from . import gdf
from .gdf.audio import *
from .gdf.graphics import *
from .gdf.net import *
from .gdf.physics import *
from .gdf.controllers import *
from .gdf import files
from .gdf import math
from .gdf import input
from .gdf import utils


# Получить версию движка:
def get_version() -> str: return "v0.1"


# Получить версию питона:
def get_python_version() -> str: return platform.python_version()


# Получить мета данные для проекта:
def get_meta_info() -> dict:
    return {
        "engine-version": get_version(),
        "gdf-version": gdf.get_version(),
        "editor-version": "v0.1"
    }


# Импортируем скрипты:
from . import component
from . import crash_handler
from . import debug
from . import discord
from . import object
from . import project_manager
from . import scene
from . import scene_manager


# Импортируем основной функционал из скриптов:
from .component       import Components
from .crash_handler   import CrashHandler
from .debug           import Debug
from .discord         import DiscordRPCEngine
from .object          import GameObject
from .project_manager import ProjectData, ProjectError, ProjectDamagedError, ProjectManager
from .scene           import GameScene
from .scene_manager   import SceneManager
