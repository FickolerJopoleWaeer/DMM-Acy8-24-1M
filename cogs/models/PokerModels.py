from ..DB import Data
from ..configs import MainConfig as MC
from discord.ext import commands
# from discord import Interaction

class Room(Data):
    def __init__(self, Название):
        self.row = Data.Room.find_one({"Название": Название})
        if not self.row:
            raise ValueError(f"Комната '{Название}' не найдена!")
        self.Название = self.row["Название"]
        self.Участники = self.row["Участники"]
        self.Порядок_ходов = self.row["Порядок_ходов"]
        self.Максимум_участников = self.row["Максимум_участников"]
        self.Пароль = self.row["Пароль"]
        self.Правила = self.row["Правила"]
        self.Создатель = self.row["Создатель"]
        self.Канал = self.row["Канал"]
        self.Роль = self.row["Роль"]
        self.ЧС = self.row["ЧС"]
        self.ID_Сервера = self.row["ID_Сервера"]
        self.Карты_стола = self.row["Карты_стола"]
        self.Мин_ставка = self.row["Мин_ставка"]
        self.Макс_ставка = self.row["Макс_ставка"]
        self.Тип_ставок = self.row["Тип_ставок"]
        self.Текущий_раунд = self.row["Текущий_раунд"]
        self.Текущий_ход = self.row["Текущий_ход"]
        self.Банк_общий = self.row["Банк_общий"]
        self.Банк_раунда = self.row["Банк_раунда"]
        self.Колода = self.row["Колода"]
        self.Время = self.row["Время"]



#                      ------  МОДЕРАЦИЯ КОМНАТЫ   ------

    # Добавление участника
    def add_member(self, member_id):
        if member_id in self.Участники:
            raise ValueError("Этот пользователь уже в комнате.")
        if len(self.Участники) >= self.Максимум_участников:
            raise ValueError("Комната заполнена.")
        Data.Room.update_one({"Название": self.Название}, {"$push": {"Участники": member_id}})
        return self.__init__(self.Название) # чтобы обновить атрибуты

    # Удаление участника
    def remove_member(self, member_id):
        Data.Room.update_one({"Название": self.Название}, {"$pull": {"Участники": member_id}})
        return self.__init__(self.Название)

    # Обновление атрибута комнаты
    def update_field(self, field: str, value):
        """
        print(f"Обновление поля: {field}, новое значение: {value}")  # Проверка значений +
        if isinstance(value, list):
            print("Переданное значение — это список")  # Подтверждение, что это список (если отправляем список, конечно) +
        """
        Data.Room.update_one({"Название": self.Название}, {"$set": {field: value}})
        # Перезагружаем объект комнаты для актуализации данных:
        return self.__init__(self.Название)

    # Удаление комнаты
    def delete_room(self):
        Data.Room.delete_one({"Название": self.Название})
        #return self.__init__(self.Название)

    # Добавление участника в ЧС
    def add_member_BL(self, member_id):
        if member_id in self.ЧС:
            raise ValueError("Этот пользователь уже в ЧС.")
        Data.Room.update_one({"Название": self.Название}, {"$push": {"ЧС": member_id}})
        return self.__init__(self.Название) # чтобы обновить атрибуты
    
    # Удаление участника в ЧС
    def remove_member_BL(self, member_id):
        if not (member_id in self.ЧС):
            raise ValueError("Этого пользователя уже нет в ЧС.")
        Data.Room.update_one({"Название": self.Название}, {"$pull": {"ЧС": member_id}})
        return self.__init__(self.Название) # чтобы обновить атрибуты
    
    # Форматирование списка комнат
    @staticmethod
    def format_room_list(rooms): # , interaction: Interaction
        formatted_rooms = []
        n: int = 0 # считаем кол-во комнат для формирования каждой страницы (до 10 шт. на стр.)
        room_info: str = '' # список комнат на каждую страницу
        for room in rooms:
            n += 1
            # print('room\n', room, n) # +
            password_icon = "🔐" if room["Пароль"] else "" # 🔐 🔒
            название = room['Название']
            room_info +=    f"> {n}. {название} {password_icon}\n" \
                            f"> ```{название}```" \
                            f"Количество человек: {len(room['Участники'])}/{room['Максимум_участников']}\n" \
                            f"> Создатель: <@{room['Создатель']}>\n" \
                            f"> Мин. ставка: {room['Мин_ставка']}\n" \
                            f"> Макс. ставка: {room['Макс_ставка']}"
            room_info += "\n\n"
            if n % 10 == 0: # каждые десять страниц добавляем на одну стр: (если нужно каждые 15, то if n % 15 == 0 и т.д.)
                formatted_rooms.append(room_info)
                room_info = '' # обнуляем список для следующей страницы
            else: pass
        formatted_rooms.append(room_info) # добавляем последние комнаты, которые вышли за пределы десяток
        # print('formatted_rooms\n', formatted_rooms) # +
        return formatted_rooms # Если захотим вернуть не список, а текстом все комнаты сразу, то можно использовать "\n\n".join(formatted_rooms)




#                      ------  РЕАЛИЗАЦИЯ ИГРЫ   ------

# метод обновления ходов (inc) - прибавить
    def след_ход(self):
        Data.Room.update_one({"Название": self.Название}, {"$inc": {'Текущий_ход': 1}}) # делает переход к следующему ходу (+1)
        return self.__init__(self.Название)

# метод обновления раундов (отпраавляем сюда название раунда)
    def след_раунд(self, раунд: str):
        Data.Room.update_one({"Название": self.Название}, {"$set": {'Текущий_раунд': раунд}}) # делает переход к следующему раунду
        return self.__init__(self.Название)
    
# добавление денег в банк

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Room(bot))