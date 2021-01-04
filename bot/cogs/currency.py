import discord
from discord.ext import commands

from data import UserData


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_user_entry(self, user_id):
        if user_id not in UserData.user_data:
            UserData.user_data[user_id] = UserData.create_new_data()

    @commands.command(name="balance", aliases=["bal", "b"], description="Check how many beans someone has")
    async def balance(self, ctx, user: discord.User=None):
        if user is None:
            user = ctx.author

        self.check_user_entry(user.id)
        wallet = UserData.user_data[user.id]["wallet"]
        bank = UserData.user_data[user.id]["bank"]

        embed = discord.Embed(title=f"{user.display_name}'s Bean Balance")
        embed.add_field(name="Wallet", value=f"{wallet} beans")
        embed.add_field(name="Bank", value=f"{bank} beans")

        await ctx.send(embed=embed)

    @commands.command(name="pay", description="Give beans to somebody")
    async def pay(self, ctx, user: discord.User, amount):
        self.check_user_entry(ctx.author.id)
        self.check_user_entry(user.id)

        UserData.user_data[ctx.author.id]["wallet"] -= int(amount)
        UserData.user_data[user.id]["wallet"] += int(amount)

        await ctx.send(f"You paid {amount} beans to {user.display_name}.")
