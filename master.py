import os
import json
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands
import datetime
import pytz

# Загрузка переменных окружения из .env файла
load_dotenv()

# Чтение конфигурационного файла
with open("config.json") as f:
    config = json.load(f)

# Переменные
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ADMIN_ROLE_ID = config["ADMIN_ROLE_ID"]
OLD_ROLE_ID = config["OLD_ROLE_ID"]
NEW_ROLE_ID = config["NEW_ROLE_ID"]
CHANNEL_ID = config["CHANNEL_ID"]
JOIN_TIME_THRESHOLD = config["JOIN_TIME_THRESHOLD"]
TIMEZONE = config["TIMEZONE"]
PREFIX = config["PREFIX"]
LOG_FILE = config["LOG_FILE"]

# Логгер
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# Интенты
intents = discord.Intents.all()

# Бот
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


# Получение списка участников с ролью OLD_ROLE
async def get_members_with_old_role(guild):
    old_role = guild.get_role(OLD_ROLE_ID)
    return old_role.members if old_role else []


# Смена роли и отправка сообщения в канал
async def change_role_and_send_message(member, old_role, new_role, channel):
    await member.remove_roles(old_role)
    await member.add_roles(new_role)
    await channel.send(f"{member.mention}, поздравляю с получением нового титула.")


# Проверка наличия админской роли
def check_admin_role(ctx):
    admin_role = ctx.guild.get_role(ADMIN_ROLE_ID)
    return admin_role in ctx.author.roles if admin_role else False


# Проверка времени пребывания участника на сервере
def check_join_time(member, threshold):
    join_time = member.joined_at.astimezone(pytz.timezone(TIMEZONE))
    current_time = datetime.datetime.now(pytz.timezone(TIMEZONE))
    return (current_time - join_time).total_seconds() > threshold


# Команда check
@bot.command()
async def C(ctx, threshold: int = JOIN_TIME_THRESHOLD):
    if not check_admin_role(ctx):
        await ctx.send("У вас нет прав на выполнение этой команды.")
        return

    guild = ctx.guild
    old_role = guild.get_role(OLD_ROLE_ID)
    new_role = guild.get_role(NEW_ROLE_ID)
    channel = bot.get_channel(CHANNEL_ID)

    if not old_role:
        logging.error("Роль OLD_ROLE не найдена.")
        await ctx.send("Роль OLD_ROLE не найдена.")
        return

    if not new_role:
        logging.error("Роль NEW_ROLE не найдена.")
        await ctx.send("Роль NEW_ROLE не найдена.")
        return

    if not channel:
        logging.error("Канал не найден.")
        await ctx.send("Канал не найден.")
        return

    for member in await get_members_with_old_role(guild):
        if check_join_time(member, threshold):
            await change_role_and_send_message(member, old_role, new_role, channel)


# Событие on_ready
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name}")


# Запуск бота
try:
    bot.run(TOKEN)
except Exception as e:
    logging.error(f"Произошла ошибка при запуске бота: {e}")
