import discord
from discord.ext import commands

from data import UserData


class Currency(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

    @commands.command(name="balance", aliases=["bal", "b"], help="Check how many beans someone has", brief="Check your beans")
    async def balance(self, ctx, user: discord.User=None):
        if user is None:
            user = ctx.author

        UserData.check_user_entry(user)

        UserData.c.execute("SELECT wallet, bank FROM users WHERE id = :user_id", {"user_id": user.id})
        data = UserData.c.fetchone()
        wallet = data[0]
        bank = data[1]

        embed = discord.Embed(title=f"{user.display_name}'s Bean Balance", color=self.theme_color)
        embed.add_field(name="Wallet", value=f"{wallet} beans")
        embed.add_field(name="Bank", value=f"{bank} beans")

        await ctx.send(embed=embed)

    @commands.command(name="pay", aliases=["p"], help="Give beans to somebody", brief="Give beans to somebody")
    async def pay(self, ctx, user: discord.User, amount: int):
        if amount == 0:
            await ctx.send("Why are you using this command if you aren't giving them money?")
            return
        elif amount < 1:
            await ctx.send("You can't trick me into taking away their money fool!")
            return

        UserData.check_user_entry(ctx.author)
        UserData.check_user_entry(user)

        # Get current wallet balances
        UserData.c.execute("SELECT wallet FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        current_balance = UserData.c.fetchone()[0]

        UserData.c.execute("SELECT wallet FROM users WHERE id = :user_id", {"user_id": user.id})
        current_reciever_balance = UserData.c.fetchone()[0]

        # Ensure user has enough to pay
        if amount > current_balance:
            amount_needed = amount - current_balance
            await ctx.send(f"You don't have enough beans for that. You need {amount_needed} more beans.")
            return

        # Update balances
        UserData.c.execute(
            "UPDATE users SET wallet = :new_amount WHERE id = :user_id",
            {
                "new_amount": current_balance - amount,
                "user_id": ctx.author.id
            }
        )
        UserData.c.execute(
            "UPDATE users SET wallet = :new_amount WHERE id = :user_id",
            {
                "new_amount": current_reciever_balance + amount,
                "user_id": user.id
            }
        )

        UserData.conn.commit()

        await ctx.send(f"You paid {amount} beans to {user.display_name}.")
