# -*- coding: utf-8 -*-

import logging
import time

from utils import torrents_async, save_torrent_info
from pymongo.errors import AutoReconnect
from maga import Maga
from mala import get_metadata

WORKING_INFOHASHES = set()


class SPZCrawler(Maga):
    async def handle_get_peers(self, infohash, addr):
        pass
    
    async def handle_announce_peer(self, infohash, addr, peer_addr):
        if infohash in WORKING_INFOHASHES:
            return
        doc = await torrents_async.find_and_modify(
            {"infohash": infohash},
            update={
                "$set": {"last_seen": time.time()},
                "$inc": {"seen": 1}
            }
        )
        if doc or infohash in WORKING_INFOHASHES:
            return
        WORKING_INFOHASHES.add(infohash)
        logging.info("See new infohash: " + infohash)
        metainfo = await get_metadata(
            infohash, peer_addr[0], peer_addr[1], loop=self.loop
        )
        WORKING_INFOHASHES.discard(infohash)
        if metainfo:
            await save_torrent_info(infohash, metainfo)


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    crawler = SPZCrawler()
    logging.info("Crawler started")
    crawler.run(port=0)
