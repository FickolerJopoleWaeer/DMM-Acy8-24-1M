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
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(User(bot))