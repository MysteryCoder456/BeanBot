import discord
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

    @commands.command(name="db")
    @commands.is_owner()
    async def db(self, ctx):
        with open("bot/data/data.db", "r") as data_file:
            discord_file = discord.File(data_file)
            await ctx.author.send(file=discord_file)
