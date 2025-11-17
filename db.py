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