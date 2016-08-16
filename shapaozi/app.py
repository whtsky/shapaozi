import asyncio
import tornado.web
import tornado.httpserver
import os

MONGO_HOST = os.environ.get("MONGO_HOST", 'localhost')


class Application(tornado.web.Application):
    def __init__(self):
        from handlers import status, detail, search
        super().__init__(handlers=[
            (r"/api/search/([^/]+)", search.SearchHandler),
            (r"/api/search/([^/]+)/page/(\d+)", search.SearchHandler),
            (r"/api/infohash/([A-Za-z0-9]{40})", detail.DetailHandler),
            (r"/api/random", detail.RandomHandler),
            (r"/api/status", status.StatusHandler),
        ], debug=True)
        import motor
        self.torrents = motor.MotorClient(MONGO_HOST).spz.torrents


def main():
    from tornado.platform.asyncio import AsyncIOMainLoop
    AsyncIOMainLoop().install()
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(8000)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
