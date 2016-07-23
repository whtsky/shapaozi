import tornado.web


class RequestHandler(tornado.web.RequestHandler):
    @property
    def torrents(self):
        return self.application.torrents
