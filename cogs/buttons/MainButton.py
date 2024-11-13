# page_manager.py
import discord

class PageManager:
    def __init__(self, items: list[str]):
        self.items = items # содержимое страниц (текст списками). Каждый элемент списка - отдельная страница.
        self.total_pages = len(items) # всего страниц

    def get_embed(self, page: int) -> discord.Embed:
        embed = discord.Embed(description=f"{self.items[page]}\n\n{page + 1}/{self.total_pages}") # подписываем номера страниц: текущая / всего стр.
        return embed

class ListView(discord.ui.View):
    def __init__(self, manager: PageManager, page: int = 0):
        super().__init__()
        self.manager = manager
        self.page = page
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        # для каждой страницы отображает кнопки:
        if self.page > 0: # если не первая страница (0), то появляется кнопка - назад "<"
            self.add_item(PreviousButton(self.page, self.manager))
        if self.page < self.manager.total_pages - 1: # если не последняя страница (len), то появляется кнопка - далее ">"
            self.add_item(NextButton(self.page, self.manager))

class PreviousButton(discord.ui.Button): # кнопка - назад "<"
    def __init__(self, page: int, manager: PageManager):
        super().__init__(label="<", style=discord.ButtonStyle.primary)
        self.page = page
        self.manager = manager

    async def callback(self, interaction: discord.Interaction):
        new_page = self.page - 1
        view = ListView(self.manager, new_page)
        embed = self.manager.get_embed(new_page)
        await interaction.response.edit_message(embed=embed, view=view)

class NextButton(discord.ui.Button): # кнопка - далее ">"
    def __init__(self, page: int, manager: PageManager):
        super().__init__(label=">", style=discord.ButtonStyle.primary)
        self.page = page
        self.manager = manager

    async def callback(self, interaction: discord.Interaction):
        new_page = self.page + 1
        view = ListView(self.manager, new_page)
        embed = self.manager.get_embed(new_page)
        await interaction.response.edit_message(embed=embed, view=view)
