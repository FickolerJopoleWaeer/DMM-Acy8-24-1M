# Poker_Room.py

import discord
from discord.ext import commands
from discord import app_commands, Interaction, Member
from .models.MainModels import User
from .models.PokerModels import Room
from .DB import Data
from .configs import MainConfig as MC
from .embeds.MainEmbed import Embed
from .functions.MainFunction import Func
from typing import Optional # для типов данных: Optional[str] - специальный тип данных, который указывает, что переменная может быть либо строкой, либо None.
from .buttons.MainButton import PageManager, ListView # чтобы листать список комнат

class Poker_Room(commands.GroupCog, name="комната"): # создаёт класс команд
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

#                      ------  МОДЕРАЦИЯ КОМНАТЫ   ------

# 1 - создать
    '''
Комната создать: 
Возможность создания новой игровой сессии. 
•	Создаёт канал, чтобы никто не мешал, 
•	Создаёт роль, которая даёт доступ к каналу, 
•	Даёт роль создателю комнаты,
•	Отправляет сообщение с ID канала комнаты в чате, где была написана команда,
•	Отправляет сообщение с пингом в канал комнаты (пишет инфу кто создатель), в котором перечисляет все команды для настройки комнаты,
При создании комнаты можно: 
•	Указать название (обязательно),
•	Выбрать максимальное количество человек (по умолчанию = максимально возможному = 10), 
•	Минимальную ставку (большой блайнд), (обязательно),
•	Настраивать пароль (по умолчанию отсутствует, не обязательно), 
•	после первой партии (по умолчанию: нет, она будет оставаться открытой),
•	Выбрать правила игры: техасский холдем по умолчанию, …
•	Добавляет к ЧС комнаты чёрный список создателя,
•	
Пример: /комната создать Техасский_холдем Техас44 4 Uieo 
Где: Комната – класс команд, Техас44 – название комнаты, 4 – максимально кол-во человек, Uieo – пароль, Техасский_холдем – правила игры, выбираются из списка (если можно такой сделать)
Возвращает ошибку, если:
•	Комната с таким названием уже существует (именно на этом сервере); +
•	Ты уже находишься в комнате (выдаёт предупреждение об этом с названием комнаты); +
•	Максимальное кол-во человек не является целым числом ИЛИ: + 
•	Числом вообще, ИЛИ: +
•	Превышает лимит (больше чем 10), обычно играют максимум по 6, 8, 10, ИЛИ: +
•	Меньше минимального (меньше чем 2); +
•	Название не введено; +
    '''
    @app_commands.command(name="создать", description="Создать новую комнату")
    @app_commands.describe(правила="Выберите правила игры")
    @app_commands.choices(правила=[
        discord.app_commands.Choice(name="Техасский холдем", value="Техасский холдем"),
        discord.app_commands.Choice(name="Омаха", value="Омаха")
    ])
    @app_commands.rename(max_players='максимум_игроков') # переименовывает атрибут в интерфейсе дискорда для пользователей
    async def _создание_комнаты(self, interaction: Interaction,
                                  правила: discord.app_commands.Choice[str], 
                                  название: str, 
                                  max_players: int = 10, 
                                  пароль: Optional[str] = None):
        user = User(interaction.user.id)
        Комната = user.Комната
    # Проверяем ошибки
        if Комната:
            await Func.error(interaction, f'Вы уже находитесь в комнате "{Комната}".\nДля выхода используйте: "/комната выход"')
            return
        if max_players < 2 or max_players > 10:
            await Func.error(interaction, f"Максимальное количество игроков должно быть от 2 до 10.\nВы указали: {max_players}")
            return
        if Data.Room.find_one({"Название": название}): # Проверяем, существует ли уже комната с таким именем +
            await Func.error(interaction, f"Комната с названием '{название}' уже существует.")
            return
    # Создаем комнату
        guild = interaction.guild
        роль = await guild.create_role(name=название) # Создание роли
        канал = await guild.create_text_channel(название) # Создание канала
        # Установка прав на доступ к каналу:
        await канал.set_permissions(роль, read_messages=True, send_messages=True)
        await канал.set_permissions(guild.default_role, read_messages=False)  # Запрет доступа для остальных
        # Выдача роли пользователю, который ввел команду:
        await interaction.user.add_roles(роль)
    # Заполняем БД
        # добавляем в базу данных комнат:
        # print('название: ',название, '\nid создателя: ', interaction.user.id, '\nguild: ', guild.id, '\nроль: ', роль.id, '\nканал: ', канал.id, '\nправила: ', правила.value, '\nЧС: ', user.ЧС, '\nmax_players: ', max_players, '\nпароль: ', password)
        room_data = Data.create_room_db(self, название, interaction.user.id, guild.id, роль.id, канал.id, правила.value, user.ЧС, max_players, пароль)        
        Data.Room.insert_one(room_data)
        # добавляем базу данных игрока: 
        user.установить('Комната', название)
    # Отправляем сообщени об успехе
        if пароль:  # Проверяем, был ли введён пароль
            await interaction.user.send(f'Пароль для комнаты "{название}": `{пароль}`')  # Обрамляем пароль в `` для удобства копирования
        await interaction.response.send_message(embed = Embed.комната(
"Комната успешно создана!", 
f'Название: {название}\n\
Правила: {правила.value}\n\
Канал: <#{канал.id}>\n\
Состав: <@{user.id}> (Создатель)\n\
Максимальное количество человек: {max_players}\n\n\
\n\
'))


# 2 - удалить
    '''
Комната удалить:
Доступна только для создателя комнаты. Удаляет комнату в БД каждого участника, а затем и у бота. Аналогично удаляет роли, а затем канал
Пример: /комната удалить
Возвращает ошибку, если:
•	Если ты не состоишь ни в одной комнате, +
•	Команду использует не создатель комнаты, +
•	Идёт игра +
    '''
    @app_commands.command(name = "удалить", description="Удалить созданную комнату") # balance
    async def _удаление_комнаты(self, interaction: Interaction):
        user = User(interaction.user.id)
    # Проверяем ошибки
        Комната = user.Комната
        if not Комната:
            await Func.error(interaction, f'Вы не находитесь ни в одной комнате.')
            return
        room = Room(Комната)
        Создатель = room.Создатель
        if Создатель != interaction.user.id:
            await Func.error(interaction, f'Вы не являетесь создателем комнаты "{Комната}".\nЕё создатель: <@{Создатель}>.\nДля выхода используйте: "/комната выход"')
            return
        Текущий_раунд = room.Текущий_раунд
        '''if Текущий_раунд != 'не начата':
            await Func.error(interaction, f'Игра уже началась - текущий раунд: "{Текущий_раунд}".\nДождитесь окончания игры.')
            return''' # ВРЕМЕННО ЗАКОММЕНТИРОВАЛ ДЛЯ ТЕСТОВ
        Участники = room.Участники # список с ID участников
    # Удаляем у каждого участника комнату в БД
        for Участник in Участники:
            Участник = User(Участник)
            Участник.установить('Комната', None)
    # Удаляем канал        
        guild = interaction.guild
        роль = guild.get_role(room.Роль)  # Получаем роль по её ID, сохраненному ранее. Если роли нет, вернёт None
        канал = guild.get_channel(room.Канал)  # Получаем канал по ID
        if канал:  # Проверяем, что канал существует
            await канал.delete() # Удаление канала
        if роль:  # Проверяем, что роль существует
            await роль.delete() # Удаление роли
        room.delete_room() # Удаляем комнату из БД
    # Отправляем сообщени об успехе
        await interaction.user.send(f'Комната "{Комната}" успешно удалена') # отправляем в ЛС
        await interaction.response.send_message(embed = Embed.комната(f'Комната "{Комната}" успешно удалена'))
        

# 3 - пароль
    '''
Комната пароль: 
Меняет /устанавливает пароль комнаты. 
Прозрачная, по возможности даёт легко скопировать пароль.
Доступна только для создателя комнаты.
Если пароль не введён – сбрасывает (удаляет) пароль для комнаты.
Пример: /комната Uieo
Возвращает ошибку, если:
•	Если ты не состоишь ни в одной комнате, +
•	Команду использует не создатель комнаты, +
    '''
    @app_commands.command(name = "пароль", description="Изменить пароль комнаты") # balance
    async def _пароль_комнаты(self, interaction: Interaction,
                              пароль: Optional[str] = None):
        user = User(interaction.user.id)
    # Проверяем ошибки
        Комната = user.Комната
        if not Комната:
            await Func.error(interaction, f'Вы не находитесь ни в одной комнате.')
            return
        room = Room(Комната)
        Создатель = room.Создатель
        if Создатель != interaction.user.id:
            await Func.error(interaction, f'Вы не являетесь создателем комнаты "{Комната}".\nЕё создатель: <@{Создатель}>.')
            return
    # Обновляем пароль
        room.update_field('Пароль', пароль)
        if пароль:  # Проверяем, был ли введён пароль
            await interaction.user.send(f'Установлен новый пароль для комнаты "{Комната}": `{пароль}`')  # Обрамляем пароль в `` для удобства копирования
            await interaction.response.send_message(embed = Embed.комната("Пароль успешно установлен!"))
        else: 
            await interaction.user.send(f'Пароль для комнаты "{Комната}" был сброшен')
            await interaction.response.send_message(embed = Embed.комната("Пароль успешно сброшен!"))
        

# 4 - изгнать
    '''
Комната изгнать:
Доступна только для создателя комнаты. Выгоняет участника, занося его в чёрный список. 
Если участника нет в комнате, то просто заносит в ЧС.
Пример: /комната изгнать 2938374747701
Где: 2938374747701 (обязательный ID игрока)
Возвращает ошибку, если:
•	Ты не состоишь ни в одной комнате, +
•	Команду использует не создатель комнаты, +
•	Уже идёт игра, +
•	Пытаетесь изгнать самого себя (предлагает воспользоваться командой: комната удалить), +
•	Пытаетесь изгнать уже изгнанного, +
•	
    '''
    @app_commands.command(name = "изгнать", description="Добавить игрока в ЧС")
    @app_commands.rename(member='игрока')
    async def _добавить_в_чс(self, interaction: Interaction, member: Member):
        user = User(interaction.user.id)
    # Проверяем ошибки
        Комната = user.Комната        
        if not Комната:
            await Func.error(interaction, 'Вы не находитесь ни в одной комнате.')
            return
        room = Room(Комната)
        Создатель = room.Создатель
        if Создатель != interaction.user.id:
            await Func.error(interaction, f'Вы не являетесь создателем комнаты "{Комната}".\nЕё создатель: <@{Создатель}>.')
            return
        Текущий_раунд = room.Текущий_раунд
        if Текущий_раунд != 'не начата':
            await Func.error(interaction, f'Игра уже началась - текущий раунд: "{Текущий_раунд}".\nДождитесь окончания игры.')
            return
        if interaction.user == member: # если игрок указывает себя
            await Func.error(interaction, 'Нельзя выгнать себя же.\nЕсли вы хотите закончить игру, введите: "/комната удалить"')
            return
        ЧС = room.ЧС
        if member.id in ЧС:
            await Func.error(interaction, 'Данный пользователь уже есть в чёрном списке. Чтобы посмотреть список, используйте команду: "/комната инфо"')
            return
        if len(ЧС) == 25:
            await Func.error(interaction, f'Превышено максимальное количество участников в чёрном списке (25/25). Рекомендуем поставить пароль, освободить место в чёрном списке, используя: "/комната принять" и повторить ввод данной команды.')
            return
    # Изгоняем человека, если он в комнате:
        text = ''
        if member.id in room.Участники:
            user_BL = User(member.id) # пользователь из ЧС
            user_BL.установить('Комната', None) # убираем ему атрибут комнаты
            text = ' и изгнан из комнаты'
            room.remove_member(member.id) # убираем его из списка участников
            guild = interaction.guild
            роль = guild.get_role(room.Роль)  # Получаем роль по её ID, сохраненному ранее. Если роли нет, вернёт None
            if роль:
                await member.remove_roles(роль) # Удаляем роль у него
            else: pass
        else: pass
    # Добавляем человека в ЧС:
        room.add_member_BL(member.id) # В БД комнаты
        await interaction.response.send_message(embed = Embed.комната("Минус один.", f'Пользователь {member} добавлен в ЧС{text}.'))


# 5 - принять
    '''
Комната принять: (возможно переименую)
Даёт возможность зайти ранее изгнанному участнику (убирает из чёрного списка)
Пример: /комната принять 2938374747701
Где: 2938374747701 (обязательный ID игрока)
Возвращает ошибку, если:
•	Если ты не состоишь ни в одной комнате, +
•	Команду использует не создатель комнаты, +
•	Пытаетесь вернуть человека не из списка изгнанных, +
    '''
    @app_commands.command(name = "принять", description="Убрать игрока из ЧС")
    @app_commands.rename(member='игрока')
    async def _добавить_в_чс(self, interaction: Interaction, member: Member):
        user = User(interaction.user.id)
    # Проверяем ошибки
        Комната = user.Комната        
        if not Комната:
            await Func.error(interaction, 'Вы не находитесь ни в одной комнате.')
            return
        room = Room(Комната)
        Создатель = room.Создатель
        if Создатель != interaction.user.id:
            await Func.error(interaction, f'Вы не являетесь создателем комнаты "{Комната}".\nЕё создатель: <@{Создатель}>.')
            return
        ЧС = room.ЧС
        if not (member.id in ЧС):
            await Func.error(interaction, 'Данного пользователя нет в чёрном списке.')
            return
    # Убираем из БД комнаты
        room.remove_member_BL(member.id) 
        await interaction.response.send_message(embed = Embed.комната("Выполнено!", f'Пользователь {member} убран из ЧС.'))


# 6 - ставки
    '''
Комната ставки:
Устанавливает тип ставок и максимальную ставку при необходимости.
Минимальная ставка: Равна большому блайнду – во всех типах.
1. Fixed-Limit (Фиксированный лимит)
Первые два раунда могут ставить только минимальную (большой блайнд), последние два – только максимальную.
Пример: /комната ставки Fixed-Limit 50 100
2. Pot-Limit (Пот-лимит)
Максимальная ставка равна текущему размеру банка (сумме всех ставок на столе на момент ставки).
Пример: /комната ставки Pot-Limit 50
3. No-Limit (Безлимит)
Игрок может поставить все свои фишки в любой момент.
Пример: /комната ставки No-Limit 50
4. Spread-Limit (Ограниченные ставки)
Устанавливается диапазон, в котором игроки могут делать ставки.
Пример: /комната ставки Spread-Limit 50 500
Где: /комната ставки <тип ставок> <мин.ставка> <макс.ставка>
Если не введены аргументы, выводить информацию о типах ставок. (или отдельно туториал сделать)
Возвращает ошибку, если: 
•	Ты не состоишь ни в одной комнате, +
•	Команду использует не создатель комнаты, +
•	Уже идёт игра, +
•	Как минимум одно из введённых чисел не положительное (ИЛИ не является числом ИЛИ не целое число - авто), +
•	Минимальная ставка больше максимальной, +
•	Минимальная ставка = нечётному числу, см ниже: + 
(для удобства деления на 2, т.е. расчёта малого блайнда. Хотя можно оптимизировать код, если давать вводить размер малого блайнда, а не большого),
•	Введены не все аргументы, но выбран тип покера, -
    '''
    @app_commands.command(name = "ставки", description="Изменить тип ставок и лимиты")
    @app_commands.describe(ставка="Выберите тип ставки для игры")
    @app_commands.choices(ставка=[
        discord.app_commands.Choice(name="Fixed-Limit (Фиксированный лимит)", value="Fixed-Limit"),
        discord.app_commands.Choice(name="Pot-Limit (Пот-лимит)", value="Pot-Limit"),
        discord.app_commands.Choice(name="No-Limit (Безлимит)", value="No-Limit"),
        discord.app_commands.Choice(name="Spread-Limit (Ограниченные ставки)", value="Spread-Limit"),
    ])
    @app_commands.rename(min='минимальная_ставка') # переименовывает атрибут в интерфейсе дискорда для пользователей
    @app_commands.rename(max='максимальная_ставка')
    #@app_commands.rename(ставка ='тип ставок')
    async def _добавить_в_чс(self, interaction: Interaction, 
                            ставка: discord.app_commands.Choice[str],
                            min: int,
                            max: int = None,
                            ):
        user = User(interaction.user.id)
    # Проверяем ошибки
        Комната = user.Комната        
        if not Комната:
            await Func.error(interaction, 'Вы не находитесь ни в одной комнате.')
            return
        room = Room(Комната)
        Создатель = room.Создатель
        if Создатель != interaction.user.id:
            await Func.error(interaction, f'Вы не являетесь создателем комнаты "{Комната}".\nЕё создатель: <@{Создатель}>.')
            return
        Текущий_раунд = room.Текущий_раунд
        if Текущий_раунд != 'не начата':
            await Func.error(interaction, f'Игра уже началась - текущий раунд: "{Текущий_раунд}".\nДождитесь окончания игры.')
            return
        txt = ''
        if ставка.value == "Fixed-Limit" or ставка.value == "Spread-Limit": # если выбраны типы ставок, в которых обязательно указывать и мин и макс:
            if not max:
                await Func.error(interaction, "Для типов ставок Fixed-Limit и Spread-Limit следует указывать максимальную ставку тоже.")
                return
            else:
                if min <= 0 or max <= min or min % 2 == 1: # проверка на чётность
                    await Func.error(interaction, f"Ставки должны быть положительными.\nМаксимальная ставка должна быть больше минимальной.\nМинимальная ставка должна быть чётной.")
                    return
                room.update_field("Макс_ставка", max)
                txt = f'\nМаксимальная ставка: {max}'
        else: # если выбраны типы ставок, в которых обязательно указывать только мин:
            if min <= 0 or min % 2 == 1:
                await Func.error(interaction, "Ставка должна быть положительной и чётной.")
                return
            room.update_field("Мин_ставка", min)
    # Изменяем тип ставок, выводим сообщение:
        room.update_field('Тип_ставок', ставка.value)
        await interaction.response.send_message(embed = Embed.комната("Игровые настройки обновлены!", f'Тип ставок: {ставка.name}\nМинимальная ставка: {min}{txt}'))



#                      ------  ВЗАИМОДЕЙСТВИЕ С КОМНАТОЙ   ------

#  - вступить
    '''
Комната вступить:
Присоединиться к уже существующей комнате. 
/комната вступить <Название (обязательно)> <Пароль (не обязательно)> 
Пример: /комната вступить Техас Uieo
Где: Техас – название комнаты, Uieo – пароль
Возвращает ошибку если:
•	ты состоишь в другой комнате, +
•	комнаты нет, +
•	вы были изгнаны из этой комнаты ранее (существуете в чёрном списке комнаты БД бота), +
•	уже идёт игра,
•	комната переполнена, +
•	пароль неправильный или не введён, +
    '''
    @app_commands.command(name = "вступить", description="Вступить в комнату")
    async def _вход_в_комнату(self, interaction: Interaction,
                                  название: str, 
                                  пароль: Optional[str] = None):
        user = User(interaction.user.id)
    # Проверяем ошибки
        Комната = user.Комната
        if Комната:
            await Func.error(interaction, f'Вы уже находитесь в комнате "{Комната}".\nДля выхода используйте "/комната выход"')
            return
        if not Data.Room.find_one({"Название": название}): # Проверяем, существует ли комната с таким именем
            await Func.error(interaction, f"Комнаты с названием '{название}' не существует.")
            return
        room = Room(название)
        if interaction.user.id in room.ЧС: # Если есть в списке ЧС
            await Func.error(interaction, f"Вы находитесь в чёрном списке данной комнаты.")
            return
        Текущий_раунд = room.Текущий_раунд
        if Текущий_раунд != 'не начата': # Если игра началась
            await Func.error(interaction, f'Игра уже началась - текущий раунд: "{Текущий_раунд}".\nДождитесь окончания игры.')
            return
        Участники = len(room.Участники)
        Макс = room.Максимум_участников
        if Участники == Макс: # Если макс. кол-во участников уже достигнуто
            await Func.error(interaction, f"Комната переполнена ({Участники}/{Макс}).")
            return
        password = room.Пароль
        if password: # пароль у комнаты есть
            if пароль != password: # введён другой пароль (или не введён)
                await Func.error(interaction, "Верный пароль не введён.")
                return
    # Добавляем базу данных игрока:
        user.установить('Комната', название)
        Role = discord.utils.get(interaction.user.guild.roles, id = room.Роль)
        await interaction.user.add_roles(Role) # достаём объект роли именно, а не ID её.
        Канал = room.Канал
        room.add_member(interaction.user.id) # добавляем игрока в БД комнаты
    # Отправляем сообщени об успехе:
        await interaction.response.send_message(embed = Embed.комната(
f'Вы вступили в комнату {название}',
f'Для начала игры перейдите в канал: <#{Канал}>'))
    # Отправляем сообщение в канал Комнаты:
        guild = self.bot.get_guild(room.ID_Сервера)
        channel = guild.get_channel(Канал)  # Получаем объект канала
        if channel:
            await channel.send(embed = Embed.комната(
f'Пополнение!',
f'В комнату вступил <@{user.id}>\n\
Количество игроков: {Участники+1}/{Макс}'))
        else: pass


# 8 - выход
    '''
Комната выход: (альтернативное название: /комната покинуть)
Выход из комнаты. 
Пример: /комната выход
Без аргументов.
Возвращает ошибку, если:
•	Если ты не состоишь ни в одной комнате,
•	Команду использует создатель комнаты,
•	Идёт игра, но выйти можно, если ты уже вышел через (Fold) [игрока нет в списке "Порядок_ходов"] 
– в таком случае сбрасывает кэш в банк и выгоняет из канала.
    '''
    @app_commands.command(name = "выход", description="Выйти из комнаты")
    async def _выход_из_комнаты(self, interaction: Interaction):
        user = User(interaction.user.id)
    # Проверяем ошибки
        Комната = user.Комната        
        if not Комната:
            await Func.error(interaction, 'Вы не находитесь ни в одной комнате.')
            return
        room = Room(Комната)
        Создатель = room.Создатель
        if Создатель == interaction.user.id:
            await Func.error(interaction, f'Вы являетесь создателем комнаты "{Комната}".\nОднако, вы можете удалить комнату, для этого введите: "/комната удалить"')
            return
        Текущий_раунд = room.Текущий_раунд
        Порядок_ходов = room.Порядок_ходов
        if (Текущий_раунд != 'не начата') and not (interaction.user.id in Порядок_ходов):
            await Func.error(interaction, f'Игра уже началась - текущий раунд: "{Текущий_раунд}".\nДождитесь окончания игры или сбросьте карты через Fold.')
            return
    # Убираем из БД игрока:
        user.установить('Комната', None)
    # Убираем роль:
        guild = interaction.guild
        роль = guild.get_role(room.Роль)  # Получаем роль по её ID, сохраненному ранее. Если роли нет, вернёт None
        if роль:
            await interaction.user.remove_roles(роль) # Удаляем роль у него
        else: pass
    # удаляем игрока из БД комнаты:
        Канал = room.Канал
        room.remove_member(interaction.user.id) 
    # Отправляем сообщени об успехе:
        await interaction.response.send_message(embed = Embed.комната(
f'Вы покинули комнату "{Комната}"'))
    # Отправляем сообщение в канал Комнаты:
        guild = self.bot.get_guild(room.ID_Сервера)
        channel = guild.get_channel(Канал)  # Получаем объект канала
        if channel:
            Участники = len(room.Участники)
            Макс = room.Максимум_участников
            await channel.send(embed = Embed.комната(
f'Комнату покинул игрок',
f'<@{user.id}>\n\
Количество игроков: {Участники}/{Макс}'))
        else: pass


# 4 - список
    '''
Комната список:
Возвращает список всех комнат на данном сервере (проходит по списку комнат у бота, выбирает только те, у которых совпадает ID сервера автора команды с ID сервера комнат).
Отображает:
•	Название комнат,
•	Наличие пароля (по возможности сортирует сначала без пароля),
•	Количество человек: текущее / максимальное (по возможности показывает полностью забитые комнаты в конце вне зависимости от наличия пароля),
•	Возможно, показывает Имя (главное без пинга) создателей комнат (чтобы можно было связаться, попросить пароль),
•	Минимальную и максимальную ставки,
Пример: /комната список
Возвращает другое сообщение (предупреждение / ошибку), если:
•	комнат на сервере нет.
*Возможно, стоит добавить возможность ручной сортировки, например, по величине ставок, кол-ву игроков и т.п.
    '''
    @app_commands.command(name = "список", description="Список комнат")
    async def _список_комнат_покер(self, interaction: Interaction):
        server_id = interaction.guild.id # user.
        rooms = Data.get_rooms_by_server(server_id) # достаёт из БД список со всеми комнатами на сервере
        if not rooms:
            await Func.error(interaction, "На этом сервере нет активных комнат.")
            return
        await interaction.response.defer()  # Поддерживает взаимодействие активным
        # print('rooms', rooms) # +
        room_list = Room.format_room_list(rooms) # сортирует комнаты по страницам
        # print('room list', room_list) # +
        # room_list = ['as', 'asss', '202'] # +
    # модуль для отображения стрелок, чтобы листать список комнат:
        manager = PageManager(room_list)
        embed = manager.get_embed(0)
        view = ListView(manager)
        await interaction.followup.send(embed=embed, view=view)




# - инфо / инфа
    '''
Если будешь изменять название, поменяй и в ошибке команды "/комната изгнать" - вообще с этим бы сделать что-то... автоматизировать там
Отображет всю информацию:
•	Название,
•	Правила,
•	участники (текущее /макс кол-ва) 
•	отдельной строкой: создатель,
•	Канал
•	ЧС (надо продумать, чтобы не выводил весь список, если он очень большой...) - можно ограничить сам список ЧС 25 участниками, например. Вывод в строку одну.
•	Тип_ставок, 
•	Мин_ставка, макс_ставка
•	Текущий_раунд
Пример: /комната инфо
Доступна всем участникам, автоматически определяет нужную комнату (берёт из БД).
Если вводит создатель, отправляет пароль ему в ЛС. (хотя по идее можно и для всех открыть, и выводить сообщение с паролем в канал с комнатой)
Возвращает ошибку, если:
•	Если ты не состоишь ни в одной комнате,
    '''



# отдельно туториал сделать о типах ставок

# переименовать???
    """
    @app_commands.command(name = "переименовать", description="изменить навзание") # amount: int = None, space: str = None): # Можно задать сумму и ставку сразу по желанию
    async def _расширение_группы(self, interaction: discord.Interaction, название: str):
        user = User(interaction.user.id)
        Группа = user.Группа
        if not Группа:
            await interaction.response.send_message(embed = Func.create_embed_error('Ошибка', f'Вы пока не состоите в группе. Для создания используйте: "/группа создать <название>"'), ephemeral=True, delete_after=60)
            return
        bot = User(MC.IDBOT)
        if Группа['Состав'][str(user.id)] != 'Лидер':
            await interaction.response.send_message(embed = Func.create_embed_error('Ошибка', f'Данная команда доступна только лидеру {user.id}'), ephemeral=True, delete_after=60)
            return
        if название is None:
            await interaction.response.send_message(embed = Func.create_embed_error('Ошибка', 'Введите новое название группы'), ephemeral=True, delete_after=60)
            return
        if название in bot.Группа:
            await interaction.response.send_message(embed = Func.create_embed_error('Ошибка', 'Данное название уже занято'), ephemeral=True, delete_after=60)
            return
        user.СозданиеГруппы(название)
        bot.СписокГрупп(название) # добавляем название группы в список боту
        await interaction.response.send_message(embed = Func.create_embed('Группа успешно переименована!', f'Старое название: {Группа['Название']}\nНовое название: {название}\nСостав: <@{user.id}> (Лидер)'))
    """




async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Poker_Room(bot))