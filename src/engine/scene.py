#
# scene.py - Создаёт класс игровой сцены.
#


# Импортируем:
import traceback
from .debug import Debug
from .gdf.graphics import scene
from .object import GameObject


# Класс игровой сцены:
class GameScene(scene.Scene):
    def __init__(self, id: int, name: str, objects: list = None) -> None:
        self.id      = int(id)
        self.name    = name.strip()
        self.objects = objects if objects is not None else []
        self.objects = [self.objects] if not isinstance(self.objects, list) else self.objects

    # Добавить объект в список объектов:
    def add(self, object: GameObject | list) -> None:
        for obj in [object] if not isinstance(object, list) else object:
            if obj not in self.objects:
                self.objects.append(obj)

    # Удалить объект из списка объектов:
    def remove(self, object: GameObject | list) -> None:
        for obj in [object] if not isinstance(object, list) else object:
            if obj in self.objects:
                self.objects.remove(obj)

    # Вызывается при переключении на эту сцену:
    def start(self) -> None:
        for obj in self.objects:
            for comp in obj.components:
                try: comp.start()
                except Exception as error:
                    lineno = traceback.extract_tb(error.__traceback__)[-1].lineno
                    Debug.error(
                        f"Scene \"{self.name}\" [id: {self.id}]: "
                        f"Error starting component: \"{type(comp).__name__}\" from object: "
                        f"\"{obj.name}\" [id: {obj.id}]: {error} [line: {lineno}]"
                    )

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, event_list: list) -> None:
        for obj in self.objects:
            for comp in obj.components:
                try: comp.update(delta_time)
                except Exception as error:
                    lineno = traceback.extract_tb(error.__traceback__)[-1].lineno
                    Debug.error(
                        f"Scene \"{self.name}\" [id: {self.id}]: "
                        f"Error updating component: \"{type(comp).__name__}\" from object: "
                        f"\"{obj.name}\" [id: {obj.id}]: {error} [line: {lineno}]"
                    )

    # Вызывается каждый кадр (игровая отрисовка):
    def render(self, delta_time: float) -> None:
        for obj in self.objects:
            for comp in obj.components:
                try: comp.render(delta_time)
                except Exception as error:
                    lineno = traceback.extract_tb(error.__traceback__)[-1].lineno
                    Debug.error(
                        f"Scene \"{self.name}\" [id: {self.id}]: "
                        f"Error rendering component: \"{type(comp).__name__}\" from object: "
                        f"\"{obj.name}\" [id: {obj.id}]: {error} [line: {lineno}]"
                    )

    # Вызывается при изменении размера окна:
    def resize(self, width: int, height: int) -> None:
        for obj in self.objects:
            for comp in obj.components:
                try: comp.resize(width, height)
                except Exception as error:
                    lineno = traceback.extract_tb(error.__traceback__)[-1].lineno
                    Debug.error(
                        f"Scene \"{self.name}\" [id: {self.id}]: "
                        f"Error resizing component: \"{type(comp).__name__}\" from object: "
                        f"\"{obj.name}\" [id: {obj.id}]: {error} [line: {lineno}]"
                    )

    # Вызывается при разворачивании окна:
    def show(self) -> None:
        pass

    # Вызывается при сворачивании окна:
    def hide(self) -> None:
        pass

    # Вызывается при закрытии сцены:
    def destroy(self) -> None:
        for obj in self.objects:
            for comp in obj.components:
                try: comp.destroy()
                except Exception as error:
                    lineno = traceback.extract_tb(error.__traceback__)[-1].lineno
                    Debug.error(
                        f"Scene \"{self.name}\" [id: {self.id}]: "
                        f"Error destroy component: \"{type(comp).__name__}\" from object: "
                        f"\"{obj.name}\" [id: {obj.id}]: {error} [line: {lineno}]"
                    )
