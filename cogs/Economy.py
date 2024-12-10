# Economy.py

import random
import time
#import datetime
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional # используется в самом начале команд, на случай отсутствия ввода значений, например:
# def _buy666(self, count: Optional[int] = None): # в этом случае мы показываем, что аргумент могут не ввести, но если введут, он должен быть целым числом.
# from typing import Union # для того чтоб вводить аргумент либо число, либо строку all - т.е. всё сумму.
from discord.app_commands import Choice
import discord
from discord.ext import commands, tasks
from discord import Interaction
from .configs import MainConfig as MC


from .models.MainModels import User
from .embeds.MainEmbed import Embed
"""
from .models.models2 import Sila
from .models.models3 import Hikki
from .Emoji import Emoji as EM
"""
from discord import app_commands
from discord.ui import Button, View


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.FM = EM(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Экономика процветает!")

    '''
Баланс (Balance | Bal | Money): 
Посмотреть, сколько у тебя (или другого пользователя) сейчас фишек / монет. 
Пример: /баланс @джони
@джони – имя пользователя. Для просмотра своего баланса можно оставить пустым. Если указать себя – не будет считаться ошибкой.
    '''
    @app_commands.command(name = "баланс", description="посмотреть баланс") # balance
    @app_commands.rename(member='игрока')
    async def _balance(self, interaction: Interaction, member: discord.Member = None):
        if member:
            interaction.user = member
        user = User(interaction.user.id)
        # emoji = self.FM.e_FM()
        await interaction.response.send_message(embed = Embed.база(f"Профиль {interaction.user.display_name}", 
            f"Баланс: {"{:,.0f}".format(user.Баланс).replace(",", ".")}"), ephemeral=True, delete_after = 90)

    '''
Передать:
Передача фишек/монет другому игроку.
Пример: /передать @джони
@джони – имя пользователя. Можно указать ID, чтобы не пришёл пинг.
Возвращает ошибку, если:
•	Не ввёл имя/ID игрока;
•	Передаёшь больше, чем у тебя есть;
•	Передаёшь не целое и не положительное число;
•	Передаёшь себе;
    '''

    
    '''
Работа (Work): 
Получить ежедневную сумму (одинакова для всех). Может лучше сделать так, чтоб каждую игру могли получать деньги? Какой-то минимальный кэш-бек. Считает сколько игр сыграно с последнего ввода команды – и умножает на сумму. Или это как коэффициент будет, типо: 300 + 50*(кол-во игр в покер) + 10*(кол-во игр в другую игру) + … Коэффициенты исходя из средней величины ставок.
    '''







async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Economy(bot))