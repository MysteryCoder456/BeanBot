import json
import discord
from discord.ext import commands

from data import Data


class Words(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command(name="trackword", aliases=["tw"], help="Track how many times a word has been used", brief="Track a word's usage")
    async def trackword(self, ctx, *, word: str):
        Data.check_guild_entry(ctx.guild)

        word = word.strip()

        Data.c.execute("SELECT tracked_words FROM guilds WHERE id = :guild_id", {"guild_id": ctx.guild.id})
        tracked_words = json.loads(Data.c.fetchone()[0])

        if word in tracked_words:
            await ctx.send(f"The word **{word}** is already being tracked!")
            return

        tracked_words[word] = 0

        Data.c.execute(
            "UPDATE guilds SET tracked_words = :new_words WHERE id = :guild_id",
            {
                "new_words": json.dumps(tracked_words),
                "guild_id": ctx.guild.id
            }
        )
        Data.conn.commit()

        await ctx.send(f"The word **{word}** is now being tracked!")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command(name="untrackword", aliases=["utw"], help="Untrack a word", brief="Untrack a word")
    async def untrackword(self, ctx, *, word: str):
        Data.check_guild_entry(ctx.guild)

        word = word.strip()

        Data.c.execute("SELECT tracked_words FROM guilds WHERE id = :guild_id", {"guild_id": ctx.guild.id})
        tracked_words = json.loads(Data.c.fetchone()[0])

        try:
            del tracked_words[word]
        except KeyError:
            await ctx.send("This word was never being tracked...")
            return

        Data.c.execute(
            "UPDATE guilds SET tracked_words = :new_words WHERE id = :guild_id",
            {
                "new_words": json.dumps(tracked_words),
                "guild_id": ctx.guild.id
            }
        )
        Data.conn.commit()

        await ctx.send(f"The word **{word}** is no longer being tracked!")

    @commands.command(name="viewwordcount", aliases=["vwc"], help="View how many times a word has been said", brief="See a word's usage")
    async def viewwordcount(self, ctx, *, word: str):
        Data.check_guild_entry(ctx.guild)

        word = word.strip()

        Data.c.execute("SELECT tracked_words FROM guilds WHERE id = :guild_id", {"guild_id": ctx.guild.id})
        tracked_words = json.loads(Data.c.fetchone()[0])

        try:
            word_count = tracked_words[word]
        except KeyError:
            await ctx.send("This word is not being tracked...")
            return

        await ctx.send(f"The word **{word}** has been said **{word_count} times**!")
