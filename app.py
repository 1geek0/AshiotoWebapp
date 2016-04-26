import time

import os

import json
import urllib3

import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
import tornado.template
import tornado.websocket
import tornado.gen

from PIL import Image
import io

from tornado.options import define, options
from tornado.web import RequestHandler

define("port", default=8000, help="run on the given port", type=int)

# libashioto imports
from libashioto.genmethods import *
from libashioto.graphmethods import *


class CountHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        req_body = tornado.escape.json_decode(self.request.body)
        dict_body = dict(req_body)
        count = int(dict_body.get('count'))  # Number of People
        gateID = int(dict_body.get('gateID'))  # GateID
        eventCode = dict_body.get('eventCode')  # Event Code
        times = int(dict_body.get('timestamp', time.time()))  # Unix Timestamp
        count_item = {
            'gateID': gateID,
            'timestamp': times,
            'outcount': count,
            'eventCode': eventCode
        }
        db.ashioto_data.insert(count_item)
        serve = {
            'error': False
        }
        try:
            for user in client_dict[eventCode]:
                user.write_message({
                    'type': 'count_update',
                    'gateID': gateID,
                    'timestamp': times,
                    'count': count
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
                'exists': True
            }
            self.write(response)
        else:
            response = {
                'exists': False
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


class DashboardHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, event):
        if event in event_codes:
            start_time = db.ashioto_events.find({"eventCode": event})[0]['time_start']
            name = events[event]['event_name']
            theme_primary = events[event]['theme_primary']
            theme_accent = events[event]['theme_accent']
            theme_text = events[event]['theme_text']
            logo = events[event]['logo_name']
            background = events[event]['background']
            call = gates_top(event, start_time)
            all_gates = call['Gates']
            total_count = total(all_gates)
            size = 6
            if len(all_gates) == 1:
                size = 12
            self.render(
                "templates/template_dashboard.html",
                event_title=name,
                total_count=total_count,
                gates=all_gates,
                size=size,
                theme_primary=theme_primary,
                theme_accent=theme_accent,
                theme_text=theme_text,
                eventCode=event,
                logo_name=logo,
                background=background)
        else:
            self.write("Event not found")
            self.finish()


class LogoHandler(tornado.web.RequestHandler):
    # code
    def get(self, filename):
        image_file = Image.open("static_files/images/" + filename)
        image_io = io.BytesIO()
        image_file.save(image_io, format="JPEG")
        image_value = image_io.getvalue()
        self.set_header('Content-type', 'image/jpg')
        self.set_header('Content-Length', len(image_value))
        self.write(image_value)


class AshiotoWebSocketHandler(tornado.websocket.WebSocketHandler):
    # To always allow access to websocket
    def check_origin(self, origin):
        return True

    eventCode = ""
    event_type = ""

    def on_message(self, msg):
        message = json.loads(msg)
        self.event_type = message['type']
        self.eventCode = message['event_code']
        if self.event_type == "browserClient_register":
            try:
                if self not in client_dict[self.eventCode]:
                    client_dict[self.eventCode].append(self)
            except KeyError:
                client_dict[self.eventCode] = []
                client_dict[self.eventCode].append(self)
        elif self.event_type == "bar_range_register":  # Make into HTTP call
            print("New Range Client")
            try:
                if self not in bar_range_clients_dict[self.eventCode]:
                    bar_range_clients_dict[self.eventCode].append(self)
            except KeyError:
                bar_range_clients_dict[self.eventCode] = []
                bar_range_clients_dict[self.eventCode].append(self)
            delay1 = int(message['delay1']) * 60
            delay2 = int(message['delay2']) * 60
            barInit = bar_init(delay1, delay2, self)
            print(barInit)
            self.write_message(barInit)
        elif self.event_type == "bar_overall_register":  # Make into HTTP call
            print("New Overall Client")
            self.time_step = int(message['time_step'])
            self.time_range = int(message['time_range'])
            self.time_type = str(message['time_type'])
            print("Time Type: " + str(self.time_type))
            try:
                if self not in bar_overall_clients_dict[self.eventCode]:
                    bar_overall_clients_dict[self.eventCode].append(self)
            except KeyError:
                bar_overall_clients_dict[self.eventCode] = []
                bar_overall_clients_dict[self.eventCode].append(self)
            if self.time_type == "day_one":
                self.time_day = int(message['time_day'])
            if self.time_type == "day_between":
                self.time_one = int(message['time_one'])
                self.time_two = int(message['time_two'])
                print("Time One and Two" + str(self.time_one) + "\n" + str(self.time_two))
            if self.time_type != "day_between":
                bar_stats = bar_overall(self)
            else:
                bar_stats = bar_between_days(self)
            # print("STATS: " + str(bar_stats))
            self.write_message(bar_stats)
        elif self.event_type == "time_difference":
            timestamp_start = int(db.ashioto_events.find({
                "eventCode": self.eventCode
            })[0]['time_start'])
            time_difference = int((time.time() - timestamp_start) / 60)
            resonse_dict = {"difference": time_difference, "type": "time_difference_response"}
            print("TIME: " + str(resonse_dict))
            self.write_message(resonse_dict)

    def on_close(self):
        print("Socket Closed")
        client_dict[self.eventCode].remove(self)


class StartTimeHandler(tornado.web.RequestHandler):
    def get(self, eventCode):
        event = db.ashioto_events.update({"eventCode": eventCode},
                                         {"$set": {"time_start": int(time.time())},}
                                         )
        self.write("KAM ZALA!!")
        print(event)


class UserStatsHandler(tornado.web.RequestHandler):
    def get(self):
        stats_json = {}
        client_lengths = 0
        for i in client_dict:
            stats_json[i] = str(len(client_dict[i]))
            client_lengths += len(client_dict[i])
        stats_json['Total Clients'] = str(client_lengths)
        self.write(stats_json)


class CreateUser(RequestHandler):
    """Needs: events, email and type in json"""

    def post(self):
        request_body = dict(tornado.escape.json_decode(self.request.body))
        user_events = request_body['events']
        user_email = request_body['email']
        user_type = request_body['type']
        user_tempcode = generateConfirmCode()
        user_dbitem = {'email': user_email, 'type': user_type, 'events': user_events, 'tempCode': user_tempcode}
        try:
            db.ashioto_users.find({'email': user_email})[0]
            self.write(False)
        except IndexError:
            db.ashioto_users.insert(user_dbitem)
            sendConfirmEmail(user_email, user_tempcode)
            self.write(True)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            # (r"/websock", AshiotoWebSocketHandler),
            (r"/img/(?P<filename>.+\.jpg)?", LogoHandler),
            (r"/count_update", CountHandler),
            (r"/event_confirm", EventCodeConfirmHandler),
            (r"/per_gate", PerGate_DataProvider),
            (r"/dashboard/([a-zA-Z_0-9]+)", DashboardHandler),
            (r"/dashboard/([a-zA-Z_0-9]+)/", DashboardHandler),
            (r"/event_time_start/([a-zA-Z_0-9]+)", StartTimeHandler),
            (r"/event_time_start/([a-zA-Z_0-9]+)/", StartTimeHandler),
            (r"/userstats", UserStatsHandler),
            (r"/userstats/", UserStatsHandler),
            (r"/createUser", CreateUser),
            (r"/createUser/", CreateUser)
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static_files")
    )
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    # http_server.start(0)
    # http_server.bind(options.port)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
