import random
import json
import asyncio
import math
import discord
from discord.ext import commands

from data import UserData


class Fun(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color
        self.currently_fighting = []

        with open("bot/data/beanlations.json", "r") as beanlations_file:
            self.beanlations = json.load(beanlations_file)

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
            amount_won = math.ceil((player_roll - dealer_roll) / 6 * amount)
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
        p1_name = ctx.author.display_name
        p2_name = user.display_name

        if ctx.author in self.currently_fighting:
            await ctx.send("You are already fighting someone at the moment...")
            return

        elif user in self.currently_fighting:
            await ctx.send(f"**{user.display_name}** is already fighting someone at the moment...")
            return

        self.currently_fighting.append(ctx.author)
        self.currently_fighting.append(user)

        def check_p1(message):
            return message.author == ctx.author and message.channel == ctx.channel

        def check_p2(message):
            return message.author == user and message.channel == ctx.channel

        await ctx.send(f"{ctx.author.mention} wants to fight {user.mention}. Let's see how this goes...")

        while True:
            # Player 2 turn
            p2_response = None
            p2_resp_valid = False

            try:
                while not p2_resp_valid:
                    await ctx.send(f"{user.mention}, it's your turn! What will you do?")
                    await ctx.send("`punch`, `defend`, `end`")

                    p2_response = (await self.bot.wait_for("message", check=check_p2, timeout=30)).content

                    if p2_response == "punch":
                        damage = random.randint(10, 60)
                        p1_health -= damage
                        p2_resp_valid = True

                        await ctx.send(f"**{p2_name}** bazooka punched **{p1_name}** and did **{damage}** damage! wHoOaA...")

                    elif p2_response == "defend":
                        heal = random.randint(5, 30)
                        p2_health += heal
                        p2_resp_valid = True

                        await ctx.send(f"**{p2_name}** defended and regained **{heal}** health! Proteccshun...")

                    elif p2_response == "end":
                        p2_resp_valid = True
                        await ctx.send(f"**{p2_name}** chickened out, spam noob in the chat!")
                        self.currently_fighting.remove(ctx.author)
                        self.currently_fighting.remove(user)
                        return

                    else:
                        await ctx.send("Invalid response!")

            except asyncio.TimeoutError:
                await ctx.send(f"**{p2_name}** didn't respond in time what a noob...")
                self.currently_fighting.remove(ctx.author)
                self.currently_fighting.remove(user)
                return

            if p1_health <= 0:
                await ctx.send(f"Wow **{p1_name}** just died. Git gud noooob!")
                self.currently_fighting.remove(ctx.author)
                self.currently_fighting.remove(user)
                return
            else:
                await ctx.send(f"**{p1_name}** is now left with **{p1_health}** health.")

            # Player 1 turn
            p1_response = None
            p1_resp_valid = False

            try:
                while not p1_resp_valid:
                    await ctx.send(f"{ctx.author.mention}, it's your turn! What will you do?")
                    await ctx.send("`punch`, `defend`, `end`")

                    p1_response = (await self.bot.wait_for("message", check=check_p1, timeout=30)).content

                    if p1_response == "punch":
                        damage = random.randint(10, 60)
                        p2_health -= damage
                        p1_resp_valid = True

                        await ctx.send(f"**{p1_name}** bazooka punched **{p2_name}** and did **{damage}** damage! wHoOaA...")

                    elif p1_response == "defend":
                        heal = random.randint(5, 30)
                        p1_health += heal
                        p1_resp_valid = True

                        await ctx.send(f"**{p1_name}** defended and regained **{heal}** health! Proteccshun...")

                    elif p1_response == "end":
                        p1_resp_valid = True
                        await ctx.send(f"**{p1_name}** chickened out, spam noob in the chat!")
                        self.currently_fighting.remove(ctx.author)
                        self.currently_fighting.remove(user)
                        return

                    else:
                        await ctx.send("Invalid response!")

            except asyncio.TimeoutError:
                await ctx.send(f"**{p1_name}** didn't respond in time what a noob...")
                self.currently_fighting.remove(ctx.author)
                self.currently_fighting.remove(user)
                return

            if p2_health <= 0:
                await ctx.send(f"Wow **{p2_name}** just died. Git gud noooob!")
                self.currently_fighting.remove(ctx.author)
                self.currently_fighting.remove(user)
                return
            else:
                await ctx.send(f"**{p2_name}** is now left with **{p2_health}** health.")

    @commands.command(name="pray", help="Pray to the Bean Gods by reciting the Beanlations", brief="Pray to the Bean Gods")
    async def pray(self, ctx):
        prayer = random.choice(self.beanlations)
        await ctx.send(f"**{ctx.author.display_name}** recites a prayer:\n*{prayer}*")

