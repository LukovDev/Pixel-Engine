#
# component.py - Создаёт классы-компоненты для игрового объекта.
#


# Импортируем:
from .gdf.graphics import *
from .gdf.math import *


# Класс компонентов:
class Components:
    # Родительский класс для всех компонентов:
    class Component:
        # Получить словарь параметров:
        def get_parameters(self) -> dict: return {}

        def start(self) -> None: pass

        def update(self, delta_time: float) -> None: pass

        def render(self, delta_time: float) -> None: pass

        def resize(self, width: int, height: int) -> None: pass

        def destroy(self) -> None: pass

    # 2D Преобразование:
    class Transform2D(Component):
        def __init__(self, project_manager, position: vec2, scale: vec2, angle: float) -> None:
            self._projmng_ = project_manager  # Менеджер проекта.
            self.position  = vec2(position)   # Позиция.
            self.scale     = vec2(scale)      # Размер.
            self.angle     = float(angle)     # Угол наклона.

        # Получить словарь параметров:
        def get_parameters(self) -> dict:
            return {
                "position": list(self.position.xy),
                "scale":    list(self.scale.xy),
                "angle":    float(self.angle)
            }

    # 2D Спрайт:
    class Sprite2D(Component):
        def __init__(self, project_manager, path: str) -> None:
            self._projmng_ = project_manager                # Менеджер проекта.
            self.path      = path                           # Путь до файла.
            self._texture_ = self._projmng_.get_data(path)  # Получить файл из пути.

        # Получить словарь параметров:
        def get_parameters(self) -> dict:
            return {
                "path": str(self.path)
            }
