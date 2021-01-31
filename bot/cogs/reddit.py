import os
import praw
import discord
from discord.ext import commands


class Reddit(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

        self.reddit_client = praw.Reddit(
            client_id=os.environ["REDDIT_PUS"],
            client_secret=os.environ["REDDIT_SECRET"],
            user_agent="Bean Bot",
            username=os.environ["REDDIT_USERNAME"],
            password=os.environ["REDDIT_PASSWORD"]
        )

    @commands.command(name="reddit", help="Browse a subreddit")
    async def reddit(self, ctx, subreddit_name: str, category: str = "hot"):
        subreddit_name.replace("r/", "", 1)
        subred = self.reddit_client.subreddit(subreddit_name)

        listing = None

        if category == "top":
            listing = subred.top(limit=1)
        elif category == "hot":
            listing = subred.hot(limit=1)
        elif category == "controversial":
            listing = subred.controversial(limit=1)
        elif category == "new":
            listing = subred.new(limit=1)
        elif category == "gilded":
            listing = subred.gilded(limit=1)
        else:
            await ctx.send("That category is non-existent, just like your common sense smh...")
            return

        post = next(listing)

        post_embed = discord.Embed(title=post.title, color=self.theme_color, url=post.url)
        if post.selftext == "":
            pass
        else:
            post_embed.add_field(name="Content", value=post.selftext, inline=False)
        post_embed.add_field(name="Score", value=post.score)
        post_embed.set_footer(text=f"Post by u/{post.author}")

        await ctx.send(embed=post_embed)
