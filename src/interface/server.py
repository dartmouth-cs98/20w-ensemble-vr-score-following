import asyncio
import logging
import sys
import time

from websockets import WebSocketServerProtocol

sys.path.append("../../")

logging.basicConfig(level=logging.INFO)


# Code adapted from https://medium.com/better-programming/how-to-create-a-websocket-in-python-b68d65dbd549
class Server:
    clients = set()

    async def register(self, ws):
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects.')

    async def unregister(self, ws):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message):
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    async def ws_handler(self, ws, url):
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol):
        print("Distributing Messages")
        async for message in ws:
            print(message, ws.remote_address, time.time())
            await self.send_to_clients(message)
