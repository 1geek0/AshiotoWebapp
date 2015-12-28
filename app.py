import time

import pickledb

import json

from pymongo import MongoClient

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

#MongoDB init
client = MongoClient()
client.ashioto_data.authenticate("rest_user", "Ashioto_8192")
db = client.ashioto_data

#api keys
event_codes = {'test_event', 'ca_demo', 'sulafest_15' 'express_tower'}
events = {
    'express_tower' : {
        'gates' : [
            {
                'name' : 'Express Towers'
            },
            {
                'name' : 'Exit'
            }
        ]
    },
    'test_event' : {
        'gates' : [
            {
                'name' : "Entry"
            },
            {
                'name' : 'Exit'
            }
        ]
    },
    'sulafest' : {
        'gates' : [
            {
                'name' : 'Entry'
            },
            {
                'name' : 'Exit'
            }
        ]
    }
}

class CountHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        req_body = tornado.escape.json_decode(self.request.body)
        dict_body = dict(req_body)
        count = int(dict_body.get('count')) #Number of People
        gateID = int(dict_body.get('gateID'))#GateID
        eventCode = dict_body.get('eventCode') #Event Code
        times = int(dict_body.get('timestamp', time.time())) #Unix Timestamp
        lat = float(dict_body.get('lat', 0.0))
        lon = float(dict_body.get('long', 0.0))
        apiPOST = Item(ashiotoTable, data={
            'gateID' : gateID,
            'timestamp' : times,
            'latitude' : lat,
            'longitude' : lon,
            'outcount' : count,
            'plotted' : 0,
            'event_code' : eventCode
        },)
        response = self.save_to_DB(apiPOST)
        serve = {
            'error' : False
        }
        self.write(serve)
        self.finish()      
    def save_to_DB(self, dbItem):
        dbItem.save()

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

class PerGate_DataProvider(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        request_body = tornado.escape.json_decode(self.request.body)
        event_code = request_body['event_code']
        event_request = events[event_code]
        gates_number = len(event_request['gates'])
        gates = []
        i = 1
        while i <= gates_number:
            query = ashiotoTable.query_2(
                index="event_code-timestamp-index",
                reverse=True,
                limit=1,
                event_code__eq=event_code,
                timestamp__gt=1,
                query_filter={"gateID__eq":i})
            count = 0
            last = 0
            for item in query:
                count = item['outcount']
                print(count)
                last = item['timestamp']
                print(last)
            
            index = i-1
            
            gates.append({
                "name" : str(events[event_code]['gates'][index]['name']),
                "count" : int(count),
                "last_sync" : int(last)
            })
            i+=1
        response = {
            'Gates' : json.dumps(gates)
        }
        self.write(response)

    
if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/count_update", CountHandler),
            (r"/event_confirm", EventCodeConfirmHandler),
            (r"/per_gate", PerGate_DataProvider)
        ]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    #http_server.start(0)
    #http_server.bind(8888)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()