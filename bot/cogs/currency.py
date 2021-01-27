import random
import discord
from discord.ext import commands

from data import UserData


class Currency(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

    @commands.command(name="balance", aliases=["bal", "b"], help="Check how many beans someone has", brief="Check your beans")
    async def balance(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author

        UserData.check_user_entry(user)

        UserData.c.execute("SELECT wallet, bank, bank_capacity FROM users WHERE id = :user_id", {"user_id": user.id})
        data = UserData.c.fetchone()
        wallet = data[0]
        bank = data[1]
        bank_capacity = data[2]

        embed = discord.Embed(title=f"{user.display_name}'s Bean Balance", color=self.theme_color)
        embed.add_field(name="Wallet", value=f"{wallet} beans")
        embed.add_field(name="Bank", value=f"{bank}/{bank_capacity} beans")

        await ctx.send("You can get beans for free if you vote for me on Top.gg. Do `b.vote` for more info...", embed=embed)

    @commands.command(name="pay", aliases=["p"], help="Give beans to somebody", brief="Give beans to somebody")
    async def pay(self, ctx, user: discord.User, amount: int):
        if amount == 0:
            await ctx.send("Why are you using this command if you aren't giving them beans?")
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

        await ctx.send(f"You paid **{amount} beans** to {user.display_name}.")

    @commands.command(name="deposit", aliases=["dep"], help="Deposit beans to your bank where they will stay safe", brief="Deposit beans to bank")
    async def deposit(self, ctx, amount):
        UserData.check_user_entry(ctx.author)

        # Get current wallet and banks balances
        UserData.c.execute("SELECT wallet, bank, bank_capacity FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        data = UserData.c.fetchone()
        wallet_amount = data[0]
        bank_amount = data[1]
        bank_capacity = data[2]

        if str(amount) == "all" or str(amount) == "max":
            amount = wallet_amount

            if bank_amount + amount > bank_capacity:
                amount = bank_capacity - bank_amount

        else:
            amount = int(amount)

            if amount == 0:
                await ctx.send("Why are you using this command if you aren't depositing anything?")
                return
            elif amount < 1:
                await ctx.send("There's a command for withdrawing as well, you know...")
                return

            # Ensure user has enough to deposit
            if amount > wallet_amount:
                amount_needed = amount - wallet_amount
                await ctx.send(f"You don't have enough beans for that. You need {amount_needed} more beans.")
                return

            if bank_amount + amount > bank_capacity:
                await ctx.send("You don't have enough space in your bank for that.")
                return

            # Ensure user doesn't go over the capacity

        # Update balances
        UserData.c.execute(
            "UPDATE users SET wallet = :new_wallet_amount, bank = :new_bank_amount WHERE id = :user_id",
            {
                "new_wallet_amount": wallet_amount - amount,
                "new_bank_amount": bank_amount + amount,
                "user_id": ctx.author.id
            }
        )

        UserData.conn.commit()
        await ctx.send(f"You deposited **{amount} beans** to your bank.")

    @commands.command(name="withdraw", aliases=["with"], help="Withdraw beans from your bank when you want to use them", brief="Withdraw beans from bank")
    async def withdraw(self, ctx, amount):
        UserData.check_user_entry(ctx.author)

        # Get current wallet and banks balances
        UserData.c.execute("SELECT wallet, bank FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        data = UserData.c.fetchone()
        wallet_amount = data[0]
        bank_amount = data[1]

        if str(amount) == "all" or str(amount) == "max":
            amount = bank_amount
        else:
            amount = int(amount)

            if amount == 0:
                await ctx.send("Why are you using this command if you aren't withdrawing anything?")
                return
            elif amount < 1:
                await ctx.send("There's a command for depositing as well, you know...")
                return

            # Ensure user has enough to deposit
            if amount > bank_amount:
                await ctx.send("You don't have that many beans in your bank.")
                return

        # Update balances
        UserData.c.execute(
            "UPDATE users SET wallet = :new_wallet_amount, bank = :new_bank_amount WHERE id = :user_id",
            {
                "new_wallet_amount": wallet_amount + amount,
                "new_bank_amount": bank_amount - amount,
                "user_id": ctx.author.id
            }
        )

        UserData.conn.commit()
        await ctx.send(f"You withdrew **{amount} beans** from your bank.")


    @commands.command(name="rob", aliases=["steal"], help="\"Borrow\" some money from people without telling", brief="\"Borrow\" some money")
    @commands.cooldown(1, 120)
    async def rob(self, ctx, victim: discord.Member):
        UserData.check_user_entry(ctx.author)
        UserData.check_user_entry(victim)

        UserData.c.execute("SELECT wallet FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        robber_wallet = UserData.c.fetchone()[0]

        UserData.c.execute("SELECT wallet FROM users WHERE id = :user_id", {"user_id": victim.id})
        victim_wallet = UserData.c.fetchone()[0]

        if robber_wallet < 150:
            amount_needed = 150 - robber_wallet
            await ctx.send(f"You need at least 150 beans for that. You need {amount_needed} more beans...")
            return

        chance = random.randint(0, 100)

        if chance > 35:
            amount_stolen = random.randint(0, victim_wallet)
            await ctx.send(f"OMG! You stole **{amount_stolen} beans** from **{victim.display_name}**...")
        else:
            amount_stolen = random.randint(-150, -70)
            await ctx.send(f"You got caught stealing from **{victim.display_name}** and had to pay them **{abs(amount_stolen)} beans**")

        UserData.c.execute(
            "UPDATE users SET wallet = :new_wallet WHERE id = :user_id",
            {
                "new_wallet": robber_wallet + amount_stolen,
                "user_id": ctx.author.id
            }
        )
        UserData.c.execute(
            "UPDATE users SET wallet = :new_wallet WHERE id = :user_id",
            {
                "new_wallet": victim_wallet - amount_stolen,
                "user_id": victim.id
            }
        )

        UserData.conn.commit()


