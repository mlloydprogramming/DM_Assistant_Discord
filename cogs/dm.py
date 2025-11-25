import discord
from discord import app_commands
from discord.ext import commands

from db import set_balance, add_balance, set_party_xp_spent, set_party_level

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
        new_balance = amount
        set_balance(member.id, new_balance)
        await interaction.response.send_message(
            f"Set {member.display_name}'s balance to **{new_balance}** coins.",
            ephemeral=True
        )

    @app_commands.command(name="add_balance", description="Add an amount to player's balance")
    @app_commands.check(is_dm)
    @app_commands.guild_only()
    async def add_balance(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        add_balance(member.id, amount)
        await interaction.response.send_message(
            f"Added **{amount}** coins to {member.display_name}'s balance.",
            ephemeral=True,
        )

    @app_commands.command(name="set_party_xp_spent", description="Set the party's total XP spent to a specific amount")
    @app_commands.check(is_dm)
    @app_commands.guild_only()
    async def set_party_xp_spent(self, interaction: discord.Interaction, amount: int, role: discord.Role):
        role_id = role.id
        set_party_xp_spent(amount, role_id)
        await interaction.response.send_message(
            f"Set the party **{role.name}** total XP spent to **{amount}** XP.",
            ephemeral=True,
        )

    @app_commands.command(name="set_party_level", description="Set the party's current level")
    @app_commands.check(is_dm)
    @app_commands.guild_only()
    async def set_party_level(self, interaction: discord.Interaction, level: int, role: discord.Role):
        role_id = role.id
        set_party_level(level, role_id)
        await interaction.response.send_message(
            f"Set the party **{role.name}** level to **{level}**.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(DM(bot))
