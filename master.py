import asyncio
import datetime
import json
import logging

import discord
import pytz
from discord.ext import commands

# Read the configuration file
def read_config():
    """Reads and returns the configuration settings from a JSON file."""
    try:
        with open("config.json") as f:
            return json.load(f)
    except FileNotFoundError as e:
        logging.error(f"Failed to read configuration file: {e}")
        raise

config = read_config()

# Variables
TOKEN = #your bot token
ADMIN_ROLE_ID = config["ADMIN_ROLE_ID"]
OLD_ROLE_ID = config["OLD_ROLE_ID"]
NEW_ROLE_ID = config["NEW_ROLE_ID"]
CHANNEL_ID = config["CHANNEL_ID"]
JOIN_TIME_THRESHOLD = config["JOIN_TIME_THRESHOLD"]
TIMEZONE = config["TIMEZONE"]
PREFIX = config["PREFIX"]
LOG_FILE = config["LOG_FILE"]

# Logger
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# Intents
intents = discord.Intents.all()

# Bot instance
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

async def get_members_with_old_role(guild):
    """Returns a list of members who have the old role in the specified guild."""
    old_role = guild.get_role(OLD_ROLE_ID)
    return old_role.members if old_role else []

async def change_role_and_send_message_with_retry(member, old_role, new_role, channel, max_retries=5):
    """
    Attempts to change a member's role and send a notification message, with retries on failure.

    Args:
        member: The member object to change roles for.
        old_role: The role to remove from the member.
        new_role: The role to add to the member.
        channel: The channel object to send the notification message.
        max_retries: Maximum number of retries on failure.
    """
    for attempt in range(max_retries):
        try:
            await member.remove_roles(old_role)
            await member.add_roles(new_role)
            await channel.send(f"{member.mention}, поздравляю с новым титулом!")
            break  # Successful request, exit the loop
        except discord.Forbidden as e:
            logging.error(f"Error changing role and sending message: {e}")
            if attempt >= max_retries - 1:
                raise  # Raise exception if all retries are exhausted
            wait_time = 2 ** attempt  # Exponential backoff
            logging.info(f"Waiting {wait_time} seconds before retrying...")
            await asyncio.sleep(wait_time)

def check_admin_role(ctx):
    """Check if the context author has the admin role."""
    admin_role = ctx.guild.get_role(ADMIN_ROLE_ID)
    return admin_role in ctx.author.roles if admin_role else False

def check_join_time(member, threshold):
    """
    Checks if a member has joined before a certain threshold.

    Args:
        member: The member to check.
        threshold: The time threshold in seconds.

    Returns:
        Boolean indicating if the member joined before the threshold.
    """
    join_time = member.joined_at.astimezone(pytz.timezone(TIMEZONE))
    current_time = datetime.datetime.now(pytz.timezone(TIMEZONE))
    return (current_time - join_time).total_seconds() > threshold

async def handle_command(ctx, threshold: int = JOIN_TIME_THRESHOLD):
    """
    Handles the command execution logic, including role change and notification for eligible members.

    Args:
        ctx: The context under which the command was invoked.
        threshold: The join time threshold to consider a member eligible.
    """
    if not check_admin_role(ctx):
        await ctx.send("У вас нет прав на выполнение этой команды.")
        return

    guild = ctx.guild
    old_role = guild.get_role(OLD_ROLE_ID)
    new_role = guild.get_role(NEW_ROLE_ID)
    channel = bot.get_channel(CHANNEL_ID)

    if not old_role or not new_role or not channel:
        logging.error("Role or channel not found.")
        await ctx.send("Role or channel not found.")
        return

    members = await get_members_with_old_role(guild)
    if tasks := [
        change_role_and_send_message_with_retry(
            member, old_role, new_role, channel)
        for member in members
        if check_join_time(member, threshold)
    ]:
        await asyncio.gather(*tasks)
    else:
        await ctx.send("Достойных кандидатов не нашлось, милорд.")

@bot.command()
async def C(ctx, threshold: int = JOIN_TIME_THRESHOLD):
    """Command to handle role change and notification for members, uppercase version."""
    await handle_command(ctx, threshold)

@bot.command()
async def c(ctx, threshold: int = JOIN_TIME_THRESHOLD):
    """Command to handle role change and notification for members, lowercase version."""
    await handle_command(ctx, threshold)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready. Logs the bot's name or indicates if user is None."""
    if bot.user is not None:
        logging.info(f"Logged in as {bot.user.name}")
    else:
        logging.info("User is None")

# Run bot
try:
    bot.run(TOKEN)
except discord.LoginFailure as e:
    logging.error(f"Failed to run bot: {e}")
    raise