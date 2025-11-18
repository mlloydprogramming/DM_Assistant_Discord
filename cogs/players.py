import discord
import constants
from discord import app_commands
from discord.ext import commands
import db

class Players(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
    async def add_party_xp_spent(self, interaction: discord.Interaction, amount: int):
        level = db.get_party_level()
        user_id = interaction.user.id
        current = db.get_balance(user_id)
        if amount > current:
            await interaction.response.send_message(
                f"You cannot spend **{amount}** coins as you only have **{current}** coins.",
                ephemeral=True,
            )
        # Spend Player coins
        db.spend_balance(user_id, amount)
        bal = db.get_balance(user_id)

        # Update the party XP spent total
        db.add_party_xp_spent(amount)

        total_xp_spent = db.get_party_xp_spent()

        await interaction.response.send_message(
            f"Spent **{amount}** coints. New balance is **{bal}** coins.\n"
            f"The party has now spent a total of **{total_xp_spent}** XP. You have **{constants.LEVEL_REQUIREMENTS[level+1] - total_xp_spent}** XP left to raise the party level.",
        )
        

    @app_commands.command(name="get_party_level", description="Get the party's current level")
    async def get_party_level(self, interaction: discord.Interaction):
        level = db.get_party_level()
        await interaction.response.send_message(
            f"The party is currently at level **{level}**."
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Players(bot))