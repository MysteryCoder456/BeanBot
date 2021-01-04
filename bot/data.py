import asyncio
import json


class UserData:
    filename = "bot/user_data.json"
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
    def create_new_data(cls):
        data_entry = {
            "wallet": 100,
            "bank": 0
        }
        return data_entry
