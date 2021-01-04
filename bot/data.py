import asyncio
import json


class UserData:
    filename = "bot/data/user_data.json"
    with open(filename, "r") as data_file:
        user_data = json.load(data_file)

    @classmethod
    async def auto_update_data(cls):
        while True:
            # erase file and dump data
            with open(cls.filename, "w") as data_file:
                json.dump(cls.user_data, data_file)

            await asyncio.sleep(10)

    @classmethod
    def create_new_data(cls, user):
        data_entry = {
            "wallet": 100,
            "bank": 0,
            "job_id": None,
            "job_streak": 0
        }
        cls.user_data[str(user.id)] = data_entry
        print(f"Created data entry for {user}")

    @classmethod
    def set_data(cls, user, key, value):
        cls.user_data[str(user.id)][key] = value

    @classmethod
    def get_data(cls, user, key):
        return cls.user_data[str(user.id)][key]

    @classmethod
    def add_data(cls, user, key, amount):
        if isinstance(cls.user_data[str(user.id)][key], int):
            cls.user_data[str(user.id)][key] += amount
