import os
import time
import random
import asyncio
import dbl
import discord
from discord.ext import commands

from bot.data import Data

from cogs.currency import Currency
from cogs.jobs import Jobs
from cogs.shop import Shop
from cogs.fun import Fun
from cogs.image import Image
from cogs.words import Words
from cogs.reddit import Reddit
from cogs.vote import Vote
from cogs.owner import Owner

TOKEN = os.getenv("BEAN_TOKEN")
DBL_TOKEN = os.getenv("BEAN_DBL_TOKEN")
DBL_AUTH = os.getenv("DBL_AUTH")
THEME = discord.Color.green()
PREFIX = "b."
VOTE_REWARD = 100

intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(PREFIX, description="Bean Bot is a fun mini-game and economy bot.", intents=intents)
# TODO: uncomment when top.gg approved
# dbl_client = dbl.DBLClient(bot, DBL_TOKEN, webhook_port=8000, webhook_auth=DBL_AUTH)
presence_task = None
running = True

bot.add_cog(Currency(bot, THEME))
bot.add_cog(Jobs(bot, THEME))
bot.add_cog(Shop(bot, THEME))
bot.add_cog(Fun(bot, THEME))
bot.add_cog(Image(bot, THEME))
bot.add_cog(Words(bot, THEME))
bot.add_cog(Reddit(bot, THEME))
bot.add_cog(Vote(bot, THEME))
bot.add_cog(Owner(bot, THEME))


class HelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=THEME, description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)


bot.help_command = HelpCommand()


async def update_presence():
    while running:
        activity = discord.Activity(type=discord.ActivityType.playing, name="with the beans!")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(5)

        if not running:
            break

        server_count = len(bot.guilds)
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{server_count} servers")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(5)

        if not running:
            break

        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{PREFIX}help")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(5)


@bot.command(name="invite", help="Get the link to invite me to another server")
async def invite(ctx):
    invite_embed = discord.Embed(title="Bean Bot Invite Link", color=THEME, url="https://discord.com/api/oauth2/authorize?client_id=804243703455547462&permissions=537259088&scope=bot")
    invite_embed.add_field(name="Thank you for spreading word about Bean Bot!", value=":D")

    await ctx.send(embed=invite_embed)


@bot.event
async def on_command_error(ctx, exception):
    if isinstance(exception, commands.CommandOnCooldown):
        await ctx.send(f"Chill out bean bro, try again in {exception.retry_after} seconds...")

    elif isinstance(exception, commands.errors.MissingRequiredArgument):
        await ctx.send(f"`{exception.param.name}` is a required input.")

    elif isinstance(exception, commands.CommandNotFound):
        cmd_used = str(ctx.invoked_with)

        if cmd_used.endswith("rate"):
            if len(ctx.message.mentions) > 0:
                user = ctx.message.mentions[0]
            else:
                user = ctx.author

            rate = random.randint(0, 100)
            cmd_used = cmd_used[:-4]
            await ctx.send(f"**{user.display_name}** is {rate}% {cmd_used}.")

        else:
            await ctx.send("That's not a real command...")

    elif isinstance(exception, commands.MissingPermissions):
        await ctx.send("You don't have permission to run this command. You need the following permissions:")

        for missing_perm in exception.missing_perms:
            await ctx.send(missing_perm)

    else:
        raise exception


@bot.event
async def on_ready():
    global presence_task
    Data.create_tables()
    presence_task = bot.loop.create_task(update_presence())
    print(f"Bot logged into {len(bot.guilds)} servers.")


@bot.event
async def on_guild_join(guild):
    bean_server_id = 797019569037639693
    log_channel_id = 804951646173790208
    tester_role_id = 804770607002681405

    bean_server = bot.get_guild(bean_server_id)
    log_channel = bean_server.get_channel(log_channel_id)
    tester_role = bean_server.get_role(tester_role_id)

    guild_owner = bean_server.get_member(guild.owner_id)

    if guild_owner is None:
        guild_owner = guild.owner
    else:
        await guild_owner.add_roles(tester_role)

    await log_channel.send(f"Bean Bot joined server: **{guild.name}**\nOwner: **{guild_owner}**")


@bot.event
async def on_guild_remove(guild):
    bean_server_id = 797019569037639693
    log_channel_id = 804951646173790208
    tester_role_id = 804770607002681405

    bean_server = bot.get_guild(bean_server_id)
    log_channel = bean_server.get_channel(log_channel_id)
    tester_role = bean_server.get_role(tester_role_id)

    guild_owner = bean_server.get_member(guild.owner_id)

    if guild_owner is None:
        guild_owner = guild.owner
    else:
        await guild_owner.remove_roles(tester_role)

    await log_channel.send(f"Bean Bot left server: **{guild.name}**\nOwner: **{guild_owner}**")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.start(TOKEN))
    except KeyboardInterrupt:
        print()
    except SystemExit:
        print()
    finally:
        print("Exiting...")

        # Close bot connection
        running = False
        time.sleep(5)
        loop.run_until_complete(bot.logout())
        # TODO: uncomment when top.gg approved
        # asyncio.run(dbl_client.close())

        # Close Database connection
        Data.conn.commit()
        Data.c.close()
        Data.conn.close()
