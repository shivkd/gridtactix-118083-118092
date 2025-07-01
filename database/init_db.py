#!/usr/bin/env python3
"""Initialize SQLite database for tactical duel game (games, players, units)."""

import sqlite3
import os

DB_NAME = "myapp.db"

print("Starting SQLite tactical duel game schema setup...")

def create_schema(cursor):
    # The games table stores each game, its state, and turn info.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'waiting', -- waiting, active, finished
            current_turn_player_id INTEGER,
            winner_player_id INTEGER,
            board_width INTEGER NOT NULL DEFAULT 6,
            board_height INTEGER NOT NULL DEFAULT 6,
            FOREIGN KEY (current_turn_player_id) REFERENCES players(id),
            FOREIGN KEY (winner_player_id) REFERENCES players(id)
        )
    """)

    # The players table stores user/player data per game.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            display_name TEXT,
            is_human INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            -- Could add avatar, color, etc.
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        )
    """)

    # The units table stores unit positions and stats for each unit in every game. Owner by player.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL, -- owner
            unit_type TEXT NOT NULL,
            pos_x INTEGER NOT NULL,
            pos_y INTEGER NOT NULL,
            hp INTEGER NOT NULL,
            max_hp INTEGER NOT NULL,
            attack INTEGER NOT NULL,
            defense INTEGER NOT NULL,
            move_range INTEGER NOT NULL,
            attack_range INTEGER NOT NULL,
            has_acted INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
        )
    """)

    # Indexes for performance on foreign keys and game state lookup
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_game_id ON players(game_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_units_game_id ON units(game_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_units_player_id ON units(player_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_units_pos ON units(game_id, pos_x, pos_y)")

def insert_initial_data(cursor):
    # Example: Optionally, insert a sample game with two players and a few units.
    pass  # No default data for production, intended for test/development only.

# Main execution
db_exists = os.path.exists(DB_NAME)
if db_exists:
    print(f"SQLite database already exists at {DB_NAME}")
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("SELECT 1")
        conn.close()
        print("Database is accessible and working.")
    except Exception as e:
        print(f"Warning: Database exists but may be corrupted: {e}")
else:
    print("Creating new SQLite database...")

# Always connect and ensure schema (idempotent)
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")
create_schema(cursor)
insert_initial_data(cursor)
conn.commit()

# Save connection info for backend integration (and for the db_visualizer tool)
current_dir = os.getcwd()
connection_string = f"sqlite:///{current_dir}/{DB_NAME}"

with open("db_connection.txt", "w") as f:
    f.write(f"# SQLite connection methods:\n")
    f.write(f"# Python: sqlite3.connect('{DB_NAME}')\n")
    f.write(f"# Connection string: {connection_string}\n")
    f.write(f"# File path: {current_dir}/{DB_NAME}\n")

# Update environment file for Node.js db visualizer as well
db_path = os.path.abspath(DB_NAME)
if not os.path.exists("db_visualizer"):
    os.makedirs("db_visualizer", exist_ok=True)
with open("db_visualizer/sqlite.env", "w") as f:
    f.write(f"export SQLITE_DB=\"{db_path}\"\n")

# Report schema
print("\nSQLite tactical duel game DB schema initialized!")
print("Tables created: games, players, units")
print(f"Database: {DB_NAME}")
print(f"Location: {current_dir}/{DB_NAME}")

print("\nTo use with Node.js viewer, run: source db_visualizer/sqlite.env")
print("\nTo connect to the database, use one of the following methods:")
print(f"1. Python: sqlite3.connect('{DB_NAME}')")
print(f"2. Connection string: {connection_string}")
print(f"3. Direct file access: {current_dir}/{DB_NAME}")

print("\nTo inspect schema, launch:")
print(f"  python3 db_shell.py")
print("\nScript completed successfully.")
