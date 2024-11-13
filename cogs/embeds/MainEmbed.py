import discord
from discord.ext import commands



class Embed(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.FM = EM(bot)

# создание обычного ебмеда:   
    def база(title: str, description: str = None) -> discord.Embed:
        clr = 0x2b2d31 # цвет фона дискорд тёмно-серый
        if description:
            embed = discord.Embed(title=title, description=description, color=clr)
        else:
            embed = discord.Embed(title=title, color=clr)
        return embed
    
# ебмед ошибки:
    def ошибка(title: str, description: str = None) -> discord.Embed:
        clr = discord.Color.red()
        if description:
            embed = discord.Embed(title=title, description=description, color=clr)
        else:
            embed = discord.Embed(title=title, color=clr)
        return embed

# ебмед создания и настроек комнаты для покера:
    def комната(title: str, description: str = None) -> discord.Embed:
        clr = discord.Color.green()
        if description:
            embed = discord.Embed(title=title, description=description, color=clr)
        else:
            embed = discord.Embed(title=title, color=clr)
        return embed

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Embed(bot))