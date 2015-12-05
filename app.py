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

#api keys
api_keys = ['geeKey4096', 'rajeKey2048', 'virajKey1024', 'mat']

class CountHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        key = str(self.get_argument('key'))
        if key in api_keys:
            count = int(self.get_argument('count'))#Number of People
            gateID = int(self.get_argument('gateID'))#GateID
            eventCode = int(self.get_argument('eventCode'))#Event Code
            times = int(self.get_argument('time',default=time.time()))#Unix Timestamp
            lat = float(self.get_argument('lat', default=0))
            lon = float(self.get_argument('lon', default=0))
            apiPOST = Item(ashiotoTable, data={
                'gateID' : gateID,
                'timestamp' : times,
                'latitude' : lat,
                'longitude' : lon,
                'outcount' : count,
                'plotted' : 0,
                'eventCode' : eventCode
            })
            #esponse = self.save_to_DB(apiPOST)
            serve = {
                "Count" : count,
                "GateID" : gateID,
                "Event Code" : eventCode,
                "Timestamp" : times,
                "Lat" : lat,
                "Long" : lon
            }
            self.write(serve)
            self.finish()
        else:
            self.write('Unable to authenticate. Check your api key')
            
    def save_to_DB(self, dbItem):
        dbItem.save()
class GetLastHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        key = str(self.get_argument('key'))
        if key in api_keys:
            self.write('hey')
    

    
if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/count_update", CountHandler),
        ]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    #http_server.start(0)
    #http_server.bind(8888)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()