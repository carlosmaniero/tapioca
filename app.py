import tornado.ioloop
import tornado.web
import motor
from urls import urls
from fields import Field

client = motor.MotorClient()
db = client.test_database

application = tornado.web.Application(urls, db=db)

Field().is_valid()

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
