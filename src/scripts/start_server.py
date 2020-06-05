import argparse
import asyncio
import logging
import sys

import websockets

sys.path.append("../../")

from src.interface.server import Server
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Websockets Server')
    parser.add_argument('local_ip', metavar='local_ip', type=str, help='Local IP address for server to start')
    parser.add_argument('port', metavar='port', type=int, help='Port server')
    args = parser.parse_args()

    logging.info("Starting Server....")
    server = Server()
    start_server = websockets.serve(server.ws_handler, args.local_ip, args.port)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    logging.info("Started")
    loop.run_forever()
