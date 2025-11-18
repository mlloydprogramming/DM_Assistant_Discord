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
            balance INTEGER NOT NULL DEFAULT 0
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS party_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            xp_spent INTEGER NOT NULL DEFAULT 0,
            party_level INTEGER NOT NULL DEFAULT 1
        );
        """
    )

    cur.execute("INSERT OR IGNORE INTO party_state (id) VALUES (1);")
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

def set_party_xp_spent(amount: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE party_state SET xp_spent = ? WHERE id = 1;",
        (amount,),
    )
    conn.commit()
    conn.close()

def get_party_xp_spent() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT xp_spent FROM party_state WHERE id = 1;")
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 0
    return row[0]

def add_party_xp_spent(amount: int):
    if amount < 0:
        raise ValueError("Amount to add must be non-negative")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE party_state SET xp_spent = xp_spent + ? WHERE id = 1;",
        (amount,),
    )
    conn.commit()
    conn.close()

def set_party_level(level: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE party_state SET party_level = ? WHERE id = 1;",
        (level,),
    )
    conn.commit()
    conn.close()

def get_party_level() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT party_level FROM party_state WHERE id = 1;")
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 1
    return row[0]