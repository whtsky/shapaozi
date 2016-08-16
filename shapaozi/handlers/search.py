# -*- coding: utf-8 -*-
import string
import math

from . import RequestHandler
from .utils import infohash_simplified

from tornado.web import HTTPError


_english_words = string.ascii_letters + string.digits


def _is_english(word):
    return all(x in _english_words for x in word)


def process_text(text):
    if '"' in text:
        return text  # 这是会玩的
    words = []
    _last_is_english = False
    for word in text.split():
        if word.isdigit() and len(word) < 2 and words:
            if _last_is_english:
                words[-1] += " " + word
            else:
                words[-1] += word
        elif _is_english(word):
            if _last_is_english:
                words[-1] += " " + word
            else:
                words.append(word)
                _last_is_english = True
        else:
            words.append(word)
            _last_is_english = False
    return '"' + '" "'.join(words) + '"'


class SearchHandler(RequestHandler):
    async def get(self, text, page=1):
        if len(text) > 100:
            raise HTTPError(403)
        try:
            page = int(page)
        except TypeError:
            page = 1
        cursor = self.torrents.find({
            "$text": {"$search": process_text(text)}
        }, sort=[('last_seen', -1)])
        total = await cursor.count()
        if page > 1:
            cursor = cursor.skip((page - 1)*20)
        cursor.limit(20)
        result_list = []
        async for result in cursor:
            result_list.append(infohash_simplified(result))
        self.write(dict(
            total=total,
            page=page,
            max_page=math.ceil(total/20),
            results=result_list
        ))
