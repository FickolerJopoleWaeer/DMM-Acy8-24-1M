# MainModels.py

from ..DB import Data
from ..configs import MainConfig as MC
from discord.ext import commands

class User(Data):
    def __init__(self, id): # считываем поля игрока по ID
        self.row = Data.Player.find_one({"id": id}) 
        self.id = self.row["id"] 
        self.Имя = self.row["Имя"]
        self.Баланс = self.row["Баланс"]
        self.Комната = self.row["Комната"]
        self.Карты = self.row["Карты"]
        self.Всего_поставил = self.row["Всего_поставил"]
        self.Сейчас_поставил = self.row["Сейчас_поставил"]
        self.Общая_ставка = self.row["Общая_ставка"]
        self.Общий_выигрыш = self.row["Общий_выигрыш"]
        self.Колво_игр = self.row["Кол-во_игр"]
        self.Колво_побед = self.row["Кол-во_побед"]
        self.Комбо = self.row["Комбо"]
        self.ЧС = self.row["ЧС"]

# метод обновления (set) - установить
    def установить(self, имя: str, значение):
        Data.Player.update_one({"id": self.id}, {"$set": {имя: значение}})
        return self.__init__(self.id) # чтобы обновить атрибуты

# метод обновления (inc) - прибавить
    def добавить(self, имя: str, значение):
        Data.Player.update_one({"id": self.id}, {"$inc": {имя: значение}}) # можно добавить upsert=True - тогда если строки нет такой в бд, она её создаст
        return self.__init__(self.id)

# игрок делает ставку
    def ставка(self, сумма: int):
        Data.Player.update_one({"id": self.id}, {"$inc": {'Баланс': -сумма, 'Сейчас_поставил': сумма, 'Всего_поставил': сумма, 'Общая_ставка': сумма}})
        return self.__init__(self.id)

# игрок использует /покер фолд (выходит из игры) или КОНЕЦ ИГРЫ, сбрасываем поставленные деньги, карты, увеличиваем кол-во сыгранных игр на 1
    def сброс_ставки(self):
        Data.Player.update_one({"id": self.id}, {"$set": {'Сейчас_поставил': 0, 'Всего_поставил': 0, 'Карты': None}})
        Data.Player.update_one({"id": self.id}, {"$inc": {'Кол-во_игр': 1}})
        return self.__init__(self.id)
    
# Заносим выигрыш игроку в БД
    def наградить(self, сумма: int):
        Data.Player.update_one({"id": self.id}, {"$inc": {'Баланс': сумма, 'Общий_выигрыш': сумма, 'Кол-во_побед': 1}}) 
        return self.__init__(self.id)
    
# метод обновления комбинации (при ЗАВЕРШЕНИИ ИГРЫ, не учитывается во время выхода из игры чз /покер фолд)
    def обновить_комбо(self, комбинация: str):
        # Проверяем, есть ли поле "Комбо" и инициализируем его, если пустое
        if not isinstance(self.Комбо, dict):  # На случай, если поле отсутствует или не словарь
            self.Комбо = {}
        self.Комбо[комбинация] = self.Комбо.get(комбинация, 0) + 1  # Увеличиваем значение для указанной комбинации или создаём с 1, если её нет
        Data.Player.update_one({"id": self.id}, {"$set": {"Комбо": self.Комбо}})    # Обновляем данные в базе
        return self.__init__(self.id)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(User(bot))