import random
import discord
from discord.ext import commands

from bot.data import Data


class Vote(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color
        self.vote_reward = 100

    # TODO: uncomment when top.gg approved
    # @commands.Cog.listener()
    # async def on_dbl_vote(self, data):
    #     if data["type"] == "upvote":
    #         user = self.bot.get_user(int(data["user"]))
    #         Data.check_user_entry(user)
    #         print(f"{user} has upvoted the bot on Top.gg")
    #         try:
    #             await user.send(f"Thank you for voting for me on Top.gg. You have gotten {self.vote_reward} beans as a gift!")
    #         except discord.errors.Forbidden:
    #             print(f"Couldn't send a message to {user}")

    #         Data.c.execute("SELECT wallet FROM users WHERE id = :user_id", {"user_id": user.id})
    #         wallet = Data.c.fetchone()[0]

    #         Data.c.execute(
    #             "UPDATE users SET wallet = :new_amount WHERE id = :user_id",
    #             {
    #                 "new_amount": wallet + self.vote_reward,
    #                 "user_id": user.id
    #             }
    #         )
    #         Data.conn.commit()

    @commands.command(name="vote", help="Get links to Bot List sites where you can vote for me")
    async def vote(self, ctx):
        # TODO: uncomment when top.gg approved
        # vote_embed = discord.Embed(title="Vote Bean Bot for Best Bot", color=self.theme_color)
        # vote_embed.add_field(name="Top.gg", value="[Click here to vote](https://top.gg/bot/795564109922959361)")

        # await ctx.send(embed=vote_embed)
        await ctx.send("Coming soon...")
