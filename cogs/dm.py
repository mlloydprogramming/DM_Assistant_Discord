import discord
from discord import app_commands
from discord.ext import commands

from db import get_balance, set_balance

DM_ROLE_NAME = "Dungeon Master"


def is_dm(interaction: discord.Interaction) -> bool:
    """Return True if the invoking user has the DM role."""
    if interaction.guild is None:
        return False  # just in case

    member = interaction.user
    # interaction.user is a Member in guild commands
    return any(role.name == DM_ROLE_NAME for role in getattr(member, "roles", []))


class DM(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="dm_test",
        description="Test DM assistant command",
    )
    @app_commands.check(is_dm)
    @app_commands.guild_only()
    async def dm_test(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "DM test command is working (and you have the DM role).",
            ephemeral=True,
        )

    @app_commands.command(name="set_balance", description="Set your balance to a specific amount")
    @app_commands.check(is_dm)
    @app_commands.guild_only()
    async def set_balance(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        current = get_balance(member.id)
        new_balance = current + amount
        set_balance(member.id, new_balance)
        await interaction.response.send_message(
            f"Added {amount} to {member.display_name}'s balance. New total is **{new_balance}** coins.",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(DM(bot))
