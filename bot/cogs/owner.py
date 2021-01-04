import discord
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="data")
    @commands.is_owner()
    async def data(self, ctx):
        with open("bot/user_data.json", "r") as data_file:
            discord_file = discord.File(data_file)
            await ctx.author.send(file=discord_file)
