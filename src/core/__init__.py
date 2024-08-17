#
# core - Ядро окон. Хранит разный функционал для разных окон движка.
#


# Импортируем скрипты:
from . import editor_const
from . import project_manager


# Импортируем основной функционал из скриптов:
from .project_manager import ProjectError, ProjectDamagedError, ProjectManager
