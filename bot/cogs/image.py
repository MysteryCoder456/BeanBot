import os
import discord
from discord.ext import commands
import cv2


class Image(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color
        self.images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "images")

    @commands.command(name="abandon", help="Baby abandon meme", brief="Baby abandon meme")
    async def abandon(self, ctx, *, text):
        img_path = os.path.join(self.images_dir, "abandon.jpg")

        image = cv2.imread(img_path)
        cv2.putText(image, text, (60, 305), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

        cache_filename = os.path.join(self.images_dir, "cache.jpg")
        cv2.imwrite(cache_filename, image)

        await ctx.send(file=discord.File(cache_filename))
