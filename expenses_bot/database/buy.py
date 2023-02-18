from expenses_bot.database.base_storage import BaseStorage


class BuyStorage(BaseStorage):
    def __init__(self, db_name: str) -> None:
        super().__init__(db_name)
        self.connection.cursor().execute("CREATE TABLE IF NOT EXISTS buy("
                                         "user_id INTEGER NOT NULL PRIMARY KEY,"
                                         "room_id TEXT DEFAULT NULL,"
                                         "name TEXT DEFAULT NULL,"
                                         "cost INTEGER DEFAULT NULL)")
        self.connection.cursor().execute("CREATE TABLE IF NOT EXISTS buy_members("
                                         "user_id INTEGER NOT NULL,"
                                         "member_id INTEGER NOT NULL,"
                                         "FOREIGN KEY (user_id) REFERENCES buy(user_id))")
        self.connection.commit()

    def add_user(self, user_id: int) -> None:
        self.connection.cursor().execute("INSERT INTO buy VALUES (?, NULL, NULL, NULL)", (user_id,))
        self.connection.commit()

    def set_room_id(self, user_id: int, room_id: str) -> None:
        self.connection.cursor().execute("UPDATE buy SET room_id=? WHERE user_id=?", (room_id, user_id))
        self.connection.commit()

    def add_member(self, user_id: int, member_id: int) -> None:
        self.connection.cursor().execute("INSERT INTO buy_members VALUES (?, ?)", (user_id, member_id))
        self.connection.commit()

    def set_name(self, user_id: int, name: str) -> None:
        self.connection.cursor().execute("UPDATE buy SET name=? WHERE user_id=?", (name, user_id))
        self.connection.commit()

    def set_cost(self, user_id: int, cost: int) -> None:
        self.connection.cursor().execute("UPDATE buy SET cost=? WHERE user_id=?", (cost, user_id))
        self.connection.commit()

    def get(self, user_id: int) -> (str, [int], str, int):
        members = self.connection.cursor().execute("SELECT member_id FROM buy_members WHERE user_id=?",
                                                   (user_id,)).fetchall()
        members = list(map(lambda result: result[0], members))
        rest_fields = self.connection.cursor().execute("SELECT room_id, name, cost FROM buy WHERE user_id=?",
                                                       (user_id,)).fetchone()
        return rest_fields[0], members, rest_fields[1], rest_fields[2]

    def delete(self, user_id: int) -> None:
        self.connection.cursor().execute("DELETE FROM buy_members WHERE user_id=?", (user_id,))
        self.connection.cursor().execute("DELETE FROM buy WHERE user_id=?", (user_id,))
        self.connection.commit()
