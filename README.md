# 🎲 DM Assistant Bot

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![Discord.py](https://img.shields.io/badge/discord.py-2.3.2%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A Discord bot designed to assist Dungeon Masters in running westmarch-style, rogue-lite D&D adventures. This bot manages player economy, party experience pooling, character sheets, and provides a shop system for in-game rewards.

## ✨ Features

- 💰 **Player Economy System** - Track and manage player coin balances
- 📊 **Party XP Pooling** - Players contribute XP to shared party leveling system
- 🛒 **Shop System** - Purchase buffs and bonuses using earned XP
- 📄 **Character Sheet Management** - Store and retrieve character sheet URLs
- 🎲 **DM Controls** - Administrative commands for game management
- 🔒 **Role-Based Permissions** - Separate commands for DMs and players

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.13 or higher** installed (not required for Docker deployment)
- **[uv](https://github.com/astral-sh/uv)** package manager (not required for Docker deployment)
- **Docker and Docker Compose** (optional, for containerized deployment)
- A **Discord account** with permissions to create applications
- A **Discord server** where you have administrative rights

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dm_assistant_bot.git
   cd dm_assistant_bot
   ```

2. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

## 🤖 Discord Bot Setup

### 1. Create a Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** and give it a name
3. Navigate to the **"Bot"** section and click **"Add Bot"**
4. Under the bot's token section, click **"Reset Token"** and copy it (you'll need this for the `.env` file)

### 2. Configure OAuth2 Scopes

In the OAuth2 section, select the following scopes:
- **User Install Scopes:**
  - `applications.commands`
- **Guild Install Scopes:**
  - `applications.commands`
  - `bot`

### 3. Set Bot Permissions

Under **Bot Permissions**, select:
- ✅ Attach Files
- ✅ Embed Links
- ✅ Read Message History
- ✅ Send Messages
- ✅ Use Slash Commands
- ✅ View Channels

### 4. Invite the Bot

Use the generated OAuth2 URL to invite the bot to your server.

## ⚙️ Configuration

1. **Create environment file**
   ```bash
   cp .env.example .env
   ```

2. **Add your bot token**
   
   Edit `.env` and replace `<your_bot_token_here>` with your actual Discord bot token:
   ```
   DISCORD_BOT_TOKEN=your_actual_token_here
   ```

3. **Create the DM role**
   
   In your Discord server, create a role named exactly **"Dungeon Master"** and assign it to users who should have DM permissions.

## 🎮 Running the Bot

### Option 1: Running Locally

Start the bot with:
```bash
uv run main.py
```

You should see output similar to:
```
Slash commands synced.
Logged in as YourBotName (ID: 123456789)
```

### Option 2: Running with Docker Compose (Recommended for Homelab)

1. **Ensure your `.env` file is configured** with your Discord bot token

2. **Start the bot**:
   ```bash
   docker-compose up -d
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f
   ```

4. **Stop the bot**:
   ```bash
   docker-compose down
   ```

The bot will automatically restart unless manually stopped. The database is persisted in the `./data` directory on your host machine.

### Option 3: Running with Docker (Manual)

1. **Build the image**:
   ```bash
   docker build -t dm-assistant-bot .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name dm-assistant-bot \
     --restart unless-stopped \
     -e DISCORD_BOT_TOKEN=your_token_here \
     -v $(pwd)/data:/app/data \
     dm-assistant-bot
   ```

3. **View logs**:
   ```bash
   docker logs -f dm-assistant-bot
   ```

## 📖 Commands

### DM Commands

These commands require the **"Dungeon Master"** role:

| Command | Description | Usage |
|---------|-------------|-------|
| `/dm_test` | Test DM command functionality | `/dm_test` |
| `/set_balance` | Set a player's balance to a specific amount | `/set_balance @player 1` |
| `/add_balance` | Add XP to a player's balance | `/add_balance @player 50` |
| `/set_party_xp_spent` | Set the party's total XP spent | `/set_party_xp_spent 1 @PartyRole` |
| `/set_party_level` | Manually set the party's level | `/set_party_level 5 @PartyRole` |
| `/set_player_equipment_level` | Manually set the players equipment level | `/set_player_equipment_level @player 1` |
| `/set_player_weapon_level` | Manually set the players weapon level | `/set_player_equipment_level @player 1` |
| `/set_player_armor_level` | Manually set the players armor level | `/set_player_armor_level @player 1` |

### Player Commands

Available to all players:

| Command | Description | Usage |
|---------|-------------|-------|
| `/players_test` | Test player command functionality | `/players_test` |
| `/get_balance` | Check your current coin balance | `/get_balance` |
| `/spend_balance` | Spend XP from your balance | `/spend_balance 20` |
| `/shop` | View all available shop items | `/shop` |
| `/buy` | Purchase an item from the shop | `/buy bless` |
| `/add_party_xp_spent` | Contribute XP to party leveling | `/add_party_xp_spent 100 @PartyRole` |
| `/get_party_xp_spent` | View party XP progress | `/get_party_xp_spent` |
| `/get_party_level` | Check current party level | `/get_party_level @PartyRole` |
| `/set_character_sheet` | Save your character sheet URL | `/set_character_sheet https://...` |
| `/get_character_sheet` | Retrieve your character sheet URL | `/get_character_sheet` |
| `/get_character_progression` | Retrieve character progression data | `/get_character_progression` |
| `/add_weapon_xp` | Contribute XP to personal weapon progression | `/add_weapon_xp 5` |
| `/add_armor_xp` | Contribute XP to personal armor progression | `/add_armor_xp 5` |
| `/add_equipment_xp` | Contribute XP to personal equipment progression | `/add_equipment_xp 5` |

### Shop Items

| Item | Cost | Description |
|------|------|-------------|
| **Bless** | 1 XP | Gain an extra d4 to add to the next three attack rolls or saving throws |
| **Reroll** | 20 XP | Purchase a token to reroll a failed roll (requires DM approval) |
| **Contracts** | 2, 3, 5, or 8 XP | Purchase a contract for your next adventure |
| **Lucky** | 3 | Gain the lucky feat for the next adventure |

## 🗄️ Database Structure

The bot uses SQLite to store persistent data:

### `players` Table
- `discord_id` - Unique player identifier
- `balance` - Player's current coin balance
- `character_sheet` - URL to player's character sheet
- `armor_level` - Current player armor level
- `armor_xp_spent` - Total XP contributed to armor progression
- `weapon_level` - Current player weapon level
- `weapon_xp_spent` - Total XP contributed to weapon progression
- `equipment_level` - Current player equipment level
- `equipment_xp_spent` - Total XP contributed to weapon progression

### `party_state` Table
- `role_id` - Discord role ID representing the party
- `xp_spent` - Total XP contributed by the party
- `party_level` - Current party level

The database file is automatically created at `data/bot.db` when the bot first runs.

## 📁 Project Structure

```
dm_assistant_bot/
├── main.py              # Bot initialization and startup
├── db.py                # Database operations and queries
├── constants.py         # Game constants (level requirements, shop items)
├── cogs/
│   ├── dm.py           # DM-only commands
│   └── players.py      # Player commands
├── data/               # SQLite database directory (auto-created)
├── Dockerfile          # Docker container definition
├── docker-compose.yml  # Docker Compose configuration
├── .dockerignore       # Files to exclude from Docker build
├── .env                # Environment variables (not in repo)
├── .env.example        # Example environment file
├── pyproject.toml      # Project dependencies
└── README.md           # This file
```

## 🔧 Troubleshooting

### Bot not responding to commands
- Verify the bot token in `.env` is correct
- Check that slash commands were synced (look for "Slash commands synced" in console)
- Ensure the bot has proper permissions in your Discord server
- Try kicking and re-inviting the bot

### "You don't have permission" errors
- Verify you have the "Dungeon Master" role (exact name required)
- Check that the role is assigned properly in Discord server settings

### Database errors
- Ensure the bot has write permissions in the project directory
- Check that `data/` directory was created successfully
- Delete `data/bot.db` to reset the database (⚠️ this will erase all data)

### Commands not showing up
- Wait a few minutes for Discord to update slash commands globally
- Try using the commands in a different channel
- Use `/` in Discord to see if commands appear in the autocomplete

### Docker-specific issues
- **Container won't start**: Check logs with `docker-compose logs` or `docker logs dm-assistant-bot`
- **Database not persisting**: Ensure the `./data` volume mount is correct
- **Permission errors**: On Linux, you may need to adjust ownership: `sudo chown -R $USER:$USER data/`

## 📄 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🎯 Future Enhancements

Potential features for future development:
- Quest tracking system
- Inventory management
- Combat encounter tracker
- Session scheduling
- Loot distribution system

---

Made with ❤️ for tabletop gaming communities
