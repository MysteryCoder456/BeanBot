import os
import random
import json
import asyncio
import math
import discord
from discord.ext import commands

from data import Data


class Fun(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color
        self.currently_fighting = []
        self.deleted_msgs = {}
        self.edited_msgs = {}
        self.snipe_limit = 15

        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "data")

        with open(os.path.join(data_dir, "beanlations.json"), "r") as beanlations_file:
            self.beanlations = json.load(beanlations_file)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        ch_id_str = str(message.channel.id)

        if ch_id_str not in self.deleted_msgs:
            self.deleted_msgs[ch_id_str] = []

        self.deleted_msgs[ch_id_str].append(message)

        if len(self.deleted_msgs[ch_id_str]) > self.snipe_limit:
            self.deleted_msgs[ch_id_str].pop(0)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        ch_id_str = str(before.channel.id)

        if ch_id_str not in self.edited_msgs:
            self.edited_msgs[ch_id_str] = []

        self.edited_msgs[ch_id_str].append((before, after))

        if len(self.edited_msgs[ch_id_str]) > self.snipe_limit:
            self.edited_msgs[ch_id_str].pop(0)

    @commands.command(name="gamble", aliases=["gam"], help="Gamble some money to see if you earn more than you spend")
    async def gamble(self, ctx, amount: int):
        Data.check_user_entry(ctx.author)

        Data.c.execute("SELECT wallet FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        wallet = Data.c.fetchone()[0]

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

        Data.c.execute(
            "UPDATE users SET wallet = :new_wallet WHERE id = :user_id",
            {
                "new_wallet": wallet + amount_won,
                "user_id": ctx.author.id
            }
        )
        Data.conn.commit()

        gamble_embed = discord.Embed(title="Gambling Results")

        gamble_embed.add_field(name="You rolled", value=str(player_roll))
        gamble_embed.add_field(name="Dealer rolled", value=str(dealer_roll))

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

    @commands.command(name="fight", help="Pick a fight with someone")
    async def fight(self, ctx, user: discord.User):
        if ctx.author.id == user.id:
            await ctx.send("You can't do that to yourself, smh...")
            return

        if ctx.author in self.currently_fighting:
            await ctx.send("You are already fighting someone at the moment...")
            return

        elif user in self.currently_fighting:
            await ctx.send(f"**{user.display_name}** is already fighting someone at the moment...")
            return

        p1_health = 100
        p2_health = 100
        p1_name = ctx.author.display_name
        p2_name = user.display_name

        self.currently_fighting.append(ctx.author)
        self.currently_fighting.append(user)

        Data.check_user_entry(ctx.author)
        Data.check_user_entry(user)

        # Load player powerups
        Data.c.execute("SELECT powerups FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        p1_powerups = json.loads(Data.c.fetchone()[0])
        Data.c.execute("SELECT powerups FROM users WHERE id = :user_id", {"user_id": user.id})
        p2_powerups = json.loads(Data.c.fetchone()[0])

        def check_p1(message):
            return message.author == ctx.author and message.channel == ctx.channel

        def check_p2(message):
            return message.author == user and message.channel == ctx.channel

        async def end():
            self.currently_fighting.remove(ctx.author)
            self.currently_fighting.remove(user)

            if p1_health != 100 and p2_health != 100:
                if len(p1_powerups) > 0:
                    Data.c.execute(
                        "UPDATE users SET powerups = :new_powerups WHERE id = :user_id",
                        {
                            "new_powerups": "{}",
                            "user_id": ctx.author.id
                        }
                    )
                    Data.conn.commit()
                    await ctx.send(f"{ctx.author.mention}, you have used up your active powerups.")

                if len(p2_powerups) > 0:
                    Data.c.execute(
                        "UPDATE users SET powerups = :new_powerups WHERE id = :user_id",
                        {
                            "new_powerups": "{}",
                            "user_id": user.id
                        }
                    )
                    Data.conn.commit()
                    await ctx.send(f"{user.mention}, you have used up your active powerups.")

        await ctx.send(f"{ctx.author.mention} wants to fight {user.mention}. Let's see how this goes...")

        while True:
            # Player 2 turn
            p2_resp_valid = False

            try:
                while not p2_resp_valid:
                    await ctx.send(f"{user.mention}, it's your turn! What will you do?\n`punch`, `defend`, `end`")

                    p2_response = (await self.bot.wait_for("message", check=check_p2, timeout=30)).content

                    if p2_response == "punch":
                        damage = random.randint(10, 45)

                        try:
                            damage += p2_powerups["damage_increase"]
                        except KeyError:
                            pass

                        p1_health -= damage
                        p2_resp_valid = True

                        await ctx.send(f"**{p2_name}** bazooka punched **{p1_name}** and did **{damage}** damage! wHoOaA...")

                    elif p2_response == "defend":
                        heal = random.randint(5, 30)
                        p2_health += heal
                        p2_resp_valid = True

                        await ctx.send(f"**{p2_name}** defended and regained **{heal}** health! Proteccshun...")

                    elif p2_response == "end":
                        await ctx.send(f"**{p2_name}** chickened out, spam noob in the chat!")
                        await end()
                        return

                    else:
                        await ctx.send("Invalid response!")

            except asyncio.TimeoutError:
                await ctx.send(f"**{p2_name}** didn't respond in time what a noob...")
                await end()
                return

            if p1_health <= 0:
                await ctx.send(f"Wow **{p1_name}** just died. Git gud noooob!")
                await end()
                return
            else:
                await ctx.send(f"**{p1_name}** is now left with **{p1_health}** health.")

            # Player 1 turn
            p1_resp_valid = False

            try:
                while not p1_resp_valid:
                    await ctx.send(f"{ctx.author.mention}, it's your turn! What will you do?\n`punch`, `defend`, `end`")

                    p1_response = (await self.bot.wait_for("message", check=check_p1, timeout=30)).content

                    if p1_response == "punch":
                        damage = random.randint(10, 45)

                        try:
                            damage += p1_powerups["damage_increase"]
                        except KeyError:
                            pass

                        p2_health -= damage
                        p1_resp_valid = True

                        await ctx.send(f"**{p1_name}** bazooka punched **{p2_name}** and did **{damage}** damage! wHoOaA...")

                    elif p1_response == "defend":
                        heal = random.randint(5, 30)
                        p1_health += heal
                        p1_resp_valid = True

                        await ctx.send(f"**{p1_name}** defended and regained **{heal}** health! Proteccshun...")

                    elif p1_response == "end":
                        await ctx.send(f"**{p1_name}** chickened out, spam noob in the chat!")
                        await end()
                        return

                    else:
                        await ctx.send("Invalid response!")

            except asyncio.TimeoutError:
                await ctx.send(f"**{p1_name}** didn't respond in time what a noob...")
                await end()
                return

            if p2_health <= 0:
                await ctx.send(f"Wow **{p2_name}** just died. Git gud noooob!")
                await end()
                return
            else:
                await ctx.send(f"**{p2_name}** is now left with **{p2_health}** health.")

    @commands.command(name="powerups", aliases=["power", "pu"], help="See your currently active powerups")
    async def powerups(self, ctx):
        Data.check_user_entry(ctx.author)

        Data.c.execute("SELECT powerups FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        powerups = json.loads(Data.c.fetchone()[0])
        powerups_embed = discord.Embed(title=f"{ctx.author.display_name}'s Active Powerups", color=self.theme_color)

        for powerup in powerups:
            powerup_name = " ".join(powerup.split("_")).title()
            powerups_embed.add_field(name=powerup_name, value=powerups[powerup])

        await ctx.send(embed=powerups_embed)

    @commands.command(name="pray", help="Pray to the Bean Gods by reciting the Beanlations")
    async def pray(self, ctx, *, prayer=None):
        if prayer is None:
            prayer = random.choice(self.beanlations)

        await ctx.send(f"**{ctx.author.display_name}** recites a prayer:\n*{prayer}*")

    @commands.has_guild_permissions(administrator=True)
    @commands.command(name="snipe", aliases=["sn"], help="See a recently deleted message")
    async def snipe(self, ctx, limit: int = 1):
        if limit > self.snipe_limit:
            await ctx.send(f"Maximum snipe limit is {self.snipe_limit}")
            return

        msgs = self.deleted_msgs[str(ctx.channel.id)][::-1][:limit]
        snipe_embed = discord.Embed(title="Message Snipe", color=self.theme_color)

        for msg in msgs:
            snipe_embed.add_field(name=msg.author.display_name, value=msg.content, inline=False)

        await ctx.send(embed=snipe_embed)

    @commands.has_guild_permissions(administrator=True)
    @commands.command(name="editsnipe", aliases=["esn"], help="See a recently edited message")
    async def editsnipe(self, ctx, limit: int = 1):
        if limit > self.snipe_limit:
            await ctx.send(f"Maximum snipe limit is {self.snipe_limit}")
            return

        msgs = self.edited_msgs[str(ctx.channel.id)][::-1][:limit]
        editsnipe_embed = discord.Embed(title="Edit Snipe", color=self.theme_color)

        for msg in msgs:
            editsnipe_embed.add_field(name=msg.author.display_name, value=f"{msg[0].content} **-->** {msg[1].content}", inline=False)

        await ctx.send(embed=editsnipe_embed)
