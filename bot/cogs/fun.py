import random
import asyncio
import math
import discord
from discord.ext import commands

from data import UserData


class Fun(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

    @commands.command(name="gamble", aliases=["gam"], help="Gamble some money to see if you earn more than you spend", brief="Gamble some money")
    async def gamble(self, ctx, amount: int):
        UserData.check_user_entry(ctx.author)

        UserData.c.execute("SELECT wallet FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        wallet = UserData.c.fetchone()[0]

        if amount > wallet:
            amount_needed = amount - wallet
            await ctx.send(f"You don't have enough beans for that. You need {amount_needed} more beans.")
            return

        player_roll = random.randint(1, 6)
        dealer_roll = random.randint(1, 6)

        if player_roll > dealer_roll:
            amount_won = math.ceil((player_roll - dealer_roll) / 60 * amount)
        elif player_roll < dealer_roll:
            amount_won = -amount
        else:
            amount_won = 0

        UserData.c.execute(
            "UPDATE users SET wallet = :new_wallet WHERE id = :user_id",
            {
                "new_wallet": wallet + amount_won,
                "user_id": ctx.author.id
            }
        )
        UserData.conn.commit()

        gamble_embed = discord.Embed(title="Gambling Results")

        gamble_embed.add_field(name="You rolled", value=player_roll)
        gamble_embed.add_field(name="Dealer rolled", value=dealer_roll)

        if player_roll > dealer_roll:
            gamble_embed.color = discord.Color.green()
            gamble_embed.set_footer(text=f"You won {amount_won} beans!")
        elif player_roll < dealer_roll:
            gamble_embed.color = discord.Color.red()
            gamble_embed.set_footer(text=f"You lost {abs(amount_won)} beans!")
        else:
            gamble_embed.color = discord.Color.gold()
            gamble_embed.set_footer(text="You won nothing!")

        await ctx.send(embed=gamble_embed)

    @commands.command(name="fight", help="Pick a fight with someone", brief="Pick a fight with someone")
    async def fight(self, ctx, user: discord.User):
        p1_health = 100
        p2_health = 100
        winner = None

        def check_p1(message):
            return message.author == ctx.author and message.channel == ctx.channel

        def check_p2(message):
            return message.author == user and message.channel == ctx.channel

        while True:
            response = None
            try:
                while True:
                    response = await self.bot.wait_for("message", check=check_p2, timeout=30)
                    if response == "punch":
                        damage = random.randint(10, 60)
                        p1_health -= damage

            except asyncio.TimeoutError:
                await ctx.send("")
                break

