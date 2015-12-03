import time
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

from boto.dynamodb2.table import *

#DynamoDb Init
ashiotoTable = Table('ashioto2')

class DataHandler(tornado.web.RequestHandler):
    def get(self):
        count = int(self.get_argument('count'))#Number of People
        gateID = int(self.get_argument('gateID'))#GateID
        eventCode = int(self.get_argument('eventCode'))#Event Code
        times = int(time.time())#Unix Timestamp
        apiPOST = Item(ashiotoTable, data={
            'gateID' : gateID,
            'timestamp' : times,
            'latitude' : 0,
            'longitude' : 0,
            'outcount' : count,
            'plotted' : 0
        })
        apiPOST.save()
        self.write('Data Saved')
    
if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/put", DataHandler),
        ]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()