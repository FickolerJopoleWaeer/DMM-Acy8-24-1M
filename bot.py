# bot.py

import discord
from discord.ext import commands
import os
import asyncio
import logging  # Модуль logging позволяет выводить сообщения о различных событиях и ошибках в процессе выполнения программы.
from dotenv import load_dotenv


load_dotenv()  # Загружает переменные из .env файла в окружение
token = os.getenv('DISCORD_TOKEN')  # Получает значение токена
if token is None:
    raise ValueError("Токен не найден. Проверьте файл .env.")

discord.utils.setup_logging(level = logging.INFO, root = True)  # логирование для библиотеки discord.py
# Уровень INFO обычно используется для записи общей информации о работе программы, а также выводит WARNING, ERROR, и CRITICAL.
# root=True: Указывает, что нужно настраивать логирование для корневого логгера (основного, т.е. всеё программы)ы.

intents = discord.Intents.default()  # Разрешения бота по умолчанию. discord.Intents.all() - все
intents.message_content = True  # Разрешено читать сообщения
intents.members = True  # Разрешено опредялть вход и выход участников на сервере
bot = commands.Bot(command_prefix='.', intents=intents, sync_commands_debug=True)  # Префикс к боту, разрешения, включение режима отладки синхронизации команд

@bot.event
async def on_ready():  # бот запущен и подключился к серверу Discord:
    await bot.tree.sync()  # Синхронихация слеш команд с сервером
    текст = 'Бот готов к работе!'
    print(текст)
    # await bot.change_presence(status=discord.Status.online, activity = discord.Activity(type=discord.ActivityType.watching, name="за тобой")) # статус бота.
    await bot.get_channel(1285114616560488530).send(текст)  # ID канала для отправки статуса бота

# подключаем все коги  # есть также код, позволяющий сделать обновление когов через команды
async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            if filename != "__init__.py":
                await bot.load_extension(f"cogs.{ filename[:-3]}")

async def main():
    await load()
    await bot.start(token)

asyncio.run(main())