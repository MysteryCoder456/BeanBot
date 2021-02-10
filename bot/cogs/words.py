import json
import discord
from discord.ext import commands

from bot.data import Data


class Words(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

        self.tracked_words = {}
        Data.c.execute("SELECT id, tracked_words FROM guilds")

        for data_entry in Data.c.fetchall():
            guild_id = data_entry[0]
            words = json.loads(data_entry[1])
            self.tracked_words[guild_id] = words

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        guild_id = message.guild.id
        Data.check_guild_entry(message.guild)

        try:
            for word in self.tracked_words[guild_id]:
                if word in message.content:
                    self.tracked_words[guild_id][word] += message.content.count(word)
                    Data.c.execute(
                        "UPDATE guilds SET tracked_words = :new_words WHERE id = :guild_id",
                        {
                            "new_words": json.dumps(self.tracked_words[guild_id]),
                            "guild_id": guild_id
                        }
                    )
                    Data.conn.commit()
        except KeyError:
            self.tracked_words[guild_id] = {}

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command(name="trackword", aliases=["tw"], help="Track how many times a word has been used")
    async def trackword(self, ctx, *, word: str):
        Data.check_guild_entry(ctx.guild)
        guild_id = ctx.guild.id

        word = word.strip()

        Data.c.execute("SELECT tracked_words FROM guilds WHERE id = :guild_id", {"guild_id": ctx.guild.id})
        self.tracked_words[guild_id] = json.loads(Data.c.fetchone()[0])

        if word in self.tracked_words[guild_id]:
            await ctx.send(f"The word **{word}** is already being tracked!")
            return

        self.tracked_words[guild_id][word] = -1

        Data.c.execute(
            "UPDATE guilds SET tracked_words = :new_words WHERE id = :guild_id",
            {
                "new_words": json.dumps(self.tracked_words[guild_id]),
                "guild_id": ctx.guild.id
            }
        )
        Data.conn.commit()

        await ctx.send(f"The word **{word}** is now being tracked!")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command(name="untrackword", aliases=["utw"], help="Untrack a word")
    async def untrackword(self, ctx, *, word: str):
        Data.check_guild_entry(ctx.guild)
        guild_id = ctx.guild.id

        word = word.strip()

        Data.c.execute("SELECT tracked_words FROM guilds WHERE id = :guild_id", {"guild_id": ctx.guild.id})
        self.tracked_words[guild_id] = json.loads(Data.c.fetchone()[0])

        try:
            del self.tracked_words[guild_id][word]
        except KeyError:
            await ctx.send("This word was never being tracked...")
            return

        Data.c.execute(
            "UPDATE guilds SET tracked_words = :new_words WHERE id = :guild_id",
            {
                "new_words": json.dumps(self.tracked_words[guild_id]),
                "guild_id": ctx.guild.id
            }
        )
        Data.conn.commit()

        await ctx.send(f"The word **{word}** is no longer being tracked!")

    @commands.command(name="viewwordcount", aliases=["vwc"], help="View how many times a word has been said")
    async def viewwordcount(self, ctx, *, word: str):
        Data.check_guild_entry(ctx.guild)
        guild_id = ctx.guild.id

        word = word.strip()

        Data.c.execute("SELECT tracked_words FROM guilds WHERE id = :guild_id", {"guild_id": ctx.guild.id})
        self.tracked_words[guild_id] = json.loads(Data.c.fetchone()[0])

        try:
            word_count = self.tracked_words[guild_id][word]
        except KeyError:
            await ctx.send("This word is not being tracked...")
            return

        await ctx.send(f"The word **{word}** has been said **{word_count} times**!")

    @commands.command(name="viewtrackedwords", aliases=["vtw"], help="View all the words being tracked")
    async def viewtrackedwords(self, ctx):
        Data.check_guild_entry(ctx.guild)
        guild_id = ctx.guild.id

        Data.c.execute("SELECT tracked_words FROM guilds WHERE id = :guild_id", {"guild_id": ctx.guild.id})
        self.tracked_words[guild_id] = json.loads(Data.c.fetchone()[0])

        if len(self.tracked_words[guild_id]) > 0:
            await ctx.send("These are the words currently being tracked:")
            words_string = "\n".join([f"**{i+1}) {word}**: {self.tracked_words[guild_id][word]}" for (i, word) in enumerate(self.tracked_words[guild_id])])
            await ctx.send(words_string)
        else:
            await ctx.send("There aren't any words being tracked on this server...")
