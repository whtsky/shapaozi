# -*- coding: utf-8 -*-
import base64
import binascii
import time
import bencoder
import asyncio
import logging

import aiohttp
import cchardet as chardet

from config import MONGO_HOST
from concurrent.futures import FIRST_COMPLETED
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

torrents_async = AsyncIOMotorClient(MONGO_HOST).spz.torrents


async def fetch_url(url, decode=True, timeout=3):
    logging.debug("fetching {}".format(url))
    try:
        with aiohttp.Timeout(timeout):
            async with aiohttp.get(url) as response:
                if decode:
                    try:
                        return await response.text()
                    except:
                        body = await response.read()
                        return guess_and_decode(body)
                return await response.read()
    except:
        return b""


def guess_and_decode(bytes):
    result = chardet.detect(bytes)
    try:
        if result.get("confidence", 0) > 0.8:
            return bytes.decode(result["encoding"])
        return bytes.decode("GB18030")
    except:
        return


async def wait_for_rv(fs, rv):
    while fs:
        done, fs = await asyncio.wait(fs, return_when=FIRST_COMPLETED)
        if any([x.result == rv for x in done]):
            for c in fs:
                c.cancel()
            return True
    return False


def bytes_to_str(b):
    try:
        if isinstance(b, bytes):
            return b.decode()
        else:
            return str(b)
    except UnicodeDecodeError:
        rv = guess_and_decode(b)
        if rv:
            return rv
        else:
            return False


def vuze_encode(infohash):
    return base64.b32encode(binascii.unhexlify(infohash.encode())).decode()


def path_bytes_to_str(path_byte):
    return [bytes_to_str(x) for x in path_byte]


async def save_torrent_info(infohash, torrent_info):
    if not isinstance(torrent_info, dict):
        return False
    if await torrents_async.find_one({"infohash": infohash}):
        return True
    doc = dict(
        infohash=infohash,
        last_seen=time.time(),
        first_seen=time.time(),
        seen=1
    )
    if b'name.utf-8' in torrent_info:
        title_bytes = torrent_info[b'name.utf-8']
    else:
        title_bytes = torrent_info[b"name"]
    title = bytes_to_str(title_bytes)
    if not title:
        return
    doc["title"] = title

    if b"files" in torrent_info:
        length_sum = 0
        files = []
        for file in torrent_info[b"files"]:
            length_sum += file[b"length"]
            if b'path.utf-8' in file:
                path_bytes = file[b'path.utf-8']
            else:
                path_bytes = file[b"path"]
            files.append({
                "path": path_bytes_to_str(path_bytes),
                "length": file[b"length"]
            })
        doc["files"] = files
        doc["length"] = length_sum
    else:
        doc["length"] = torrent_info[b"length"]
        if b'name.utf-8' in torrent_info:
            name_bytes = torrent_info[b'name.utf-8']
        else:
            name_bytes = torrent_info[b'name']
        doc["filename"] = bytes_to_str(name_bytes)
    try:
        await torrents_async.insert(doc)
    except DuplicateKeyError:
        return True
    return True


async def save_new_torrent(infohash, url):
    if await torrents_async.find_one({"infohash": infohash}):
        return

    import logging
    logging.debug("Downloading torrent file for {} from {}".format(
        infohash, url
    ))

    body = await fetch_url(url, decode=False)
    if not body:
        return False
    try:
        torrent_info = bencoder.bdecode(body)
    except bencoder.BTFailure:
        return False
    try:
        return await save_torrent_info(
            infohash,
            torrent_info.get(b"info", None)
        )
    except:
        return False


async def add_infohash(infohash):
    from maga import proper_infohash
    infohash = proper_infohash(infohash)
    if await torrents_async.find_one({"infohash": infohash}):
        return

    loop = asyncio.get_event_loop()
    tasks = []

    # 迅雷
    url = "http://bt.box.n0808.com/{}/{}/{}.torrent".format(
        infohash[:2], infohash[-2:], infohash
    )
    tasks.append(loop.create_task(save_new_torrent(infohash, url)))

    for url_template in [
        "http://www.torrenthound.com/torrent/{}",
        "http://www.ciliinfo.com/download/{}.torrent",
        "http://torcache.net/torrent/{}.torrent",
        "http://thetorrent.org/{}.torrent",
        "http://torrentproject.org/torrent/{}.torrent",
        "http://torrage.biz/torrent/{}.torrent",
        "http://btcache.me/torrent/{}",
        "http://TheTorrent.org/{}.torrent",
        "http://btcache.sobt5.com/{}.torrent",
    ]:
        tasks.append(loop.create_task(
            save_new_torrent(infohash, url_template.format(infohash))
        ))

    await wait_for_rv(tasks, rv=True)
