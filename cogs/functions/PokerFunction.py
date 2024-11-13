import discord
from discord.ext import commands
from discord import Interaction
from ..embeds.MainEmbed import Embed
from .MainFunction import Func
from ..models.MainModels import User
from ..models.PokerModels import Room
from typing import Optional

class FuncP(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

# Функция для вывода текста (о макс-ой ставке) в зависимости от типа ставок
    def max_bet(type: str, bet: int = None) -> str: # так как нет обращения к API / БД, можно сделать ф-цию не асинхронной (синхронной), это сделает код лучше (быстрее)
        match type:
            case "Fixed-Limit":
                return f"Максимальная ставка фиксирована: {bet}" if bet else "Максимальная ставка фиксирована"
            case "Pot-Limit":
                return "Максимальная ставка равна размеру текущего банка" 
            case "No-Limit":
                return "Максимальная ставка отсутствует"
            case "Spread-Limit":
                return f"Максимальная ставка не больше {bet}" if bet else "Максимальная ставка варьируется"
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
    
    # Функция ошибок
    async def check_error(interaction: Interaction, user: User, room: Optional[Room], блайнд: int) -> bool:
        Комната = user.Комната
        if not Комната:
            await Func.error(interaction, 'Вы не находитесь ни в одной комнате.')
            return False
        Текущий_раунд = room.Текущий_раунд
        if Текущий_раунд != 'начало':
            await Func.error(interaction, f'Игра ещё не началась или уже идёт. Текущий раунд: "{Текущий_раунд}".')
            return False
        Текущий_ход = room.Текущий_ход
        ID_первого_игрока = room.Порядок_ходов[Текущий_ход-1]
        if interaction.user.id != ID_первого_игрока:
            await Func.error(interaction, f'Сейчас ход другого игрока: "<@{ID_первого_игрока}>".')
            return False
        Баланс = user.Баланс
        Мин_ставка = room.Мин_ставка//блайнд
        if Баланс < Мин_ставка:
            await Func.error(interaction, f'Недостаточно средств.\nУ вас: {Баланс}\nТребуется: {Мин_ставка}')
            return False
        return True

    # Функция ошибок ( ТЕСТОВАЯ ВЕРСИЯ, нигде не применяется ):
    """
    async def check_conditions(user, room=None, interaction=None, check_in_room=False, check_creator=False, check_round_not_started=False, member_id=None, check_blacklist=False):
        # Проверка на нахождение в комнате
        if check_in_room:
            if not user.Комната:
                await Func.error(interaction, 'Вы не находитесь ни в одной комнате.')
                return False
        # Проверка на создателя комнаты
        if check_creator:
            if not room or room.Создатель != interaction.user.id:
                await Func.error(interaction, f'Вы не являетесь создателем комнаты "{room.Название}".\nЕё создатель: <@{room.Создатель}>.')
                return False
            # Проверка на начало игры
        if check_round_not_started:
            if room.Текущий_раунд != 'не начата':
                await Func.error(interaction, f'Игра уже началась - текущий раунд: "{room.Текущий_раунд}".\nДождитесь окончания игры.')
                return False
        # Если все проверки прошли успешно
        return True
        """

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Embed(bot))