import sqlite3
from pathlib import Path

DB_PATH = Path("data/bot.db")

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id INTEGER UNIQUE NOT NULL,
            balance INTEGER NOT NULL DEFAULT 0,
            character_sheet TEXT,
            armor_level INTEGER NOT NULL DEFAULT 1,
            armor_xp_spent INTEGER NOT NULL DEFAULT 0,
            weapon_level INTEGER NOT NULL DEFAULT 1,
            weapon_xp_spent INTEGER NOT NULL DEFAULT 0,
            equipment_level INTEGER NOT NULL DEFAULT 1,
            equipment_xp_spent INTEGER NOT NULL DEFAULT 0
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS party_state (
            role_id INTEGER PRIMARY KEY,
            xp_spent INTEGER NOT NULL DEFAULT 0,
            party_level INTEGER NOT NULL DEFAULT 1
        );
        """
    )

    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_balance(discord_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT balance FROM players WHERE discord_id = ?",
        (discord_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 0
    return row[0]

def spend_balance(discord_id: int, amount: int):
    if amount < 0:
        raise ValueError("Amount to spend must be non-negative")
    current_balance = get_balance(discord_id)
    if amount > current_balance:
        raise ValueError("Insufficient balance to spend the requested amount")
    new_balance = current_balance - amount
    set_balance(discord_id, new_balance)

def set_balance(discord_id: int, balance: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO players (discord_id, balance)
        VALUES (?, ?)
        ON CONFLICT(discord_id) DO UPDATE SET balance=excluded.balance;
        """,
        (discord_id, balance),
    )
    conn.commit()
    conn.close()

def add_balance(discord_id: int, amount: int):
    if amount < 0:
        raise ValueError("Amount to add must be non-negative")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO players (discord_id, balance)
        VALUES (?, ?)
        ON CONFLICT(discord_id) DO UPDATE SET balance=players.balance + excluded.balance;
        """,
        (discord_id, amount),
    )
    conn.commit()
    conn.close()

def set_party_xp_spent(amount: int, role_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE party_state SET xp_spent = ? WHERE role_id = ?;",
        (amount, role_id),
    )
    conn.commit()
    conn.close()

def get_party_xp_spent(role_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT xp_spent FROM party_state WHERE role_id = ?;", (role_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 0
    return row[0]

def add_party_xp_spent(amount: int, role_id: int):
    if amount < 0:
        raise ValueError("Amount to add must be non-negative")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE party_state SET xp_spent = xp_spent + ? WHERE role_id = ?;",
        (amount, role_id),
    )
    conn.commit()
    conn.close()

def set_party_level(level: int, role_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO party_state (role_id, xp_spent, party_level)
        VALUES (?, 0, ?)
        ON CONFLICT(role_id) DO UPDATE
        SET party_level = excluded.party_level;
        """,
        (role_id, level),
    )
    conn.commit()
    conn.close()

def get_party_level(role_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT party_level FROM party_state WHERE role_id = ?;", (role_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 1
    return row[0]

def set_character_sheet(discord_id: int, url: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO players (discord_id, balance, character_sheet)
        VALUES (?, 0, ?)
        ON CONFLICT(discord_id) DO UPDATE
        SET character_sheet = excluded.character_sheet;
        """,
        (discord_id, url),
    )
    conn.commit()
    conn.close()

def get_character_sheet(discord_id: int) -> str | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT character_sheet FROM players WHERE discord_id = ?;",
        (discord_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    return row[0]

def set_armor_level(discord_id: int, level: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO players (discord_id, balance, armor_level)
        VALUES (?, 0, ?)
        ON CONFLICT(discord_id) DO UPDATE
        SET armor_level = excluded.armor_level;
        """,
        (discord_id, level),
    )
    conn.commit()
    conn.close()

def get_armor_level(discord_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT armor_level FROM players WHERE discord_id = ?;",
        (discord_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 1
    return row[0]

def add_armor_xp_spent(discord_id: int, amount: int):
    if amount < 0:
        raise ValueError("Amount to add must be non-negative")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO players (discord_id, armor_xp_spent)
        VALUES (?, ?)
        ON CONFLICT(discord_id) DO UPDATE
        SET armor_xp_spent = players.armor_xp_spent + excluded.armor_xp_spent;
        """,
        (discord_id, amount),
    )
    conn.commit()
    conn.close()

def get_armor_xp_spent(discord_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT armor_xp_spent FROM players WHERE discord_id = ?;",
        (discord_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 0
    return row[0]

def set_weapon_level(discord_id: int, level: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO players (discord_id, balance, weapon_level)
        VALUES (?, 0, ?)
        ON CONFLICT(discord_id) DO UPDATE
        SET weapon_level = excluded.weapon_level;
        """,
        (discord_id, level),
    )
    conn.commit()
    conn.close()

def get_weapon_level(discord_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT weapon_level FROM players WHERE discord_id = ?;",
        (discord_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 1
    return row[0]

def add_weapon_xp_spent(discord_id: int, amount: int):
    if amount < 0:
        raise ValueError("Amount to add must be non-negative")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO players (discord_id, weapon_xp_spent)
        VALUES (?, ?)
        ON CONFLICT(discord_id) DO UPDATE
        SET weapon_xp_spent = players.weapon_xp_spent + excluded.weapon_xp_spent;
        """,
        (discord_id, amount),
    )
    conn.commit()
    conn.close()

def get_weapon_xp_spent(discord_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT weapon_xp_spent FROM players WHERE discord_id = ?;",
        (discord_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 0
    return row[0]

def set_equipment_level(discord_id: int, level: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO players (discord_id, balance, equipment_level)
        VALUES (?, 0, ?)
        ON CONFLICT(discord_id) DO UPDATE
        SET equipment_level = excluded.equipment_level;
        """,
        (discord_id, level),
    )
    conn.commit()
    conn.close()

def get_equipment_level(discord_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT equipment_level FROM players WHERE discord_id = ?;",
        (discord_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 1
    return row[0]

def add_equipment_xp_spent(discord_id: int, amount: int):
    if amount < 0:
        raise ValueError("Amount to add must be non-negative")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO players (discord_id, equipment_xp_spent)
        VALUES (?, ?)
        ON CONFLICT(discord_id) DO UPDATE
        SET equipment_xp_spent = players.equipment_xp_spent + excluded.equipment_xp_spent;
        """,
        (discord_id, amount),
    )
    conn.commit()
    conn.close()

def get_equipment_xp_spent(discord_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT equipment_xp_spent FROM players WHERE discord_id = ?;",
        (discord_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 0
    return row[0]  