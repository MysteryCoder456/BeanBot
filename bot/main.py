import os
import time
import random
import asyncio
import dbl
import discord
from discord.ext import commands

from data import UserData

from cogs.currency import Currency
from cogs.jobs import Jobs
from cogs.shop import Shop
from cogs.fun import Fun
from cogs.image import Image
from cogs.owner import Owner

TOKEN = os.getenv("BEAN_TOKEN")
DBL_TOKEN = os.getenv("BEAN_DBL_TOKEN")
DBL_AUTH = os.getenv("DBL_AUTH")
THEME = discord.Color.green()
PREFIX = "b."
bot = commands.Bot(PREFIX, description="Bean Bot is a fun mini-game and economy bot.")
dbl_client = dbl.DBLClient(bot, DBL_TOKEN, webhook_port=8000, webhook_auth=DBL_AUTH)
presence_task = None
running = True

bot.add_cog(Currency(bot, THEME))
bot.add_cog(Jobs(bot, THEME))
bot.add_cog(Shop(bot, THEME))
bot.add_cog(Fun(bot, THEME))
bot.add_cog(Image(bot, THEME))
bot.add_cog(Owner(bot, THEME))


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


@bot.command(name="invite", help="Get the link to invite me to another server", brief="Invite me to another server")
async def invite(ctx):
    invite_embed = discord.Embed(title="Bean Bot Invite Link", color=THEME, url="https://discord.com/api/oauth2/authorize?client_id=795564109922959361&permissions=388208&scope=bot")
    invite_embed.add_field(name="Thank you for spreading word about Bean Bot!", value=":D")

    await ctx.send(embed=invite_embed)


@bot.event
async def on_command_error(ctx, exception):
    if isinstance(exception, commands.errors.CommandOnCooldown):
        await ctx.send(f"Chill out bean bro, try again in {exception.retry_after} seconds...")

    elif isinstance(exception, commands.errors.MissingRequiredArgument):
        await ctx.send(f"`{exception.param.name}` is a required input.")

    elif isinstance(exception, commands.errors.CommandNotFound):
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
    else:
        raise exception


@bot.event
async def on_dbl_vote(data):
    print("hello")
    print(data)
    # UserData.check_user_entry(user)

    # UserData.c.execute("SELECT wallet FROM users WHERE id = :user_id", {"user_id": user.id})
    # wallet = UserData.c.fetchone()[0]

    # UserData.c.execute(
    #     "UPDATE users SET wallet = :new_amount WHERE id = :user_id",
    #     {
    #         "new_amount": wallet + self.vote_reward,
    #         "user_id": user.id
    #     }
    # )


@bot.event
async def on_ready():
    global presence_task
    UserData.create_tables()
    presence_task = bot.loop.create_task(update_presence())
    print(f"Bot logged into {len(bot.guilds)} servers.")


# @bot.event
# async def on_disconnect():
#     print("Exiting...")
#     UserData.conn.commit()
#     UserData.c.close()
#     UserData.conn.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.start(TOKEN))
    except KeyboardInterrupt:
        print()
    except SystemExit:
        print()
    finally:
        running = False
        time.sleep(5)
        loop.run_until_complete(bot.logout())
        asyncio.run(dbl_client.close())
