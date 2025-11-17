import discord
import dotenv
import os
import discord
import asyncio
from discord.ext import commands

from db import init_db

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()

class DMBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!", # This is not used but required
            intents=intents,
        )

    async def setup_hook(self):
        init_db()
        await self.load_extension("cogs.dm")
        await self.load_extension("cogs.players")
        await self.tree.sync()
        print("Slash commands synced.")

bot = DMBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())