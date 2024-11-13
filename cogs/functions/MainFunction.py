import discord
from discord.ext import commands
from discord import Interaction
from ..embeds.MainEmbed import Embed

class Func(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

# функция ошибки
    async def error(interaction: Interaction, message: str): 
        await interaction.response.send_message(
            embed=Embed.ошибка('Ошибка', message), 
            ephemeral=True, # невидимая
            delete_after=60 # удаляется чз 60 сек
        )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Embed(bot))