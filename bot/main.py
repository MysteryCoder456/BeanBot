import os
import random
import asyncio
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
THEME = discord.Color.green()
PREFIX = "b."
bot = commands.Bot(PREFIX, description="Bean Bot is a fun mini-game and economy bot.")

bot.add_cog(Currency(bot, THEME))
bot.add_cog(Jobs(bot, THEME))
bot.add_cog(Shop(bot, THEME))
bot.add_cog(Fun(bot, THEME))
bot.add_cog(Image(bot, THEME))
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
    while True:
        server_count = len(bot.guilds)
        activity = discord.Activity(type=discord.ActivityType.playing, name=f"with the beans | {server_count} servers | {PREFIX}help")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(10)


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


@bot.event
async def on_ready():
    UserData.create_tables()
    bot.loop.create_task(update_presence())
    print(f"Bot logged into {len(bot.guilds)} servers.")


# @bot.event
# async def on_disconnect():
#     print("Exiting...")
#     UserData.conn.commit()
#     UserData.c.close()
#     UserData.conn.close()


if __name__ == "__main__":
    bot.run(TOKEN)
    # loop = asyncio.get_event_loop()
    # try:
    #     loop.run_until_complete(bot.start(TOKEN))
    # except KeyboardInterrupt:
    #     loop.run_until_complete(bot.logout())
    # except SystemExit:
    #     loop.run_until_complete(bot.logout())
    # finally:
    #     loop.close()
