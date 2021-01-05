import json
import discord
from discord.ext import commands

from data import UserData


class Shop(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

        with open("bot/data/shop_data.json", "r") as shop_file:
            self.shop_data = json.load(shop_file)

    @commands.group(name="shop", invoke_without_command=True, help="List the available items in the shop", brief="List buyable items")
    async def shop(self, ctx):
        shop_embed = discord.Embed(title="The Bean Shop", color=self.theme_color)

        for item in self.shop_data:
            item_name = item["name"]
            item_desc = item["description"]
            item_price = item["price"]

            shop_embed.add_field(name=item_name, value=f"{item_desc}\nPrice: **{item_price} beans**")

        await ctx.send(embed=shop_embed)
