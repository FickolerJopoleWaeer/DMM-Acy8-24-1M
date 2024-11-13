from discord.ext import commands
from discord.utils import get # для поиска объектов, таких как серверы, каналы или пользователи, по атрибутам
from .configs import MainConfig as MC # файл с ID сервера
import threading

# Для определения типов:
from discord import Member, Guild
from pymongo import MongoClient, database, collection # БД
from typing import List, Optional

class Data(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild: Guild | None = None

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        #print(self.bot.guilds)
        print("Хранилища поплняются данными")

# Подключаем базу данных Poker и коллекции в ней:
    cluster: MongoClient = MongoClient('mongodb://127.0.0.1:27089/')
    poker_db: database.Database = cluster["Poker"]
    Player: collection.Collection = poker_db["Player"]
    Room: collection.Collection = poker_db["Room"]


# Проверка и создание индексов (1 вариант):
    '''
    def create_indexes(self):
        existing_indexes = Data.Player.index_information()
        if "Баланс" not in existing_indexes: 
            Data.Player.create_index("Баланс") 
        ...
        if "Комбо" not in existing_indexes:
            Data.Player.create_index("Комбо")
    '''
# наверное через цикл сделать лучше, НАПРИМЕР (2 вариант):
    '''
    def create_indexes(self):
        # Список полей для индексации:
        fields_to_index = ["Баланс", "Общая_ставка", ... , "Кол-во_побед", "Комбо"] # ТОЛЬКО ИЗ СПИСКА ИНДЕКСОВ НИЖЕ
        # Получаем существующие индексы:
        existing_indexes = Data.Player.index_information()
        # Проходим по полям и создаем индексы при необходимости:
        for field in fields_to_index:
            if field not in existing_indexes:
                Data.Player.create_index(field)
    '''
    # Данная версия хороша при выводе бота в массы. 
    # Для стадии теста и разработки сойдёт вариант ниже:

# Создаем индексы для игроков (3 вариант)
    def create_indexes(self) -> None:
        Data.Player.create_index("Баланс")           # Индекс по балансу
        Data.Player.create_index("Общая_ставка")     # Индекс по ставкам
        Data.Player.create_index("Общий_выигрыш")    # Индекс по выигрышам
        Data.Player.create_index("Кол-во_игр")       # Индекс по играм
        Data.Player.create_index("Кол-во_побед")     # Индекс по победам
        Data.Player.create_index("Комбо")            # Индекс по комбинациям

# Создаем индексы для комнат (3 вариант)
        Data.Room.create_index("Название", unique=True)  # Уникальное имя комнаты
        Data.Room.create_index("ID_Сервера") # ID_Сервера может повторяться для разных комнат

# метод, чтобы извлекать комнаты с определённым ID_Сервера (использует индексы выше)
    @staticmethod
    def get_rooms_by_server(server_id):
        #print('Data:')
        #print(list(Data.Room.find({"ID_Сервера": server_id}))) # +
        return list(Data.Room.find({"ID_Сервера": server_id})) # Когда выполняется метод find с фильтром по ID_Сервера, MongoDB использует индекс, чтобы найти подходящие записи быстрее.

# Функция для создания комнаты (заполняем значениями по умолчанию)
    def create_room_db(self, 
                       name: str,           # название комнаты
                       creator_id: int,     # ID создателя
                       server_id: int,      # ID сервера
                       role_id: int,        # ID роли
                       channel_id: int,     # ID канала
                       rules: str = "Техасский холдем",     # Правила игры
                       creator_BL: list = [],       # ЧС создателя
                       max_players: int = 10,       # Максимальное число игроков
                       password: Optional[str] = None,        # Пароль
                       ) -> dict:
        return {
"Название": name,
"Участники": [creator_id],  # Список участников, изначально в нём ID создателя
"Порядок_ходов": [],  # Порядок ходов
"Максимум_участников": max_players,
"Пароль": password,
"Правила": rules,
"Создатель": creator_id,
"Канал": channel_id,  # ID канала 
"Роль": role_id,  # Роль для канала
"ЧС": creator_BL,  # (BL - black list) включает создателя
"ID_Сервера": server_id,
"Карты_стола": [],
"Мин_ставка": 10,
"Макс_ставка": 100,
"Тип_ставок": "Spread-Limit", # Fixed-Limit / Pot-Limit / No-Limit / Spread-Limit 
"Текущий_раунд": "не начата", # не начата, начало, пре-флоп, флоп, тёрн, ривер
"Текущий_ход": 0,
"Банк_общий": 0,
"Банк_раунда": 0,
"Колода": [],  # Нерозданные карты (будет заполнен)
"Время": None, # Время последнего хода
        }
    
# Значения полей по умолчанию
    def create_player_db(self, ID: int, Name: str) -> dict:
        return {
"id": ID,       # member.id,
"Имя": Name,    # member.name,
"Баланс": 1000,     # Баланс
"Комната": None,    # В какой комнате состоишь
"Карты": None,      # Карты на руках
"Всего_поставил": 0,    # Всего поставлено в этой игре
"Сейчас_поставил": 0,   # На текущий момент (раунд) поставлено в игре
"Общая_ставка": 0,      # Сколько всего денег поставил в покере
"Общий_выигрыш": 0,     # Сколько всего денег выиграл в покере
"Кол-во_игр": 0,    # Сколько игр всего сыграно
"Кол-во_побед": 0,  # Сколько раз победил
"Комбо": {},    # Наилучшие комбинации и сколько раз выпадали
"ЧС": [],       # Чёрный список
        }

    def check_users(self) -> None:
        # for guild in bot.guilds: - для перебора серверов не в коге.
        # https://www.youtube.com/watch?v=-hPVfjyDREA
        members: List[Member] = self.guild.members  # Указываем тип как список участников
    # Добавляем людей в БД:
        for member in members: # для перебора всех людей (или только на сервере?)
            # print(f'self: {self} \nself.guild: {self.guild}\nmember: {member}')
            if Data.Player.count_documents({"id": member.id}) == 0: 
            # проверяет, есть ли в базе данных записи о текущем пользователе,
            # если нет, то:
                post = self.create_player_db(member.id, member.name) # Создается словарь с информацией о пользователе с помощью функции data_base
                Data.Player.insert_one(post) # Вставляет созданный объект post в коллекцию Data.Player базы данных
    # Добавляем поля людям:
        for member in self.guild.members: # для каждого участника на сервере
            post = self.create_player_db(member.id, member.name) # Создает словарь с данными о пользователе
            Словарь_Игрока = Data.Player.find_one({"id": member.id}) # Ищет в базе данных запись о игроке по id. Возвращает все поля в БД о игроке.
            # Удаляем существующую запись о пользователе из базы данных: (Чтобы позже добавить обновленные данные)
            Data.Player.delete_one({"id": member.id})
            # Добавляем новую запись о пользователе с недостающими полями:
            new_data = {
                field: Словарь_Игрока[field] if field in Словарь_Игрока else default_value 
                # Проверяет: есть ли поле field в существующей записи об игроке? 
                # ДА: сохраняем. 
                # Нет: берём значение по умолчанию из post.
                for field, default_value in post.items() # Проходит по каждому полю и значению из словаря post
            }
            Data.Player.insert_one(new_data) # Добавляет новую, обновленную запись о пользователе в БД.

# Добавляет всех отсутствующих людей в БД при запуске
    @commands.Cog.listener()
    async def on_ready(self) -> None: # когда бот подключается к серверу
        self.guild = self.bot.get_guild(MC.SERVER_GUILD) # Получает сервер по его ID
        self.create_indexes()  # Создаем индексы при запуске бота
        t1 = threading.Thread(target=self.check_users) # Создается новый поток 
        # с целью запустить функцию check_users. Потоки позволяют выполнять несколько задач 
        # одновременно, не блокируя основной поток программы. 
        t1.start() # Запускает созданный поток

# Добавляет в БД при вступлении на сервер
    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None: # когда игрок заходит на сервер
        if Data.Player.count_documents({"id": member.id}) == 0: # Если его нет в БД, то:
            post = self.create_player_db(member.id, member.name) # Значения по умолчанию
            Data.Player.insert_one(post) # Добавляет

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Data(bot))