# -*- coding: utf-8 -*-

from . import RequestHandler
from .utils import infohash_to_dict
from utils import add_infohash

from tornado.web import HTTPError
from tornado.escape import json_encode


class DetailHandler(RequestHandler):
    async def get(self, infohash):
        data = await self.torrents.find_one({"infohash": infohash.upper()})
        if not data:
            if not await add_infohash(infohash):
                raise HTTPError(404)
            data = await self.torrents.find_one({"infohash": infohash.upper()})
        self.write(json_encode(infohash_to_dict(data)))
