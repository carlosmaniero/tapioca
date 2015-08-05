import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.db = self.settings['db']


class TapiocaHandler(MainHandler):
    def get(self, client, route):
        self.write({
            'client': client,
            'route': route
        })
