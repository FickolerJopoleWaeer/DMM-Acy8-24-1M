from discord.ext import commands
from discord.utils import get # для поиска объектов, таких как серверы, каналы или пользователи, по атрибутам
from pymongo import MongoClient # БД
from .configs import MainConfig as MC # файл с ID сервера
import threading

class Data(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        #print(self.bot.guilds)
        print("Хранилища поплняются данными")

    cluster = MongoClient('mongodb://127.0.0.1:27089/') # подключаем БД
    PlayerDB = cluster.shp.PlayerDB # Подключаем коллекции внутри базы данных shp

    def data_base(self, ID, Name):
        Player = {
"id": ID, # member.id,
"Имя": Name, # member.name,

        }
        return Player

    def check_users(self):
        # for guild in bot.guilds: - для перебора серверов не в коге.
        # https://www.youtube.com/watch?v=-hPVfjyDREA
        # Добавляем людей в БД:
        for member in self.guild.members: # для перебора всех людей (или только на сервере?)
            # print(f'self: {self} \nself.guild: {self.guild}\nmember: {member}')
            if Data.users.count_documents({"id": member.id}) == 0: 
            # проверяет, есть ли в базе данных записи о текущем пользователе,
            # если нет, то:
                post = self.data_base(member.id, member.name) # Создается словарь с информацией о пользователе с помощью функции data_base
                Data.users.insert_one(post) # Вставляет созданный объект post в коллекцию Data.users базы данных
        
        # Добавляем поля людям:
        for member in self.guild.members: # для каждого участника на сервере
            post = self.data_base(member.id, member.name) # Создает словарь с данными о пользователе
            Словарь_Игрока = Data.users.find_one({"id": member.id}) # Ищет в базе данных запись о игроке по id. Возвращает все поля в БД о игроке.
            # Удаляем существующую запись о пользователе из базы данных: (Чтобы позже добавить обновленные данные)
            Data.users.delete_one({"id": member.id})
            # Добавляем новую запись о пользователе с недостающими полями:
            new_data = {
                field: Словарь_Игрока[field] if field in Словарь_Игрока else default_value 
                # Проверяет: есть ли поле field в существующей записи об игроке? 
                # ДА: сохраняем. 
                # Нет: берём значение по умолчанию из post.
                for field, default_value in post.items() # Проходит по каждому полю и значению из словаря post
            }
            Data.users.insert_one(new_data) # Добавляет новую, обновленную запись о пользователе в БД.

# Добавляет всех отсутствующих людей в БД при запуске
    @commands.Cog.listener()
    async def on_ready(self): # когда бот подключается к серверу
        self.guild = self.bot.get_guild(MC.SERVER_GUILD) # Получает сервер по его ID
        t1 = threading.Thread(target=self.check_users) # Создается новый поток 
        # с целью запустить функцию check_users. Потоки позволяют выполнять несколько задач 
        # одновременно, не блокируя основной поток программы. 
        t1.start() # Запускает созданный поток

# Добавляет в БД при вступлении на сервер
    @commands.Cog.listener()
    async def on_member_join(self, member): # когда чел заходит на серв
        if Data.users.count_documents({"id": member.id}) == 0: # Если его нет в БД, то:
            post = self.data_base(member.id, member.name) # Значения по умолчанию
            Data.users.insert_one(post) # Добавляет

async def setup(bot):
    await bot.add_cog(Data(bot))