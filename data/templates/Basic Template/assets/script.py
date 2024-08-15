#
# script.py
#


# Импортируем:
import engine
from engine import gdf


# Вызывается при запуске сцены:
def start(window) -> None:
    print("Start called.")


# Вызывается перед обновлением сцены:
def update(window, delta_time: float) -> None:
    print("Update called.")


# Вызывается после отрисовки сцены:
def render(window, delta_time: float) -> None:
    print("Render called.")


# Вызывается при изменении размера окна:
def resize(window, width: int, height: int) -> None:
    print("ReSize called.")


# Вызывается при разворачивании окна:
def show(window) -> None:
    print("Show called.")


# Вызывается при сворачивании окна:
def hide(window) -> None:
    print("Hide called.")


# Вызывается закрытии сцены:
def destroy(window) -> None:
    print("Destroy called.")
