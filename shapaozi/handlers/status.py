from tornado.escape import json_encode

from . import RequestHandler


class StatusHandler(RequestHandler):
    async def get(self):
        self.write(json_encode({
            "total": await self.torrents.count(),
        }))
