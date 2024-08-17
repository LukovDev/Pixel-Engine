#
# editor_const.py - Хранит разные константы и переменные для редактора.
#


# Настройки редактора:
config = {
    # Настройки окна:
    "size":       [960, 540],
    "vsync":      False,
    "fps":        60,
    "titlebar":   True,
    "resizable":  True,
    "fullscreen": False,
    "min-size":   [640, 360],
    "max-size":   [float("inf"), float("inf")],
    "samples":    16,
}


# Общие настройки:
settings = {
    "clear-color": [24/255, 28/255, 34/255],
    "meter":       1,
}
