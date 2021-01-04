import os
import asyncio
import discord
from discord.ext import commands

from data import UserData

from cogs.currency import Currency
from cogs.jobs import Jobs
from cogs.owner import Owner

TOKEN = os.getenv("BEAN_TOKEN")
THEME = discord.Color.green()
PREFIX = "b."
bot = commands.Bot(PREFIX, description="Bean Bot is a fun mini-game and economy bot.")

bot.add_cog(Currency(bot, THEME))
bot.add_cog(Jobs(bot, THEME))
bot.add_cog(Owner(bot, THEME))


async def update_presence():
    while True:
        server_count = len(bot.guilds)
        activity = discord.Activity(type=discord.ActivityType.playing, name=f"with the beans | {server_count} servers | {PREFIX}help")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(10)


@bot.event
async def on_ready():
    bot.loop.create_task(UserData.auto_update_data())
    bot.loop.create_task(update_presence())
    print(f"Bot logged into {len(bot.guilds)} servers.")


if __name__ == "__main__":
    bot.run(TOKEN)
