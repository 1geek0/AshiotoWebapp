import time

import pickledb
import os

import json
import urllib3

import datetime

from pymongo import MongoClient

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
import tornado.template
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
event_codes = ['test_event', 'sulafest_16', 'express_tower']
events = {
    'express_tower' : {
        'event_name' : "Indian Express Demo",
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
        'event_name' : "Test Event",
        'gates' : [
            {
                'name' : "Entry"
            },
            {
                'name' : 'Exit'
            }
        ]
    },
    'sulafest_16' : {
        'event_name' : "SulaFest 2016",
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
        count_item = {
            'gateID' : gateID,
            'timestamp' : times,
            'outcount' : count,
            'eventCode' : eventCode
        }
        db.ashioto_data.insert(count_item)
        serve = {
            'error' : False
        }
        self.write(serve)
        self.finish()

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
        gates_data = pull_gates(event_code)
        self.write(gates_data)
        
def gates_top(event_code):
    event_request = events[event_code]
    gates_number = len(event_request['gates'])
    gates = []
    mega = 0
    i = 1
    while i <= gates_number:
        query = db.ashioto_data.find({"event_code":event_request, "gateID":i}).sort({"timestamp":-1}).limit(1)
        count = 0
        last = 0
        for item in query:
            count = item['outcount']
            print(count)
            mega += count
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
        'Gates' : gates
    }
    return response

def total(gates):
    total_counts = 0
    for gate in gates:
        total_counts += int(gate['count'])
    return total_counts


class DashboardHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, event):
        if event in event_codes:
            name = events[event]['event_name']
            call = pull_gates(event)
            self.gen_website(call, name)
        else:
            self.write("error")
    def gen_website(self, call, name):
        all_gates = call['Gates']
        total_count = total(all_gates)
        self.render(
                "templates/template_dashboard.html",
                event_title=name,
                total_count=total_count,
                gates=all_gates)
        self.finish()
    
if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/count_update", CountHandler),
            (r"/event_confirm", EventCodeConfirmHandler),
            (r"/per_gate", PerGate_DataProvider),
            (r"/dashboard/([a-zA-Z_0-9]+)", DashboardHandler)
        ],
        static_path=os.path.join(os.path.dirname(__file__), "materialize_files")
    )
    http_server = tornado.httpserver.HTTPServer(app)
    #http_server.start(0)
    #http_server.bind(8888)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()