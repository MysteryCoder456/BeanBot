import os
import asyncio
import discord
from discord.ext import commands

from data import UserData

from cogs.currency import Currency

TOKEN = os.getenv("BEAN_TOKEN")
PREFIX = "b."
bot = commands.Bot(PREFIX, description="Bean Bot is a fun mini-game and currency bot.")

bot.add_cog(Currency(bot))


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
