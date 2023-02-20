import requests

import private_constants


def send_mutation_request(method: str, typename: str, return_name: str, obj: dict) -> dict:
    body = {"query": f"mutation {method}($input: {typename})"
                     + "{" + f"{method}(input: $input)" + "{" + return_name + "}}",
            "variables": {"input": obj}
            }
    print("[SEND_MUTATION_REQUEST] Sending json:", body)
    return requests.post(private_constants.API_URL, json=body).json()


def send_query_request(method: str, typename: str, arg_name: str, return_name: str, obj: dict | str) -> dict:
    body = {"query": f"query {method}($input: {typename})"
                     + "{" + f"{method}({arg_name}: $input)" + "{" + return_name + "}}",
            "variables": {"input": obj}}
    print("[SEND_QUERY_REQUEST] Sending json:", body)
    return requests.post(private_constants.API_URL, json=body).json()


class User:
    def __init__(self, user_id: str, user_name: str, debit: int) -> None:
        self.id = user_id
        self.name = user_name
        self.debit = debit

    def to_json(self) -> dict:
        return {"id": self.id,
                "name": self.name,
                "debit": self.debit,
                }


class Room:
    def __init__(self,
                 room_name: str,
                 room_password: str,
                 owner_id: str,
                 owner_name: str,
                 owner_debit: int,
                 ) -> None:
        self.name = room_name
        self.password = room_password
        self.members = [User(owner_id, owner_name, owner_debit)]

    def to_json(self) -> dict:
        return {"roomName": self.name,
                "roomPassword": self.password,
                "members": list(map(User.to_json, self.members)),
                }


class RoomSignIn:
    def __init__(self, room_id: str, room_password: str, user_id: str, user_name: str, user_debit: int) -> None:
        self.id = room_id
        self.password = room_password
        self.user = User(user_id, user_name, user_debit)

    def to_json(self) -> dict:
        return {"roomId": self.id,
                "roomPassword": self.password,
                "userInput": self.user.to_json()
                }


class RoomSignOut:
    def __init__(self, room_id: str, user_id: str) -> None:
        self.room_id = room_id
        self.user_id = user_id

    def to_json(self) -> dict:
        return {"roomId": self.room_id,
                "userId": self.user_id
                }


class Buy:
    def __init__(self, room_id: str, user_id: str, members_id: [str], cost: int) -> None:
        self.room_id = room_id
        self.user_id = user_id
        self.members_id = members_id
        self.cost = cost

    def to_json(self) -> dict:
        return {"roomId": self.room_id,
                "userSetterId": self.user_id,
                "membersId": self.members_id,
                "value": self.cost
                }


class Pay:
    def __init__(self, room_id: str, sender_id: str, receiver_id: str, value: int) -> None:
        self.room_id = room_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.value = value

    def to_json(self) -> dict:
        return {"roomId": self.room_id,
                "userSetterId": self.sender_id,
                "userGetterId": self.receiver_id,
                "value": self.value
                }


def create_room(
        room_name: str,
        room_password: str,
        owner_id: int,
        owner_name: str,
        owner_debit: int = 0,
) -> dict:
    room_json = Room(room_name, room_password, str(owner_id), owner_name, owner_debit).to_json()
    try:
        response = send_mutation_request("createRoom", "RoomInput!", "roomId", room_json)
        print(f"[CREATE_ROOM] Sent request({room_json}). \n[CREATE_ROOM] Response: {response}")
    except Exception as e:
        response = {"errors": [{"message": str(e)}]}

    return response


def sign_in_room(room_id: str, room_password: str, user_id: int, user_name: str, user_debit: int = 0) -> dict:
    sign_in_room_json = RoomSignIn(room_id, room_password, str(user_id), user_name, user_debit).to_json()
    try:
        response = send_mutation_request("roomSignIn", "RoomSignInInput!", "roomId", sign_in_room_json)
        print(f"[SIGN_IN_ROOM] Sent request({sign_in_room_json}). \n[SIGN_IN_ROOM] Response: {response}")
    except Exception as e:
        response = {"errors": [{"message": str(e)}]}

    return response


def sign_out_room(room_id: str, user_id: int) -> dict:
    sign_out_room_json = RoomSignOut(room_id, str(user_id)).to_json()
    try:
        response = send_mutation_request("roomSignOut", "RoomSignOutInput!", "roomId", sign_out_room_json)
        print(f"[SIGN_OUT_ROOM] Sent request({sign_out_room_json}). \n[SIGN_OUT_ROOM] Response: {response}")
    except Exception as e:
        response = {"errors": [{"message": str(e)}]}

    return response


def buy(room_id: str, user_id: int, members_id: [str], cost: int) -> dict:
    buy_json = Buy(room_id, str(user_id), members_id, cost).to_json()
    try:
        response = send_mutation_request("addBuy", "BuyInput!", "roomId", buy_json)
        print(f"[BUY] Sent request({buy_json}). \n[BUY] Response: {response}")
    except Exception as e:
        response = {"errors": [{"message": str(e)}]}

    return response


def pay(room_id: str, sender_id: int, receiver_id: str, value: int) -> dict:
    pay_json = Pay(room_id, str(sender_id), receiver_id, value).to_json()
    try:
        response = send_mutation_request("payMoney", "PayMoneyInput!", "roomId", pay_json)
        print(f"[PAY] Sent request({pay_json}). \n[PAY] Response: {response}")
    except Exception as e:
        response = {"errors": [{"message": str(e)}]}

    return response


def get_user_rooms(user_id: int) -> dict:
    try:
        response = send_query_request("getRooms", "ID!", "userId", "roomId, roomName, members {id, name, debit}",
                                      str(user_id))
        print(f"[GET_USER_ROOMS] Sent request({user_id}). \n[GET_USER_ROOMS] Response: {response}")
    except Exception as e:
        response = {"errors": [{"message": str(e)}]}

    return response


def get_room(room_id: str) -> dict:
    try:
        response = send_query_request("getRoom", "ID!", "roomId", "roomName, members {id, name, debit}", room_id)
        print(f"[GET_ROOM] Sent request({room_id}). \n[GET_ROOM] Response: {response}")
    except Exception as e:
        response = {"errors": [{"message": str(e)}]}

    return response
