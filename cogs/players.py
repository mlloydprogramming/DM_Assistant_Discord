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
            f"You have **{bal}** XP.",
            ephemeral=True
        )

    @app_commands.command(name="spend_balance", description="Spend a specific amount from your balance")
    async def spend_balance(self, interaction: discord.Interaction, amount: int):
        user_id = interaction.user.id
        current = db.get_balance(user_id)
        if amount > current:
            await interaction.response.send_message(
                f"You cannot spend **{amount}** XP as you only have **{current}** XP.",
                ephemeral=True,
            )
        else:
            new_balance = db.spend_balance(user_id, amount)
            await interaction.response.send_message(
                f"Spend **{amount}** XP. New balance is **{new_balance}** XP.",
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
                f"You cannot spend **{amount}** XP as you only have **{current}** XP.",
                ephemeral=True,
            )
        # Spend Player XP
        db.spend_balance(amount)
        bal = db.get_balance(user_id)

        # Update the party XP spent total
        db.add_party_xp_spent(amount, role_id)

        total_xp_spent = db.get_party_xp_spent(role_id)

        await interaction.response.send_message(
            f"Spent **{amount}** XP. New balance is **{bal}** XP.\n"
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
            cost_str = f"{cost} XP" if isinstance(cost, int) else cost

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
                f"{item_info['description']}",
                ephemeral=True,
            )
            return
        
        current = db.get_balance(user_id)

        if current < cost:
            await interaction.response.send_message(
                f"You need **{cost}** XP to buy **{item}**, but you only have **{current}** XP.",
                ephemeral=True,
            )
            return
        
        db.spend_balance(user_id, cost)

        await interaction.response.send_message(
            f"You purchased **{item}** for **{cost}** XP!\n\n"
            f"**{item_info['description']}**",
            ephemeral=True,
        )

    @app_commands.command(name="get_character_progress", description="Get your character's equipment, armor, and weapon levels and XP spent")
    async def get_character_progress(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        equipment_level = db.get_equipment_level(user_id)
        equipment_xp_spent = db.get_equipment_xp_spent(user_id)
        armor_level = db.get_armor_level(user_id)
        armor_xp_spent = db.get_armor_xp_spent(user_id)
        weapon_level = db.get_weapon_level(user_id)
        weapon_xp_spent = db.get_weapon_xp_spent(user_id)

        await interaction.response.send_message(
            f"**Your Character Progress:**\n"
            f"Equipment Level: **{equipment_level}** | XP Spent: **{equipment_xp_spent}**/{constants.EQUIPMENT_LEVEL_REQUIREMENTS.get(equipment_level + 1, 'Max')}\n"
            f"Armor Level: **{armor_level}** | XP Spent: **{armor_xp_spent}**/{constants.ARMOR_LEVEL_REQUIREMENTS.get(armor_level + 1, 'Max')}\n"
            f"Weapon Level: **{weapon_level}** | XP Spent: **{weapon_xp_spent}**/{constants.WEAPON_LEVEL_REQUIREMENTS.get(weapon_level + 1, 'Max')}",
            ephemeral=True,
        )

    @app_commands.command(name="add_equipment_xp", description="Add XP to your equipment")
    async def add_equipment_xp(self, interaction: discord.Interaction, amount: int):
        user_id = interaction.user.id
        balance = db.get_balance(user_id)
        if amount > balance:
            await interaction.response.send_message(
                f"You cannot spend **{amount}** XP as you only have **{balance}** XP.",
                ephemeral=True,
            )
            return
        db.spend_balance(user_id, amount)

        bal = db.get_balance(user_id)
        db.add_equipment_xp_spent(user_id, amount)
        equipment_xp_status = db.get_equipment_xp_spent(user_id)
        equipment_level = db.get_equipment_level(user_id)

        await interaction.response.send_message(
            f"Spent **{amount}** XP. New balance is **{bal}** XP.\n"
            f"You have now spent a total of **{equipment_xp_status}** XP on your equipment. You have **{constants.EQUIPMENT_LEVEL_REQUIREMENTS.get(equipment_level + 1, 'Max') - equipment_xp_status}** XP left to reach the next equipment level.",
            ephemeral=True
        )

    @app_commands.command(name="add_armor_xp", description="Add XP to your armor")
    async def add_armor_xp(self, interaction: discord.Interaction, amount: int):
        user_id = interaction.user.id
        balance = db.get_balance(user_id)
        if amount > balance:
            await interaction.response.send_message(
                f"You cannot spend **{amount}** XP as you only have **{balance}** XP.",
                ephemeral=True,
            )
            return
        db.spend_balance(user_id, amount)

        bal = db.get_balance(user_id)
        db.add_armor_xp_spent(user_id, amount)
        armor_xp_status = db.get_armor_xp_spent(user_id)
        armor_level = db.get_armor_level(user_id)

        await interaction.response.send_message(
            f"Spent **{amount}** XP. New balance is **{bal}** XP.\n"
            f"You have now spent a total of **{armor_xp_status}** XP on your armor. You have **{constants.ARMOR_LEVEL_REQUIREMENTS.get(armor_level + 1, 'Max') - armor_xp_status}** XP left to reach the next armor level.",
            ephemeral=True
        )

    @app_commands.command(name="add_weapon_xp", description="Add XP to your weapon")
    async def add_weapon_xp(self, interaction: discord.Interaction, amount: int):
        user_id = interaction.user.id
        balance = db.get_balance(user_id)
        if amount > balance:
            await interaction.response.send_message(
                f"You cannot spend **{amount}** XP as you only have **{balance}** XP.",
                ephemeral=True,
            )
            return
        db.spend_balance(user_id, amount)

        bal = db.get_balance(user_id)
        db.add_weapon_xp_spent(user_id, amount)
        weapon_xp_status = db.get_weapon_xp_spent(user_id)
        weapon_level = db.get_weapon_level(user_id)

        await interaction.response.send_message(
            f"Spent **{amount}** XP. New balance is **{bal}** XP.\n"
            f"You have now spent a total of **{weapon_xp_status}** XP on your weapon. You have **{constants.WEAPON_LEVEL_REQUIREMENTS.get(weapon_level + 1, 'Max') - weapon_xp_status}** XP left to reach the next weapon level.",
            ephemeral=True
        )        

async def setup(bot: commands.Bot):
    await bot.add_cog(Players(bot))