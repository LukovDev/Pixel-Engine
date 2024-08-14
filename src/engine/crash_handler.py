#
# crash_handler.py - Создаёт класс обработчика ошибок движка.
#


# Импортируем:
if True:
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    import pygame
    import tkinter as tk
    import platform
    import traceback
    from . import gdf
    from . import get_version


# Обработчик ошибок движка:
class CrashHandler:
    def __init__(self, source: str, error: Exception, title_text: str = "Pixel Engine has been Crashed!") -> None:
        try: pygame.quit()
        except Exception: pass

        window_title = "CRASH HANDLER"
        icon_path    = "./data/icons/logo/icon.ico"

        self.window = tk.Tk()
        self.window.clipboard_clear()

        # Настройка окна:
        width, height = (640, 360)
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y-30}")
        self.window.resizable(False, False)
        self.window.title(window_title)
        try: self.window.iconbitmap(icon_path)
        except Exception: pass
        self.window["bg"] = self.rgb_hex(20, 22, 28)

        # Получение текста из трассировки ошибки:
        traceback_text = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        file_name      = traceback.extract_tb(error.__traceback__)[-1].filename
        line_number    = traceback.extract_tb(error.__traceback__)[-1].lineno

        # Текст кнопки для копирования ошибки:
        copy_button_text = "copy the error"

        # Основной текст:
        text = \
            f"Engine version: {get_version()}\n" \
            f"GDF version: {gdf.get_version()}\n" \
            f"Python version: {platform.python_version()}\n" \
            f"Class / Method: {source}\n" \
            f"Line number: {line_number}\n" \
            f"\nError message:\n{type(error).__name__}: {error}"

        # Текст, который будет скопирован:
        self.full_error = f"{text}\n\n{traceback_text}"

        # Заголовок ошибки:
        tk.Label(
            text=title_text,
            font=("Segoe UI", 12),
            fg=self.rgb_hex(255, 255, 255),
            bg=self.rgb_hex(20, 22, 28)
        ).pack(pady=3)

        # Фрейм основного текста:
        main_text_frame = tk.Frame(self.window, width=width, height=height//2.5)
        main_text_frame.pack()
        main_text_frame.pack_propagate(False)

        # Общая информация:
        self.text = tk.Text(
            main_text_frame,
            font=("Segoe UI", 10),
            fg=self.rgb_hex(255, 255, 255),
            bg=self.rgb_hex(20, 22, 28),
            wrap=tk.WORD, borderwidth=0,
            padx=3, pady=3)
        self.text.insert("end", text)
        self.text.configure(state=tk.DISABLED)
        self.text.pack(expand=True, fill=tk.X, anchor=tk.S)

        # Кнопка для копирования текста ошибки:
        tk.Button(
            text=copy_button_text, width=width, borderwidth=0,
            fg=self.rgb_hex(255, 255, 255),
            bg=self.rgb_hex(35, 37, 43),
            activeforeground=self.rgb_hex(255, 255, 255),
            activebackground=self.rgb_hex(50, 52, 58),
            command=self.copy_to_clipboard
        ).pack()

        # Текст ошибки:
        self.text = tk.Text(
            font=("Consolas", 8),
            fg=self.rgb_hex(255, 255, 255),
            bg=self.rgb_hex(4, 6, 10),
            wrap=tk.WORD, borderwidth=0,
            padx=5, pady=5)
        self.text.insert("end", traceback_text)
        self.text.configure(state=tk.DISABLED)
        self.text.pack(fill=tk.X, anchor=tk.S)

        # Запускаем окно:
        self.window.mainloop()

    # Переводим rgb в hex:
    @staticmethod
    def rgb_hex(red: int, green: int, blue: int) -> str:
        return f"#{int(red):02x}{int(green):02x}{int(blue):02x}"

    # Копирование текста в буфер обмена:
    def copy_to_clipboard(self) -> None:
        self.window.clipboard_clear()
        self.window.clipboard_append(self.full_error)
