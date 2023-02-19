from expenses_bot.database.base_storage import BaseStorage


class UserStateStorage(BaseStorage):
    def __init__(self, db_name: str) -> None:
        super().__init__(db_name)
        self.connection.cursor().execute("CREATE TABLE IF NOT EXISTS user_state ("
                                         "user_id INTEGER NOT NULL PRIMARY KEY,"
                                         "state INTEGER NOT NULL)")
        self.connection.commit()

    def get_state(self, user_id: int) -> int:
        result = self.connection \
            .cursor() \
            .execute("SELECT state FROM user_state WHERE user_id=?", (user_id,)) \
            .fetchone()
        if result is None:
            return -1
        return result[0]

    def set_state(self, user_id: int, new_state: int) -> None:
        self.connection.cursor().execute("DELETE FROM user_state WHERE user_id=?", (user_id,))
        if new_state != -1:
            self.connection.cursor().execute("INSERT INTO user_state VALUES (?, ?)", (user_id, new_state))
        self.connection.commit()

    def close(self):
        self.connection.close()
        del self.connection
        del self
