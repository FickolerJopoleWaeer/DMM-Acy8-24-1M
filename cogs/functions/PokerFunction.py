# PokerFunction.py

# import discord
from discord.ext import commands
from discord import Interaction
from ..embeds.MainEmbed import Embed
from .MainFunction import Func
from ..models.MainModels import User
from ..models.PokerModels import Room
from ..configs import PokerConfig as PC
from typing import Optional
import random

class FuncP(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

# Функция для вывода текста (о макс-ой ставке) в зависимости от типа ставок
    def max_bet(type: str, bet: int = None) -> str: # так как нет обращения к API / БД, можно сделать ф-цию не асинхронной (синхронной), это сделает код лучше (быстрее)
        match type: # Вывод будет в виде: 'Максимальная ставка: {return}'
            case "Fixed-Limit":
                return f"фиксирована: {bet}" if bet else "фиксирована"
            case "Pot-Limit":
                return "равна размеру текущего банка" 
            case "No-Limit":
                return "отсутствует"
            case "Spread-Limit":
                return f"до {bet}" if bet else "варьируется"
            case _:
                return "Неверный тип ставки"

# Выводит текст о порядке ходов, подчёркивая того, кто должен ходить далее
    async def move_order(interaction: Interaction, Участники: list) -> str:
        guild = interaction.guild
        ход_участников: list = []
        star: str = ''
        for index, user_id in enumerate(Участники, start=1):
            member = await guild.fetch_member(user_id)
            nickname = member.nick if member.nick else member.name # Получаем никнеймы участников
            if index == 1:
                star = '__'
            ход_участников.append(f"{star}{index}. {nickname}{star}")
            star: str = ''
        порядок_ходов = "\n".join(ход_участников) # Формируем итоговый текст о порядке ходов
        return порядок_ходов
    
# Функция ошибок для малого и большого блайндов
    async def check_error_blind(interaction: Interaction, room: Optional[Room], Ставка: int) -> bool:
        user = User(interaction.user.id)
        Текущий_раунд = room.Текущий_раунд
        if Текущий_раунд == 'не начата':
            await Func.error(interaction, f'Игра ещё не началась.')
            return False
        if Текущий_раунд != 'начало':
            await Func.error(interaction, f'Большой и малый блайнды уже поставлены. Текущий раунд: "{Текущий_раунд}".')
            return False
        Текущий_ход = room.Текущий_ход
        ID_первого_игрока = room.Порядок_ходов[Текущий_ход]
        if interaction.user.id != ID_первого_игрока:
            await Func.error(interaction, f'Сейчас ход другого игрока: "<@{ID_первого_игрока}>".')
            return False
        Баланс = user.Баланс
        if Баланс < Ставка: # Не хватает фишек
            await Func.error(interaction, f'Недостаточно средств.\nУ вас: {Баланс}\nТребуется: {Ставка}')
            return False
        return True
    
# Функция ошибок для Бет и Рейз
    async def check_error_bet(interaction, Новая_ставка: int, Мин_ставка: int, Макс_ставка: int, Баланс: int, Ставка: int) -> bool:
        """
        Проверяет корректность новой ставки и отправляет сообщение об ошибке, если проверка не пройдена.
        interaction: объект взаимодействия Discord.
        Новая_ставка: новая ставка игрока.
        Мин_ставка: минимальная допустимая ставка.
        Макс_ставка: максимальная допустимая ставка.
        Баланс: текущий баланс игрока.
        Ставка: разница между новой ставкой и уже сделанной ставкой.
        :return: True, если проверка успешна, иначе False.
        """
        if Новая_ставка < Мин_ставка: # Указанная ставка меньше большого блайнда (бет) / меньше текущей, умноженной на 2 (рейз)
            await Func.error(interaction, f'Указанная ставка меньше минимальной.\nНужно поставить {Мин_ставка} или больше.')
            return False
        if Новая_ставка > Макс_ставка: # Указанная ставка больше максимальной
            await Func.error(interaction, f'Указанная ставка больше максимальной.\nНужно поставить {Макс_ставка} или меньше.')
            return False
        if Баланс < Ставка: # Не хватает фишек
            await Func.error(interaction, f'Недостаточно средств.\nУ вас: {Баланс}\nТребуется: {Ставка}')
            return False
        return True

# Функция ошибок для ставок
    async def check_error(interaction: Interaction, room: Optional[Room], Раунд: list) -> bool:
        """
        Проверяет основные ошибки.
        interaction: объект взаимодействия Discord.
        room:
        Раунд: Список раундов. Все раунды: ['не начата', 'начало', 'пре-флоп', 'флоп', 'тёрн', 'ривер']
        :return: True, если проверка успешна, иначе False.
        """
        Текущий_раунд = room.Текущий_раунд
        if Текущий_раунд == 'не начата':
            await Func.error(interaction, f'Игра ещё не началась.')
            return False
        if not (Текущий_раунд in Раунд):
            await Func.error(interaction, f'В этом раунде нельзя использовать эту команду. Текущий раунд: "{Текущий_раунд}".')
            return False
        Текущий_ход = room.Текущий_ход
        ID_первого_игрока = room.Порядок_ходов[Текущий_ход]
        if interaction.user.id != ID_первого_игрока:
            await Func.error(interaction, f'Сейчас ход другого игрока: "<@{ID_первого_игрока}>".')
            return False
        return True

# Функция обновления раунда 
    async def обновить_раунд(interaction: Interaction, room: Optional[Room]):
        Раунды: list[str] = PC.Раунды
        Текущий_раунд = room.Текущий_раунд
        if Текущий_раунд in Раунды:  # проверяем, есть ли название текущего раунда в списке 'Раунды' = ['не начата',..,'ривер']
            индекс = Раунды.index(Текущий_раунд) # индекс = номеру текущего раунда в списке 'Раунды' = ['не начата',..,'ривер']
            if индекс < len(Раунды) - 1: # Проверяем, есть ли следующий раунд или уже конец игры
                Следующий_раунд: str = Раунды[индекс + 1]
                room.след_раунд(Следующий_раунд)    # меняем название раунда на слеующее
                room.обнуляем_банк()                # 'Банк_раунда' = 0
                room.сбросить_ставки()              # для каждого игрока обнуляем поле 'Сейчас_поставил' (в этом раунде)
                room.новая_ставка(0)                # сбрасываем 'Текущая_ставка' для следующего раунда
                print('обновление_раунда:', f'{Текущий_раунд} -> {Следующий_раунд}')
            # Выдаём карту на стол
                print('Следующий_раунд: ', Следующий_раунд)
                if Следующий_раунд == 'флоп': # если переходим на раунд флоп, то раздём 3 карты
                    Колода: list[list] = PC.Колода
                    random.shuffle(Колода) # Перемешиваем колоду если берём из PC.Колода
                    Карты = [Колода.pop(), Колода.pop(), Колода.pop()]
                    room.стол_раздать(Карты)    # устанавливаем три карты для стола ("Карты_стола")
                    print('Карты 1: ', Карты)
                    room.обновляем_колоду(Колода)   # уменьшаем колоду на 3 карты
                elif Следующий_раунд in ['тёрн', 'ривер']: # при переходе к этим раундам выдаёт 1 карту.
                    Колода: list[list] = room.Колода    # тут колода уже перемешенная
                    Карты = [Колода.pop()]      # сохраняет в 'Карты' последний элемент (карту) из 'Колода', и одновременно убирает его из списка колоды
                    room.стол_добавить(Карты)   # добавляем 1 карту к картам стола ("Карты_стола")
                    print('Карты 2: ', Карты)
                    room.обновляем_колоду(Колода)   # уменьшаем колоду на 1 карту
                else: pass
                print('обновляем_колоду: ', Колода)
                return f'Раунд обновлён: {Текущий_раунд} -> {Следующий_раунд}\n'
            else:   # Если это последний раунд
                # Конец игры
                # ВЫЗОВ ФУНКЦИИ ПОДСЧЁТА ПОБЕДИТЕЛЕЙ и НАГРАД
                '''
                тут await и наверное return или иная остановка кода дальнейшего
                '''
                await interaction.response.send_message(
                    embed=Embed.комната('Игра окончена!', f'Подсчёт победителей в процессе...')
                )
                return None  # Завершение функции
        else:   # Если текущего раунда нет в списке
            return f'Ошибка: Текущий раунд "{Текущий_раунд}" не найден в списке!'


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Embed(bot))