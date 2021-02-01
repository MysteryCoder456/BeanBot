import os
import random
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
        subreddit_name.replace("r/", "")
        subred = self.reddit_client.subreddit(subreddit_name)

        listing = None

        if category == "top":
            listing = subred.top(limit=10)
        elif category == "hot":
            listing = subred.hot(limit=10)
        elif category == "controversial":
            listing = subred.controversial(limit=10)
        elif category == "new":
            listing = subred.new(limit=10)
        elif category == "gilded":
            listing = subred.gilded(limit=10)
        elif category == "rising":
            listing = subred.rising(limit=10)
        else:
            await ctx.send("That category is non-existent, just like your common sense smh...")
            return

        all_posts = [submission for submission in listing]
        post = random.choice(all_posts)

        if subred.over18 and not ctx.channel.is_nsfw():
            await ctx.send("This subreddit is marked NSFW. Please set this channel to NSFW to view this subreddit.")
            return

        post_embed = discord.Embed(title=post.title, color=self.theme_color, url=post.permalink)

        if post.selftext == "":
            if not post.is_self:
                post_embed.set_image(url=post.url)

        else:
            post_content = post.selftext

            if len(post_content) > 1024:
                post_content = post_content[:1021] + "..."

            post_embed.add_field(name="Content", value=post_content, inline=False)

        post_embed.add_field(name="Score", value=post.score)
        post_embed.set_footer(text=f"Post on r/{post.subreddit.display_name} by u/{post.author}")

        await ctx.send(embed=post_embed)

    @commands.command(name="meme", help="Get a meme to brighten up your day")
    async def meme(self, ctx, category: str = "hot"):
        subred = self.reddit_client.subreddit("memes")

        listing = None

        if category == "top":
            listing = subred.top(limit=10)
        elif category == "hot":
            listing = subred.hot(limit=10)
        elif category == "controversial":
            listing = subred.controversial(limit=10)
        elif category == "new":
            listing = subred.new(limit=10)
        elif category == "gilded":
            listing = subred.gilded(limit=10)
        elif category == "rising":
            listing = subred.rising(limit=10)
        else:
            await ctx.send("That category is non-existent, just like your common sense smh...")
            return

        all_posts = [submission for submission in listing]
        post = random.choice(all_posts)

        post_embed = discord.Embed(title=post.title, color=self.theme_color, url=post.permalink)

        if post.selftext == "":
            if not post.is_self:
                post_embed.set_image(url=post.url)

        else:
            post_content = post.selftext

            if len(post_content) > 1024:
                post_content = post_content[:1021] + "..."

            post_embed.add_field(name="Content", value=post_content, inline=False)

        post_embed.add_field(name="Score", value=post.score)
        post_embed.set_footer(text=f"Post on r/{post.subreddit.display_name} by u/{post.author}")

        await ctx.send(embed=post_embed)
