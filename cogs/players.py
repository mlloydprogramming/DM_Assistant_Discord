import discord
import constants
from discord import app_commands
from discord.ext import commands
import db

class Players(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def buy_autocomplete(self, interaction:discord.Interaction, current: str):
        options = []

        for name in constants.SHOP_OPTIONS.keys():
            if current.lower() in name.lower():
                options.append(app_commands.Choice(name=name, value=name))
        return options[:25]

    @app_commands.command(name="players_test", description="Test players command")
    async def players_test(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Players test command is working",
            ephemeral=True
        )
    
    @app_commands.command(name="get_balance", description="Get your current balance")
    async def get_balance(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        bal = db.get_balance(user_id)
        await interaction.response.send_message(
            f"You have **{bal}** coins.",
            ephemeral=True
        )

    @app_commands.command(name="spend_balance", description="Spend a specific amount from your balance")
    async def spend_balance(self, interaction: discord.Interaction, amount: int):
        user_id = interaction.user.id
        current = db.get_balance(user_id)
        if amount > current:
            await interaction.response.send_message(
                f"You cannot spend **{amount}** coins as you only have **{current}** coins.",
                ephemeral=True,
            )
        else:
            new_balance = db.spend_balance(user_id, amount)
            await interaction.response.send_message(
                f"Spend **{amount}** coins. New balance is **{new_balance}** coins.",
                ephemeral=True,
            )

    @app_commands.command(name="get_party_xp_spent", description="Get total party XP spent")
    async def get_party_xp_spent(self, interaction: discord.Interaction):
        xp_spent = db.get_party_xp_spent()
        level = db.get_party_level()
        await interaction.response.send_message(
            f"The party has spent a total of **{xp_spent}** XP. You have **{constants.LEVEL_REQUIREMENTS[level+1] - xp_spent}** XP left to raise the party level.",
        )

    @app_commands.command(name="add_party_xp_spent", description="Add to the party's total XP spent")
    async def add_party_xp_spent(self, interaction: discord.Interaction, amount: int, role: discord.Role):
        role_id = role.id
        level = db.get_party_level(role_id)
        user_id = interaction.user.id
        current = db.get_balance(user_id)
        if amount > current:
            await interaction.response.send_message(
                f"You cannot spend **{amount}** coins as you only have **{current}** coins.",
                ephemeral=True,
            )
        # Spend Player coins
        db.spend_balance(amount)
        bal = db.get_balance(user_id)

        # Update the party XP spent total
        db.add_party_xp_spent(amount, role_id)

        total_xp_spent = db.get_party_xp_spent(role_id)

        await interaction.response.send_message(
            f"Spent **{amount}** coins. New balance is **{bal}** coins.\n"
            f"The party **{role.name}** has now spent a total of **{total_xp_spent}** XP. You have **{constants.LEVEL_REQUIREMENTS[level+1] - total_xp_spent}** XP left to raise the party level.",
        )

    @app_commands.command(name="get_party_level", description="Get the party's current level")
    async def get_party_level(self, interaction: discord.Interaction, role: discord.Role):
        role_id = role.id
        level = db.get_party_level(role_id)
        await interaction.response.send_message(
            f"The party **{role.name}** is currently at level **{level}**."
        )

    @app_commands.command(name="set_character_sheet", description="Set your character sheet URL")
    async def set_character_sheet(self, interaction: discord.Interaction, url: str):
        user_id = interaction.user.id
        db.set_character_sheet(user_id, url)
        await interaction.response.send_message(
            "Your character sheet URL has been updated.",
            ephemeral=True,
        )
    
    @app_commands.command(name="get_character_sheet", description="Get your character sheet URL")
    async def get_character_sheet(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        url = db.get_character_sheet(user_id)
        if url:
            await interaction.response.send_message(
                f"Your character sheet URL is: {url}",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "You have not set a character sheet URL yet.",
                ephemeral=True,
            )

    

    @app_commands.command(name="shop", description="View available shop options")
    async def shop(self, interaction: discord.Interaction):
        lines: list[str] = []

        for item_name, item_data in constants.SHOP_OPTIONS.items():
            cost = item_data["cost"]
            cost_str = f"{cost} coins" if isinstance(cost, int) else cost

            lines.append(
                f"**{item_name}** - Cost: **{cost_str}**\n"
                f"{item_data['description']}"
            )
        
        shop_message = "\n\n".join(lines)

        await interaction.response.send_message(
            f"**Available Shop Options:**\n\n{shop_message}",
            ephemeral=True,
        )

    @app_commands.command(name="buy", description="Buy an item from the shop")
    @app_commands.describe(item="What do you want to buy?")
    @app_commands.autocomplete(item=buy_autocomplete)
    async def buy(self, interaction: discord.Interaction, item: str):
        user_id = interaction.user.id
        if item not in constants.SHOP_OPTIONS:
            await interaction.response.send_message("That is not something you can buy.", ephemeral=True)
            return
        
        item_info = constants.SHOP_OPTIONS[item]
        cost = item_info["cost"]

        if cost == "variable":
            await interaction.response.send_message(
                "This item has a variable cost. Please utilize the dedicated command.\n"
                "Use ```/add_party_xp_spent``` to add XP to the party pool.",
                ephemeral=True,
            )
            return
        
        current = db.get_balance(user_id)

        if current < cost:
            await interaction.response.send_message(
                f"You need **{cost}** coins to buy **{item}**, but you only have **{current}** coins.",
                ephemeral=True,
            )
            return
        
        db.spend_balance(user_id, cost)

        await interaction.response.send_message(
            f"You purchased **{item}** for **{cost}** coins!\n\n"
            f"**{item_info['description']}**",
            ephemeral=True,
        )
            

async def setup(bot: commands.Bot):
    await bot.add_cog(Players(bot))