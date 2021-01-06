import sqlite3


class UserData:
    filename = "bot/data/data.db"
    conn = sqlite3.connect(filename)
    c = conn.cursor()

    @classmethod
    def create_tables(cls):
        cls.c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, wallet INTEGER, bank INTEGER, bank_capacity INTEGER, job_id INTEGER, job_streak INTEGER, worked_today BOOL)")
        cls.conn.commit()

    @classmethod
    def create_new_data(cls, user):
        cls.c.execute("INSERT INTO users VALUES (:user_id, 100, 0, 500, 0, 0, 0)", {"user_id": user.id})
        cls.conn.commit()
        print(f"Created data entry for {user}")

    @classmethod
    def check_user_entry(cls, user):
        cls.c.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": user.id})
        user_data = cls.c.fetchone()

        if user_data is None:
            cls.create_new_data(user)
