from handlers import TapiocaHandler

urls = [
    (r"/(?P<client>[a-zA-Z\-0-9\.:,_]+)/(?P<route>[a-zA-Z\-0-9\.:,_]+)/", TapiocaHandler),
]
