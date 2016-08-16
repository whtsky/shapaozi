# -*- coding: utf-8 -*-

from . import RequestHandler
from .utils import infohash_to_dict

from tornado.web import HTTPError
from tornado.escape import json_encode


class DetailHandler(RequestHandler):
    async def get(self, infohash):
        data = await self.torrents.find_one({"infohash": infohash.upper()})
        if not data:
            raise HTTPError(404)
        self.write(json_encode(infohash_to_dict(data)))


class RandomHandler(RequestHandler):
    async def get(self):
        datas = []
        try:
            size = max(int(self.get_argument("size", "1")), 1)
        except:
            size = 1
        size = min(size, 20)
        async for data in self.torrents.aggregate([{
            "$sample": {
                "size": size
            }
        }]):
            datas.append(infohash_to_dict(data))
        self.write(json_encode({
            "size": size,
            "data": datas
        }))
