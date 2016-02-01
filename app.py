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
import tornado.websocket

from PIL import Image
import io

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

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
        'theme' : 'black',
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
        'eventCode' : "test_event",
        'event_name' : "Test Event",
        'theme_primary' : 'blue-grey darken-3',
        'theme_accent' : "teal",
        "theme_text" : "white",
        'logo_name' : 'sulafest_logo.jpg',
        'background' : 'sulafest_background.jpg',
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
        'theme_primary' : 'white',
        'theme_accent' : "purple darken-2",
        "theme_text" : "white",
        'logo_name' : 'sulafest_logo.jpg',
        'background' : 'sulafest_background.jpg',
        'gates' : [
            {
                'name' : 'Entry'
            }
        ]
    }
}

client_dict = {} #Browser clients
bar_range_clients_dict = {} #Range Graph Clients
bar_overall_clients_dict = {} #Overall Graph Clients

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
        try:
            for user in client_dict[eventCode]:
                user.write_message({
                    'type' : 'count_update',
                    'gateID' : gateID,
                    'timestamp' : times,
                    'count' : count
                    })
            for user in bar_range_clients_dict[eventCode]:
                user.write_message
                pass
        except KeyError as ke:
            print("No Clients")
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
        gates_data = gates_top(event_code)
        print(gates_data)
        self.write(gates_data)
        
def gates_top(event_code):
    event_request = events[event_code]
    gates_number = len(event_request['gates'])
    gates = []
    mega = 0
    i = 1
    while i <= gates_number:
        query = db.ashioto_data.find(
            {"eventCode":event_code,
             "gateID":i}).sort([("timestamp",-1)]).limit(1)
        count = 0
        last = 0
        for item in query:
            count = item['outcount']
            mega += count
            last = item['timestamp']
        
        index = i-1
        
        gates.append({
            "name" : str(events[event_code]['gates'][index]['name']),
            "count" : int(count),
            "last_sync" : int(last)+19800
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
            theme_primary = events[event]['theme_primary']
            theme_accent = events[event]['theme_accent']
            theme_text = events[event]['theme_text']
            logo = events[event]['logo_name']
            background = events[event]['background']
            call = gates_top(event)
            all_gates = call['Gates']
            total_count = total(all_gates)
            self.render(
                "templates/template_dashboard.html",
                event_title=name,
                total_count=total_count,
                gates=all_gates,
                theme_primary=theme_primary,
                theme_accent=theme_accent,
                theme_text=theme_text,
                eventCode=event,
                logo_name=logo,
                background=background)
        else:
            self.write("error")
            
class LogoHandler(tornado.web.RequestHandler):
    #code
    def get(self, filename):
        image_file = Image.open("static_files/images/" + filename)
        image_io = io.BytesIO()
        image_file.save(image_io, format="JPEG")
        image_value = image_io.getvalue()
        self.set_header('Content-type', 'image/jpg')
        self.set_header('Content-Length', len(image_value))
        self.write(image_value)


class AshiotoWebSocketHandler(tornado.websocket.WebSocketHandler):
    eventCode = ""
    event_type = ""
    
    def open(self):
        print("Socket Opened")
    
    def on_message(self, msg):
        message = json.loads(msg)
        self.event_type = message['type']
        self.eventCode = message['event_code']
        if self.event_type == "browserClient_register":
            try:
                if self not in client_dict[self.eventCode]:
                    client_dict[self.eventCode].append(self)
            except KeyError as ke:
                client_dict[self.eventCode] = []
                client_dict[self.eventCode].append(self)
        elif self.event_type == "bar_range_register":
            print("New Range Client")
            try:
                if self not in bar_range_clients_dict[self.eventCode]:
                    bar_range_clients_dict[self.eventCode].append(self)
            except KeyError as ke:
                bar_range_clients_dict[self.eventCode] = []
                bar_range_clients_dict[self.eventCode].append(self)
            delay1 = int(message['delay1'])*60
            delay2 = int(message['delay2'])*60
            barInit = bar_init(delay1, delay2, self)
            print(barInit)
            self.write_message(barInit)
        elif self.event_type == "bar_overall_register":
            print("New Overall Client")
            self.time_step = int(message['time_step'])
            self.time_range = int(message['time_range'])
            self.time_type = str(message['time_type'])
            try:
                if self not in bar_overall_clients_dict[self.eventCode]:
                    bar_overall_clients_dict[self.eventCode].append(self)
            except KeyError as ke:
                bar_overall_clients_dict[self.eventCode] = []
                bar_overall_clients_dict[self.eventCode].append(self)
            if self.time_type == "day_one":
                self.time_day = int(message['time_day'])
            bar_stats = bar_overall(self)
            print("STATS: " + str(bar_stats))
            self.write_message(bar_stats)
        elif self.event_type == "time_difference":
            timestamp_start = int(db.ashioto_events.find({
            "eventCode" : self.eventCode
            })[0]['time_start'])
            time_difference = int((time.time() - timestamp_start)/60)
            resonse_dict = {"difference" : time_difference, "type":"time_difference_response" }
            print("TIME: " + str(resonse_dict))
            self.write_message(resonse_dict)
        
    def on_close(self):
        print("Socket Closed")
        client_dict[self.eventCode].remove(self)
def bar_init(delay1, delay2, client):
    x = 1
    gates_length = len(events[client.eventCode]['gates'])
    response_dict = {
        'type' : "bargraph_range_data",
        'data' : {}
    }
    timestamp_start = int(db.ashioto_events.find({
            "eventCode" : client.eventCode
            })[0]['time_start'])
    
    time_difference = int((time.time() - timestamp_start)/60)
    
    response_dict['data']['time_start'] = delay1
    response_dict['data']['time_stop'] = delay2
    response_dict['data']['gates'] = []
    gates_list = []
    while x <= gates_length:
        timestamp_range = time.time()-delay1
        timestamp_buffer = time.time()-delay2
        query_lower = "";
        try:
            query_lower = db.ashioto_data.find(
                {"eventCode" : client.eventCode,
                 "gateID" : x,
                 "timestamp" :
                    {"$lt":timestamp_range}},
                    {'_id': False, 'eventCode' : False }
            ).sort([("timestamp", -1)]).limit(1)[0]
            
            query_upper = db.ashioto_data.find(
                {"eventCode" : client.eventCode,
                 "gateID" : x,
                 "timestamp" :
                    {"$lt":timestamp_buffer}},
                    {'_id': False, 'eventCode' : False }
            ).sort([("timestamp", -1)]).limit(1)[0]
            
        except IndexError as error:
            client.write_message({
                'type' : 'bargraph_data',
                'error' : "Insufficient Data"
            })
            x += 1
            continue
        x += 1
    
        response_dict['data']['gates'].append({
            'last' : query_lower,
            'secondLast' : query_upper
        })
        print("RESPONSE: " + str(response_dict))
    return response_dict

def bar_overall(client):
    gates_length = len(events[client.eventCode]['gates'])
    time_step = client.time_step
    time_limit = client.time_range
    time_type = client.time_type
    eventCode = client.eventCode
    
    #Dict to be returned
    response_dict = {
        'type' : "bargraph_overall",
        'data' : {
            'gates' : []
        }
    }
    response_dict['data']['time_step'] = time_step*60
    
    #For finding event start time
    x = 1
    starts_list = []
    if time_type == "event":
        timestamp_start = int(db.ashioto_events.find({
            "eventCode" : client.eventCode
            })[0]['time_start'])
        timestamp_stop = int(timestamp_start+time_step*60)
        
    elif time_type == "current":
        timestamp_start = int(time.time()-time_step*60*time_limit)
        timestamp_stop = int(time.time())
        print("LIMIT: " + str(time_limit))
        print("START: " + str(timestamp_start))
        print("STOP: " + str(timestamp_stop))
    elif time_type == "day_one":
        timestamp_start = client.time_day
        timestamp_stop = timestamp_start+86399
        time_limit = 86399
    response_dict['data']['time_start'] = timestamp_start
    timestamp_between = timestamp_start+(time_limit)*3600
    timesToLoop = (time_limit)*60/time_step
    response_dict['data']['loop'] = timesToLoop
        
    #for fetching actual data
    z = 1
    while z <= gates_length:
        gates_list = []
        step_number = 1
        current_start = timestamp_start
        current_stop = timestamp_stop
        oldCount=0
        while step_number <= timesToLoop:
            try:
                newCount = int(query_range(current_start, current_stop,eventCode,z))
                difference = newCount-oldCount
                gates_list.append(difference)
                print("Gate: "+str(z))
                print("New Count: " + str(newCount))
                print("Old Count: " + str(oldCount));
                oldCount=newCount
            except IndexError as ie:
                client.write_message({"error":"IndexError"})
            current_start+=time_step*60
            #print("New Current Start: " + current_start)
            current_stop+=time_step*60
            #print("New Current Stop: " + current_stop)
            step_number+=1
        response_dict['data']['gates'].append(gates_list)
        print("OVERALL: " + str(response_dict))
        z+=1
    return response_dict

def query_range(gt,lt,evt,g_id):
    query_gate = db.ashioto_data.find({
        "eventCode" : evt,
        "gateID" : g_id,
        "timestamp" : {"$gte" : gt, "$lte" : lt}
    }).sort([("timestamp", 1)]).limit(1)[0]['outcount']
    return query_gate

class StartTimeHandler(tornado.web.RequestHandler):
    def get(self, eventCode):
        event = db.ashioto_events.update({"eventCode" : eventCode},
            {"$set": {"time_start": int(time.time())},}
        )
        self.write("KAM ZALA!!")
        print(event)

        
if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/count_update", CountHandler),
            (r"/event_confirm", EventCodeConfirmHandler),
            (r"/per_gate", PerGate_DataProvider),
            (r"/dashboard/([a-zA-Z_0-9]+)", DashboardHandler),
            (r"/websock", AshiotoWebSocketHandler),
            (r"/img/(?P<filename>.+\.jpg)?", LogoHandler),
            (r"/event_time_start/([a-zA-Z_0-9]+)", StartTimeHandler),
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static_files")
    )
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    #http_server.start(0)
    #http_server.bind(8888)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()