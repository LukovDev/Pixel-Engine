#
# scene_manager.py - Создаёт класс для работы со сценами игры.
#


# Импортируем:


# Класс менеджера сцен:
class SceneManager:
    def __init__(self) -> None:
        self.scenes          = []
        self._current_scene_ = 0

    # Загрузить все сцены:
    def load_scenes(self, scenes: list)
