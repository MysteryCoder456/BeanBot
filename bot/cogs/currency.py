import discord
from discord.ext import commands

from data import UserData


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_user_entry(self, user):
        if str(user.id) not in UserData.user_data:
            UserData.create_new_data(user)

    @commands.command(name="balance", aliases=["bal", "b"], description="Check how many beans someone has")
    async def balance(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author

        self.check_user_entry(user)
        wallet = UserData.get_data(user, "wallet")
        bank = UserData.get_data(user, "bank")

        embed = discord.Embed(title=f"{user.display_name}'s Bean Balance")
        embed.add_field(name="Wallet", value=f"{wallet} beans")
        embed.add_field(name="Bank", value=f"{bank} beans")

        await ctx.send(embed=embed)

    @commands.command(name="pay", aliases=["p"], description="Give beans to somebody")
    async def pay(self, ctx, user: discord.User, amount: int):
        if amount == 0:
            await ctx.send("Why are you using this command if you aren't giving them money?")
            return
        elif amount < 1:
            await ctx.send("You can't trick me into taking away their money fool!")
            return

        self.check_user_entry(ctx.author)
        self.check_user_entry(user)

        current_amount = UserData.get_data(ctx.author, "wallet")

        if amount > current_amount:
            amount_needed = amount - current_amount
            ctx.send(f"You don't have enough beans for that. You need {amount_needed} more beans.")
            return

        UserData.add_data(ctx.author, "wallet", -amount)
        UserData.add_data(user, "wallet", amount)

        await ctx.send(f"You paid {amount} beans to {user.display_name}.")
