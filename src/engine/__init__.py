#
# engine - В основном является обёрткой ядра gdf и реализует дополнительный функционал.
#


# Импортируем:
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


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


# Импортируем скрипты:
from . import crash_handler


# Импортируем основной функционал из скриптов:
from .crash_handler import CrashHandler
