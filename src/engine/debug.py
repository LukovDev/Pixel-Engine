#
# debug.py - Создаёт код для отладки работы движка.
#


# Импортируем:
import os
from colorama import Fore
from datetime import datetime


# Глобальные переменные:
_log_list_ = []


# Структура цветов для удобства:
class ForeColors:
    # Цвета:
    WT = Fore.LIGHTWHITE_EX
    YW = Fore.LIGHTYELLOW_EX
    MT = Fore.LIGHTMAGENTA_EX
    RD = Fore.RED
    CN = Fore.LIGHTCYAN_EX
    RT = Fore.RESET


# Класс отладки:
class Debug:
    # Сообщение отладки:
    @staticmethod
    def log(message: str, by: str = "") -> None:
        global _log_list_
        сlr  = ForeColors
        time = datetime.now().strftime("%H:%M:%S")
        type = "LOG"
        by   = f"{by}: " if by else ""

        text       = f"[{time}] [{type}]: {by}{message}"
        color_text = f"{сlr.WT}[{сlr.YW}{time}{сlr.WT}] [{сlr.MT}{type}{сlr.WT}]: {сlr.CN}{by}{сlr.WT}{message}{сlr.RT}"

        _log_list_.append(text)
        print(color_text)

    # Сообщение ошибки:
    @staticmethod
    def error(message: str, by: str = "") -> None:
        global _log_list_
        сlr  = ForeColors
        time = datetime.now().strftime("%H:%M:%S")
        type = "ERROR"
        by   = f"{by}: " if by else ""

        text       = f"[{time}] [{type}]: {by}{message}"
        color_text = f"{сlr.WT}[{сlr.YW}{time}{сlr.WT}] [{сlr.RD}{type}{сlr.WT}]: {сlr.CN}{by}{сlr.RD}{message}{сlr.RT}"

        _log_list_.append(text)
        print(color_text)

    # Сообщение фатальной ошибки:
    @staticmethod
    def fatal(message: str, by: str = "") -> None:
        global _log_list_
        сlr  = ForeColors
        time = datetime.now().strftime("%H:%M:%S")
        type = "FATAL"
        by   = f"{by}: " if by else ""

        text       = f"[{time}] [{type}]: {by}{message}"
        color_text = f"{сlr.RD}[{time}] [{type}]: {by}{message}{сlr.RT}"

        _log_list_.append(text)
        print(color_text)

    # Сохранить лог:
    def save(path: str) -> None:
        global _log_list_
        fn = "debuglog"
        fp = os.path.join(os.getcwd(), path)
        if not os.path.isdir(fp): return
        try: n = max([int(f.split("-")[1].split(".")[0]) for f in os.listdir(fp) if f.startswith(fn+"-")]+[-1])+1
        except ValueError: n = 0
        with open(os.path.join(fp, f"{fn}-{1 if n == 0 else n}.log"), "w+") as f:
            for l in _log_list_: f.write(f"{l}\n")


# Автосохранение журнала при закрытии программы:
import atexit ; atexit.register(lambda: (Debug.log("Closing the program..."), Debug.save("./data/logs/")))
