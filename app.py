import time

import pickledb

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

from boto.dynamodb2.table import *

#DynamoDb Init
ashiotoTable = Table('ashioto2')

#PickleDB
keysDB = pickledb.load('api_keys.db', False)

#api keys
event_codes = ['test_event', 'ca_demo', 'sulafest_15']

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
            serve = 'Success'
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
class EventCodeConfirmHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        body_json = tornado.escape.json_decode(self.request.body)
        event_requested = body_json['event']
        if event_requested in event_codes:
            response = {
                'exists' : True
            }
            self.write(response)
        else:
            response = {
                'exists' : False
            }
            self.write(response)

class NewApiKeyHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        req_body_json = tornado.escape.json_decode(self.request.body)
        email_id = req_body_json['emailid']
        try:
            encoded = keysDB.dget('api_keys', email_id)
            encoded_json_old = {
                'key' : encoded
            }
            self.write(encoded_json_old)
        except KeyError as error:
            email_encoded = email_id.encode('rot13')
            keysDB.dadd('api_keys', (email_id, email_encoded))
            keysDB.dump()
            encoded_json_new = {
                'key' : email_encoded
            }
            self.write(encoded_json_new)
    
if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/count_update", CountHandler),
            (r"/event_confirm", EventCodeConfirmHandler),
            (r"/newkey", NewApiKeyHandler)
        ]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    #http_server.start(0)
    #http_server.bind(8888)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()