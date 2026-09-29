"""Independent TCP party process."""

from __future__ import annotations

import argparse
import json
import socketserver
from typing import Any

from .protocol import mod


class PartyState:
    def __init__(self) -> None:
        self.query: list[int] = []
        self.template: list[int] = []

    def handle(self, message: dict[str, Any]) -> dict[str, Any]:
        operation = message["op"]
        if operation == "load":
            self.query = [mod(value) for value in message["query"]]
            self.template = [mod(value) for value in message["template"]]
            return {"status": "ready"}
        if operation == "mask":
            return {"d": mod(message["value"] - message["a"]), "e": mod(message["value"] - message["b"])}
        if operation == "multiply":
            share = mod(message["c"] + message["d"] * message["b"] + message["e"] * message["a"] + message["correction"])
            return {"share": share}
        if operation == "reset":
            self.query = []
            self.template = []
            return {"status": "reset"}
        raise ValueError(f"unknown operation: {operation}")


class RequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        line = self.rfile.readline()
        if not line:
            return
        try:
            response = self.server.state.handle(json.loads(line))
        except Exception as error:
            response = {"error": str(error)}
        self.wfile.write((json.dumps(response, separators=(",", ":")) + "\n").encode())


class PartyServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], state: PartyState):
        super().__init__(address, RequestHandler)
        self.state = state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--party-id", type=int, required=True, choices=(0, 1, 2))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    server = PartyServer((args.host, args.port), PartyState())
    print(f"party {args.party_id} listening on {args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()