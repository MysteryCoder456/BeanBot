import os
import sqlite3


class Data:
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    filename = os.path.join(data_dir, "data.db")
    conn = sqlite3.connect(filename)
    c = conn.cursor()

    @classmethod
    def create_tables(cls):
        cls.c.execute("""CREATE TABLE IF NOT EXISTS "users" (
            "id"	INTEGER,
            "wallet"	INTEGER DEFAULT 0,
            "bank"	INTEGER DEFAULT 0,
            "bank_capacity"	INTEGER DEFAULT 500,
            "job_id"	INTEGER DEFAULT 0,
            "job_streak"	INTEGER DEFAULT 0,
            "last_work_date"	TEXT DEFAULT '2020-1-1 12:00',
            "inventory"	TEXT DEFAULT '[]',
            "powerups"	TEXT DEFAULT '{}'
        )""")

        cls.c.execute("""CREATE TABLE IF NOT EXISTS "guilds" (
            "id"	INTEGER,
            "tracked_words"	TEXT DEFAULT '{}'
        )""")

        cls.conn.commit()

    # User Data
    @classmethod
    def create_new_user_data(cls, user):
        cls.c.execute("INSERT INTO users VALUES (:user_id, 0, 0, 500, 0, 0, '2020-1-1 12:00', '[]', '{}')", {"user_id": user.id})
        cls.conn.commit()
        print(f"Created data entry for user {user}")

    @classmethod
    def check_user_entry(cls, user):
        cls.c.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": user.id})
        user_data = cls.c.fetchone()

        if user_data is None:
            cls.create_new_user_data(user)

    # Guild Data
    @classmethod
    def create_new_guild_data(cls, guild):
        cls.c.execute("INSERT INTO guilds VALUES (:guild_id, '{}')", {"guild_id": guild.id})
        cls.conn.commit()
        print(f"Created data entry for guild {guild.name}")

    @classmethod
    def check_guild_entry(cls, guild):
        cls.c.execute("SELECT * FROM guilds WHERE id = :guild_id", {"guild_id": guild.id})
        guild_data = cls.c.fetchone()

        if guild_data is None:
            cls.create_new_guild_data(guild)
