#
# object.py - Создаёт класс игрового объекта.
#


# Импортируем:
from .gdf.math import *
from .component import Components


# Класс игрового объекта:
class GameObject:
    def __init__(self, id: int, name: str, components: list = None) -> None:
        self.id         = int(id)
        self.name       = name.strip()
        self.components = components if components is not None else []

    # Добавить компонент в список компонентов:
    def add(self, component: Components | list) -> None:
        if isinstance(component, Components): component = [component]
        for comp in component:
            if comp not in self.components:
                self.components.append(component)

    # Удалить компонент из списка компонентов:
    def remove(self, component: Components | list) -> None:
        if isinstance(component, Components): component = [component]
        for comp in component:
            if comp in self.components:
                self.components.remove(component)
