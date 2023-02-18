from expenses_bot.database.base_storage import BaseStorage


class CreateRoomStorage(BaseStorage):
    def __init__(self, db_name: str) -> None:
        super().__init__(db_name)
        self.connection.cursor().execute("CREATE TABLE IF NOT EXISTS create_room ("
                                         "user_id INTEGER NOT NULL PRIMARY KEY,"
                                         "room_name TEXT DEFAULT NULL,"
                                         "room_password TEXT DEFAULT NULL,"
                                         "user_name TEXT DEFAULT NULL)")
        self.connection.commit()

    def add_user(self, user_id: int) -> None:
        self.connection.cursor().execute("INSERT INTO create_room VALUES (?, NULL, NULL, NULL)", (user_id,))
        self.connection.commit()

    def set_room_name(self, user_id: int, room_name: str) -> None:
        self.connection.cursor().execute("UPDATE create_room SET room_name=? WHERE user_id=?", (room_name, user_id))
        self.connection.commit()

    def set_room_password(self, user_id: int, room_password: str) -> None:
        self.connection.cursor().execute("UPDATE create_room SET room_password=? WHERE user_id=?",
                                         (room_password, user_id))
        self.connection.commit()

    def set_user_name(self, user_id: int, user_name: str) -> None:
        self.connection.cursor().execute("UPDATE create_room SET user_name=? WHERE user_id=?", (user_name, user_id))
        self.connection.commit()

    def get(self, user_id: int) -> (str, str, str):
        return self.connection.cursor().execute(
            "SELECT room_name, room_password, user_name FROM create_room WHERE user_id=?", (user_id,)).fetchone()

    def delete(self, user_id: int) -> None:
        self.connection.cursor().execute("DELETE FROM create_room WHERE user_id=?", (user_id,))
        self.connection.commit()
