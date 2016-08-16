# -*- coding: utf-8 -*-
import time
import chardet
import pymongo

from config import MONGO_HOST
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from maga import proper_infohash


torrents_async = AsyncIOMotorClient(MONGO_HOST).spz.torrents
torrents = MongoClient(MONGO_HOST).spz.torrents
torrents.create_index([('infohash', pymongo.ASCENDING)], unique=True)
torrents.create_index([('title', "text")])

def guess_and_decode(bytes):
    result = chardet.detect(bytes)
    try:
        if result.get("confidence", 0) > 0.8:
            return bytes.decode(result["encoding"])
        return bytes.decode("GB18030")
    except:
        return


def bytes_to_str(b):
    try:
        if isinstance(b, bytes):
            return b.decode()
        else:
            return str(b)
    except UnicodeDecodeError:
        return guess_and_decode(b)


def path_bytes_to_str(path_byte):
    return [bytes_to_str(x) for x in path_byte]


async def save_torrent_info(infohash, info):
    try:
        infohash = proper_infohash(infohash)
    except:
        return False
    if not isinstance(info, dict):
        return False
    if await torrents_async.find_one({"infohash": infohash}):
        return True
    doc = dict(
        infohash=infohash,
        last_seen=time.time(),
        first_seen=time.time(),
        seen=1
    )
    title = bytes_to_str(info[b"name"])
    if not title:
        return
    doc["title"] = title

    if b"files" in info:
        length_sum = 0
        files = []
        for file in info[b"files"]:
            length_sum += file[b"length"]
            path_bytes = file[b"path"]
            files.append({
                "path": path_bytes_to_str(path_bytes),
                "length": file[b"length"]
            })
        doc["files"] = files
        doc["length"] = length_sum
    else:
        doc["length"] = info[b"length"]
        doc["filename"] = bytes_to_str(info[b'name'])
    try:
        await torrents_async.insert(doc)
    except DuplicateKeyError:
        return True
    except Exception:
        return False
    return True
