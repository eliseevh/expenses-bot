import json

import requests

import private_constants


def send_request(method: str, typename: str, return_name: str, obj: dict) -> dict:
    body = {"query": f"mutation {method}($input: {typename})"
                     + "{" + f"{method}(input: $input)" + "{" + return_name + "}}",
            "variables": {"input": obj}
            }
    print("[SEND_REQUEST] Sending json:", body)
    return requests.post(private_constants.API_BASE_URL + method, json=body).json()


class User:
    def __init__(self, user_id: int, user_name: str, debit: int):
        self.id = user_id
        self.name = user_name
        self.debit = debit

    def to_json_str(self) -> str:
        return json.dumps(self.to_json())

    def to_json(self) -> dict:
        return {"id": str(self.id),
                "name": self.name,
                "debit": self.debit,
                }


class Room:
    def __init__(self,
                 room_name: str,
                 room_password: str,
                 owner_id: int,
                 owner_name: str,
                 owner_debit: int,
                 ):
        self.name = room_name
        self.password = room_password
        self.members = [User(owner_id, owner_name, owner_debit)]

    def to_json(self) -> dict:
        return {"roomName": self.name,
                "roomPassword": self.password,
                "members": list(map(User.to_json, self.members)),
                }

    def to_json_str(self) -> str:
        return json.dumps(self.to_json())


def create_room(
        room_name: str,
        room_password: str,
        owner_id: int,
        owner_name: str,
        owner_debit: int = 0,
) -> dict:
    room_json = Room(room_name, room_password, owner_id, owner_name, owner_debit).to_json()
    try:
        response = send_request("createRoom", "RoomInput!", "roomId", room_json)
        print(f"[API] Sent request({room_json}). \n[API] Response: {response}")
    except Exception as e:
        response = {"status": {"ok": False, "errorValue": e}}

    return response
