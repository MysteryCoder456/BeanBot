import os
import json
import discord
from discord.ext import commands

from data import UserData


class Shop(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "data")

        with open(os.path.join(data_dir, "shop_data.json"), "r") as shop_file:
            self.shop_data = json.load(shop_file)

        self.is_vowel = lambda ch: (ch in ('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'))

    @commands.command(name="shop", help="List the available items in the shop", brief="List buyable items")
    async def shop(self, ctx):
        shop_embed = discord.Embed(title="The Bean Shop", color=self.theme_color)

        for item in self.shop_data:
            item_name = item["name"]
            item_desc = item["description"]
            item_price = item["price"]

            shop_embed.add_field(name=item_name, value=f"{item_desc}\nPrice: **{item_price} beans**")

        await ctx.send(embed=shop_embed)

    @commands.command(name="buy", help="Purchase an item from the shop", brief="Buy from the shop")
    async def buy(self, ctx, quantity: int, *, item_name):
        UserData.check_user_entry(ctx.author)

        UserData.c.execute("SELECT wallet, inventory FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        data = UserData.c.fetchone()
        wallet_amount = data[0]
        inventory = json.loads(data[1])

        item_info = None

        for item in self.shop_data:
            if item["name"].lower() == item_name.lower():
                item_info = item
                break

        if item_info is None:
            return

        item_n = item_info["name"]
        total_price = item_info["price"] * quantity

        if total_price > wallet_amount:
            amount_needed = total_price - wallet_amount
            await ctx.send(f"You don't have enough beans for that. You need {amount_needed} more beans.")
            return

        # Find out if the item being bought is a duplicate
        item_duplicate = False
        duplicate_index = None
        for (i, item) in enumerate(inventory):
            if item["name"] == item_n:
                item_duplicate = True
                duplicate_index = i
                break

        if item_duplicate:
            inventory[duplicate_index]["quantity"] += quantity
        else:
            inventory_entry = {
                "name": item_n,
                "description": item_info["description"],
                "quantity": quantity,
                "function_id": item_info["function_id"],
                "function_vars": item_info["function_vars"]
            }
            inventory.append(inventory_entry)

        UserData.c.execute(
            "UPDATE users SET inventory = :new_json WHERE id = :user_id",
            {
                "new_json": json.dumps(inventory),
                "user_id": ctx.author.id
            }
        )

        UserData.c.execute(
            "UPDATE users SET wallet = :new_amount WHERE id = :user_id",
            {
                "new_amount": wallet_amount - total_price,
                "user_id": ctx.author.id
            }
        )

        UserData.conn.commit()

        if quantity > 1:
            await ctx.send(f"You bought **{quantity} {item_n}s** for **{total_price} beans**!")
        else:
            await ctx.send(f"You bought **{item_n}** for **{total_price} beans**!")

    @commands.command(name="inventory", aliases=["inv"], help="List all the items in your inventory", brief="View your inventory")
    async def inventory(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        UserData.check_user_entry(user)

        UserData.c.execute("SELECT inventory FROM users WHERE id = :user_id", {"user_id": user.id})
        inventory = json.loads(UserData.c.fetchone()[0])

        inventory_embed = discord.Embed(title=f"{user.display_name}'s Inventory", color=self.theme_color)

        for item in inventory:
            item_name = item["name"]
            item_desc = item["description"]
            item_quantity = item["quantity"]
            inventory_embed.add_field(name=item_name, value=f"Quantity: {item_quantity}\n{item_desc}", inline=False)

        await ctx.send(embed=inventory_embed)

    @commands.command(name="use", help="Use an item in your inventory", brief="Use an item in your inventory")
    async def use(self, ctx, *, item_name):
        UserData.check_user_entry(ctx.author)

        UserData.c.execute("SELECT bank_capacity, inventory FROM users WHERE id = :user_id", {"user_id": ctx.author.id})
        data = UserData.c.fetchone()
        bank_capacity = data[0]
        inventory = json.loads(data[1])

        # Find the desired item in inventory
        inv_index = None
        for (i, item) in enumerate(inventory):
            if item["name"].lower() == item_name.lower():
                inv_index = i
                break

        if inv_index is None:
            return

        # Remove that item from inventory
        item_info = inventory[inv_index]

        if item_info["quantity"] > 1:
            item_info["quantity"] -= 1
        else:
            inventory.pop(inv_index)

        # Perform the item's action
        f_id = item_info["function_id"]

        if f_id is not None:
            f_vars = item_info["function_vars"]

            if f_id == 0:
                bank_capacity += f_vars["bank_capacity_increase"]
                UserData.c.execute(
                    "UPDATE users SET bank_capacity = :new_capacity WHERE id = :user_id",
                    {
                        "new_capacity": bank_capacity,
                        "user_id": ctx.author.id
                    }
                )

        # Write inventory changes to DB
        UserData.c.execute(
            "UPDATE users SET inventory = :new_inventory WHERE id = :user_id",
            {
                "new_inventory": json.dumps(inventory),
                "user_id": ctx.author.id
            }
        )
        UserData.conn.commit()

        item_n = item_info["name"]

        if self.is_vowel(item_n[0]):
            await ctx.send(f"You used an **{item_n}**!")
        else:
            await ctx.send(f"You used a **{item_n}**!")
