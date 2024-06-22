import abc
import requests
import asyncio
import websockets
import json


class SignalBotError(Exception):
    pass


class Native:

    def __init__(self, base_url) -> None:
        self.base_url = base_url

    def _requests_wrap(codes=[200]):
        def decorator(func):
            def _wrapper(self, url, *args, **kwargs):
                endpoint_url = f"http://{self.base_url}/{url}"
                resp = func(self, endpoint_url, *args, **kwargs)
                if resp.status_code not in codes:
                    json_resp = resp.json()
                    if "error" in json_resp:
                        raise SignalBotError(json_resp["error"])
                    raise SignalBotError("Unknown Signal error while GET")
                return resp

            return _wrapper

        return decorator

    @_requests_wrap()
    def get(self, url, *args, **kwargs):
        return requests.get(url, *args, **kwargs)

    @_requests_wrap(codes=[200, 201])
    def post(self, url, *args, **kwargs):
        return requests.post(url, *args, **kwargs)

    @_requests_wrap()
    def put(self, url, *args, **kwargs):
        return requests.put(url, *args, **kwargs)

    @_requests_wrap()
    def delete(self, url, *args, **kwargs):
        return requests.delete(url, *args, **kwargs)


class JsonRPC(Native):

    async def fetch(self, number, handlers):
        self.connection = websockets.connect(
            f"ws://{self.base_url}/v1/receive/{number}", ping_interval=None
        )
        async with self.connection as websocket:
            async for raw_message in websocket:
                message = json.loads(raw_message)
                for h in handlers:
                    if asyncio.iscoroutinefunction(h):
                        await h(message)
                    else:
                        h(message)
