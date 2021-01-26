import discord
from discord.ext import commands

from data import UserData


class Vote(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color
        self.vote_reward = 100

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        if data["type"] == "upvote":
            user = self.bot.get_user(int(data["user"]))
            UserData.check_user_entry(user)
            print(f"{user.name} has upvoted the bot on Top.gg")
            await user.send(f"Thank you for voting for me on Top.gg. You have gotten {self.vote_reward} as a gift!")

            UserData.c.execute("SELECT wallet FROM users WHERE id = :user_id", {"user_id": user.id})
            wallet = UserData.c.fetchone()[0]

            UserData.c.execute(
                "UPDATE users SET wallet = :new_amount WHERE id = :user_id",
                {
                    "new_amount": wallet + self.vote_reward,
                    "user_id": user.id
                }
            )
            UserData.conn.commit()

    @commands.command(name="vote", help="Get links to Bot List site where you can vote for me", brief="Help me grow")
    async def vote(self, ctx):
        vote_embed = discord.Embed(title="Vote Bean Bot for Best Bot", color=self.theme_color)
        vote_embed.add_field(name="Top.gg", value="[Click here to vote](https://top.gg/bot/795564109922959361)")

        await ctx.send(embed=vote_embed)
