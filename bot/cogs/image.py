import os
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

        # Create cache directory
        if "cache" not in os.listdir(self.images_dir):
            os.mkdir(os.path.join(self.images_dir, "cache"))

    @commands.command(name="abandon", help="Baby abandon meme")
    async def abandon(self, ctx, *, text: str):
        img_path = os.path.join(self.images_dir, "abandon.jpg")
        font_path = os.path.join(self.fonts_dir, "Arial.ttf")
        image = PIL.Image.open(img_path)
        draw = ImageDraw.Draw(image)

        font_size = 50
        font = ImageFont.truetype(font=font_path, size=font_size)

        while True:
            w, _ = draw.textsize(text, font=font)

            if w <= 155 or font_size <= 1:
                break

            font_size -= 1
            font = ImageFont.truetype(font=font_path, size=font_size)

        draw.text((54, 275), text, fill=(0, 0, 0), font=font)

        cache_filename = os.path.join(self.images_dir, "cache", "abandon.jpg")
        image.save(cache_filename)

        await ctx.send(file=discord.File(cache_filename))

    @commands.command(name="slap", help="Batman slap meme")
    async def slap(self, ctx, person1: discord.User, person2: discord.User = None, *, text: str = None):
        if person2 is None:
            slapper = ctx.author
            victim = person1
        else:
            slapper = person1
            victim = person2

        img_path = os.path.join(self.images_dir, "slap.jpg")
        pfp1_path = os.path.join(self.images_dir, "cache", "pfp1.jpg")
        pfp2_path = os.path.join(self.images_dir, "cache", "pfp2.jpg")

        await slapper.avatar_url.save(pfp1_path)
        await victim.avatar_url.save(pfp2_path)

        image = PIL.Image.open(img_path)
        pfp1 = PIL.Image.open(pfp1_path).resize((150, 150))
        pfp2 = PIL.Image.open(pfp2_path).resize((150, 150))

        image.paste(pfp1, (457, 304))
        image.paste(pfp2, (202, 412))

        if text is not None:
            text_split = text.split(",")
            text1 = text_split[0]
            text2 = text_split[1]
            font_path = os.path.join(self.fonts_dir, "Comic Sans MS.ttf")

            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font=font_path, size=21)

            draw.text((362, 46), text1, fill=(0, 0, 0), font=font)
            draw.text((10, 24), text2, fill=(0, 0, 0), font=font)

        cache_filename = os.path.join(self.images_dir, "cache", "slap.jpg")
        image.save(cache_filename)

        await ctx.send(file=discord.File(cache_filename))

    @commands.command(name="lick", help="JoJo lick meme")
    async def lick(self, ctx, person1: discord.User, person2: discord.User = None):
        if person2 is None:
            licker = ctx.author
            lickee = person1
        else:
            licker = person1
            lickee = person2

        img_path = os.path.join(self.images_dir, "lick.jpeg")
        pfp1_path = os.path.join(self.images_dir, "cache", "pfp1.jpg")
        pfp2_path = os.path.join(self.images_dir, "cache", "pfp2.jpg")

        await licker.avatar_url.save(pfp1_path)
        await lickee.avatar_url.save(pfp2_path)

        image = PIL.Image.open(img_path)
        pfp1 = PIL.Image.open(pfp1_path).resize((450, 450))
        pfp2 = PIL.Image.open(pfp2_path).resize((425, 425))

        image.paste(pfp1, (784, 54))
        image.paste(pfp2, (171, 85))

        cache_filename = os.path.join(self.images_dir, "cache", "lick.jpg")
        image.save(cache_filename)

        await ctx.send(file=discord.File(cache_filename))
