from . import RequestHandler


class StatusHandler(RequestHandler):
    async def get(self):
        self.write({
            "total": await self.torrents.count(),
        })
