from expenses_bot.database.base_storage import BaseStorage


class PayStorage(BaseStorage):
    def __init__(self, db_name: str) -> None:
        super().__init__(db_name)
        self.connection.cursor().execute("CREATE TABLE IF NOT EXISTS pay("
                                         "user_id INTEGER NOT NULL PRIMARY KEY,"
                                         "room_id TEXT DEFAULT NULL,"
                                         "receiver_id INTEGER DEFAULT NULL,"
                                         "receiver_name TEXT DEFAULT NULL,"
                                         "value INTEGER DEFAULT NULL)")
        self.connection.commit()

    def add_user(self, user_id: int) -> None:
        self.connection.cursor().execute("INSERT INTO pay VALUES (?, NULL, NULL, NULL, NULL)", (user_id,))
        self.connection.commit()

    def set_room_id(self, user_id: int, room_id: str) -> None:
        self.connection.cursor().execute("UPDATE pay SET room_id=? WHERE user_id=?", (room_id, user_id))
        self.connection.commit()

    def set_receiver(self, user_id: int, receiver_id: int, receiver_name: str) -> None:
        self.connection.cursor().execute("UPDATE pay SET receiver_id=?, receiver_name=? WHERE user_id=?",
                                         (receiver_id, receiver_name, user_id))
        self.connection.commit()

    def set_value(self, user_id: int, value: int) -> None:
        self.connection.cursor().execute("UPDATE pay SET value=? WHERE user_id=?", (value, user_id))
        self.connection.commit()

    def get(self, user_id: int) -> (str, (int, str), int):
        result = self.connection.cursor().execute(
            "SELECT room_id, receiver_id, receiver_name, value FROM pay WHERE user_id=?", (user_id,)).fetchone()
        return result[0], (result[1], result[2]), result[3]

    def delete(self, user_id: int) -> None:
        self.connection.cursor().execute("DELETE FROM pay WHERE user_id=?", (user_id,))
        self.connection.commit()
