# -*- coding: utf-8 -*-

import asyncio
import logging
import time

from utils import add_infohash, torrents_async
from maga import Maga


class SPZCrawler(Maga):
    async def handler(self, infohash):
        logging.info("See infohash: " + infohash)
        doc = await torrents_async.find_and_modify(
            {"infohash": infohash},
            update={
                "$set": {"last_seen": time.time()},
                "$inc": {"seen": 1}
            },
            new=True,
        )
        if not doc:
            await add_infohash(infohash=infohash)


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    crawler = SPZCrawler()
    crawler.run(port=6881)
