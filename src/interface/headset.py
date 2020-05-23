import logging
import json
import asyncio
from enum import Enum

from websockets import connect

from src.music.note import Pitch
from src.music.score import Pieces

class HeadsetClient:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.URL = f'ws://{self.host}:{self.port}'
        self.ws = None
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.__async__connect())

    def send(self, cmd):
        return self.loop.run_until_complete(self.__async__send(cmd))

    def receive(self):
        return self.loop.run_until_complete(self.__async__receive())

    async def __async__connect(self):
        logging.info(f"Connecting to {self.URL}")
        self.ws = await connect(self.URL)
        logging.info("Connected")

    async def __async__send(self, cmd):
        await self.ws.send(json.dumps(cmd))
        return await self.ws.recv()

    async def __async__receive(self):
        message = await self.ws.recv()
        print("Received: ", message)

class MessageBuilder:

    @staticmethod
    def build_accompaniment_message(notes):
        payload = {
            "type": MessageType.Accompaniment.value,
            "data": {part: notes[part].pitch if notes[part].pitch != Pitch.REST else -1 for part in range(len(notes))}
        }
        return payload

    @staticmethod
    def parse_message(message):

        json_msg = json.loads(message)
        if json_msg["type"] == MessageType.ChoosePiece:
             if json_msg["data"]["name"] == Pieces.Pachabels:
                 return Pieces.Pachabels

class MessageType(Enum):
    ChoosePiece = "song_selection",
    Start = "start"
    Accompaniment = "accompaniment"



