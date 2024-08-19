#
# discord.py - Создаёт класс для показа активности в движке у вас в профиле дискорда.
#


# Импортируем:
import time
from .gdf.utils import DiscordRPC


# Класс дискорд rpc для движка:
class DiscordRPCEngine:
    def __init__(self, settings: dict) -> None:
        self.app_id = 1271088311238266880
        self.settings = settings

        if self.settings["discord-rpc"]:
            self.rpc = DiscordRPC(self.app_id)

    # Обновить статус:
    def update(self, state: str, details: str) -> None:
        if not self.settings["discord-rpc"] or self.rpc is None: return
        self.rpc.update(
            state=state,
            details=details,
            start_time=int(time.time())
        )
