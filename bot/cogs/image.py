import os
import re
import discord
from discord.ext import commands
import PIL
from PIL import ImageFont, ImageDraw


class Image(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color
        self.images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "images")
        self.fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "fonts")

    @commands.command(name="abandon", help="Baby abandon meme", brief="Baby abandon meme")
    async def abandon(self, ctx, *, text):
        try:
            img_path = os.path.join(self.images_dir, "abandon.jpg")
            font_path = os.path.join(self.fonts_dir, "Arial.ttf")

            font = ImageFont.truetype(font=font_path, size=17)
            image = PIL.Image.open(img_path)
            draw = ImageDraw.Draw(image)
            draw.text((60, 280), text, fill=(0, 0, 0), font=font)

            cache_filename = os.path.join(self.images_dir, "cache.jpg")
            image.save(cache_filename)

            await ctx.send(file=discord.File(cache_filename))
        except Exception as e:
            print(e)
