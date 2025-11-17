import discord
from discord import app_commands
from discord.ext import commands
from db import get_balance, set_balance

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
        bal = get_balance(user_id)
        await interaction.response.send_message(
            f"You have **{bal}** coins.",
            ephemeral=True
        )

    @app_commands.command(name="spend_balance", description="Spend a specific amount from your balance")
    async def spend_balance(self, interaction: discord.Interaction, amount: int):
        user_id = interaction.user.id
        current = get_balance(user_id)
        if amount > current:
            await interaction.response.send_message(
                f"You cannot spend **{amount}** coins as you only have **{current}** coins.",
                ephemeral=True,
            )
        else:
            new_balance = current - amount
            set_balance(user_id, new_balance)
            await interaction.response.send_message(
                f"Spend **{amount}** coins. New balance is **{new_balance}** coins.",
                ephemeral=True,
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Players(bot))