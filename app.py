import time

import os

import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
import tornado.template
import tornado.websocket
import tornado.gen
from tornado_cors import CorsMixin

from PIL import Image
import io

import datetime

from tornado.options import define, options
from tornado.web import RequestHandler

from passlib.hash import sha256_crypt

define("port", default=8000, help="run on the given port", type=int)

# libashioto imports
from libashioto.variables import *
from libashioto.genmethods import *
from libashioto.graphmethods import *
from libashioto.passmethods import *
from libashioto.flow_rate import FlowRateHandler
from libashioto.report_methods import getHourlyDayGate, getStartTimestampDay, getGateID

# Stores the received count according to the event


class CountHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def post(self):
        req_body = tornado.escape.json_decode(self.request.body)
        dict_body = dict(req_body)
        count = int(dict_body.get('count'))  # Number of People
        gateID = int(dict_body.get('gateID'))  # GateID
        eventCode = dict_body.get('eventCode')  # Event Code
        times = int(dict_body.get('timestamp', time.time())) * 1000  # Unix Timestamp
        countdouble = int(dict_body.get('count-double')) # Double count amount
        countoverstep = int(dict_body.get('count-overstep')) # Overstep amount
        countnotcounted = int(dict_body.get('count-notcounted')) # Not counted amount
        volunteeremail = dict_body.get('email')
        count_item = {
            'gateID': gateID,
            'timestamp': times,
            'outcount': count,
            'eventCode': eventCode,
            'count-double': countdouble,
            'count-overstep': countoverstep,
            'count-notcounted': countnotcounted,
            'volunteeremail': volunteeremail
        }
        db.ashioto_data.insert(count_item)
        serve = {
            'success': True
        }
        self.write(serve)
        self.finish()


class BusDataHandler(RequestHandler):
    def post(self):
        req_body = tornado.escape.json_decode(self.request.body)
        dict_body = dict(req_body)
        outcount = int(dict_body.get('outcount'))
        incount = int(dict_body.get('incount'))
        busID = str(dict_body.get('busID'))
        fleetCode = str(dict_body.get('fleetCode'))
        timestamp = int(dict_body.get('timestamp', time.time())) * 1000
        latitude = float(dict_body.get('latitude'))
        longitude = float(dict_body.get('longitude'))
        bus_data_item = {
            'outcount': outcount,
            'incount': incount,
            'busID': busID,
            'fleetCode': fleetCode,
            'timestamp': timestamp,
            'latitude': latitude,
            'longitude': longitude,
        }
        db.ashioto_data_bus.insert(bus_data_item) # Not to be confused with ashioto_data which is for a general purpose dataset
        serve = {
            'success': True
        }
        self.write(serve)
        self.finish()

# Deprecated. Returns True if the requested event exists. Used only by old app
# TODO: remove this


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

# Gives last count and last sync time of all the gates in an event


class PerGate_DataProvider(CorsMixin, tornado.web.RequestHandler):
    CORS_ORIGIN = '*'
    CORS_HEADERS = 'Content-Type'
    CORS_METHODS = 'GET'
    @tornado.gen.coroutine
    def get(self):
        event_code = self.get_argument('eventCode')
        start_time = events[event_code]['start_time']
        gates_data = gates_top(event_code, start_time=start_time)
        print(gates_data)
        self.write(gates_data)
        self.finish()

# Serves the dashboard page


class DashboardHandler(tornado.web.RequestHandler):

    def get(self, event_requested):
        if event_requested in event_codes:
            event_type = events[event_requested]['type']
            if event_type == "public":  # Directly serves page if event is public
                if event_requested == "mrally":
                    showRally(self, "mrally")
                else:
                    try:
                        client_dict[event_requested].append(self)
                    except KeyError:
                        client_dict[event_requested] = []
                        client_dict[event_requested].append(self)
                    showDashboard(self, event_requested)
            elif event_type == "private":  # If the event is private it redirects to the login page
                if self.get_secure_cookie("user"):
                    user_email = self.get_secure_cookie("user").decode('utf-8')
                    user_events = db.ashioto_users.find(
                        {'email': user_email})[0]['events']
                    if event_requested in user_events:
                        showDashboard(self, event_requested)
                    else:
                        self.write("Not authenticated for this dashboard")
                else:
                    self.redirect("/login")
        else:
            self.write("Event not found")
            self.finish()


# Deprecated now. Handles images
class LogoHandler(tornado.web.RequestHandler):

    def get(self, filename):
        image_file = Image.open("static_files/images/" + filename)
        image_io = io.BytesIO()
        image_file.save(image_io, format="JPEG")
        image_value = image_io.getvalue()
        self.set_header('Content-type', 'image/jpg')
        self.set_header('Content-Length', len(image_value))
        self.write(image_value)

# Handles real-time updation of the dashboard
# TODO: It's broken right now, needs to be fixed


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
                print("Time One and Two" + str(self.time_one) +
                      "\n" + str(self.time_two))
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
            resonse_dict = {"difference": time_difference,
                            "type": "time_difference_response"}
            print("TIME: " + str(resonse_dict))
            self.write_message(resonse_dict)

    def on_close(self):
        print("Socket Closed")
        client_dict[self.eventCode].remove(self)


# This resets the time after which the dashboard will pick the entries from
# TODO: Eliminate this altogether by making the front-end code fetch
# entries smartly
class StartTimeHandler(tornado.web.RequestHandler):

    def get(self, eventCode):
        event = db.ashioto_events.update({"eventCode": eventCode},
                                         {"$set": {
                                             "time_start": int(time.time())}, }
                                         )
        self.write("KAM ZALA!!")
        print(event)

# Gives the stats about current active dashboard users


class UserStatsHandler(tornado.web.RequestHandler):

    def get(self):
        stats_json = {}
        client_lengths = 0
        for i in client_dict:
            stats_json[i] = str(len(client_dict[i]))
            client_lengths += len(client_dict[i])
        stats_json['Total Clients'] = str(client_lengths)
        self.write(stats_json)

# Creates user for login


class CreateUser(RequestHandler):
    """Needs: events, email, password and type in json"""

    def post(self):
        request_body = dict(tornado.escape.json_decode(self.request.body))
        user_events = request_body['events']
        user_email = request_body['email']
        user_type = request_body['type']
        user_pass_plain = request_body['pass']
        user_pass_hashed = hashpasswd(user_pass_plain)
        user_dbitem = {'email': user_email, 'type': user_type,
                       'events': user_events, 'password': user_pass_hashed}
        try:
            db.ashioto_users.find({'email': user_email})[0]
            self.write('False')
        except IndexError:
            db.ashioto_users.insert(user_dbitem)
            sendConfirmEmail(user_email, user_pass_plain)
            self.write('True')

# This call is triggered only from the confirmation email that is sent
# afer calling CreateUser


class ConfirmUser(RequestHandler):
    """Confirms User"""

    def get(self, code):
        userConfirmed = confirmUser(code)
        if userConfirmed:
            self.set_secure_cookie("first_setup", code, 1)
            self.redirect("/firstset", True)
        else:
            pass

# Handles everything related to authentication


class LoginHandler(RequestHandler):
    """Login Page"""

    # Serves the login page
    def get(self):
        self.render("templates/template_login.html")

    # Checks the email and sets auth cookie
    def post(self):
        user_email = self.get_argument("email")
        user_pass = self.get_argument("password")
        try:
            user_db = db.ashioto_users.find({"email": user_email})[0]
            user_auth = sha256_crypt.verify(user_pass, user_db['password'])
            print("Auth: " + str(user_auth))
            if user_auth:
                self.set_secure_cookie("user", user_email, 1)
                url = "/dashboard/" + user_db['events'][0]
                print(url)
                self.redirect(url, True)
            else:
                self.write("Wrong password")
        except IndexError:
            self.write("Account doesn't exist")

# Returns a list of public events


class EventsListHandler(RequestHandler):

    def get(self):
        self.write(listEvents())
        self.finish()

# Returns a list of gates in a particular event


class GatesListHandler(RequestHandler):

    def get(self):
        eventCode = self.get_argument("event")
        gatesDict = {
            "Gates": events[eventCode]['gates']
        }
        self.write(gatesDict)
        self.finish()


class RewatDataHandler(RequestHandler):

    def get(self):
        rewatData = []
        dbData = db.ashioto_data.find({"eventCode": "rewat"})
        for point in dbData:
            self.write("||Count: " + str(point['outcount']) + " Timestamp: " + datetime.datetime.fromtimestamp(
                point['timestamp']).strftime('%d %b %Y %I:%M:%S %p') + " ||")
        self.finish()
        # self.render("templates/template_rewat.html", rewatData=rewatData)


class LandingHandler(RequestHandler):

    def get(self):
        self.render("templates/template_landing.html")


class MobileAuthHandler(RequestHandler):

    def post(self):
        user_email = self.get_argument('email')
        user_pass = self.get_argument('pass')
        user_event = self.get_argument('event')
        try:
            user_db = db.ashioto_users.find({'email': user_email})[0]
            user_auth = sha256_crypt.verify(user_pass, user_db['password'])
            if user_auth and (user_db['event'] == user_event or user_db['event'] == "NA"):
                superadmin = user_db['type'] == True
                self.write({"auth": True, "s_admin": superadmin})
            else:
                self.write({"auth": True})
        except IndexError as e:
            self.write({"auth": True})


class ReportHandler(RequestHandler):
    def get(self):
        location_name = self.get_argument("eventCode")
        gate_name = self.get_argument("gateName")
        startTime = float(self.get_argument("startTime"))
        table_data = getHourlyDayGate(startTimestamp=startTime, eventCode=location_name, gateID=getGateID(gate_name, location_name))
        date = datetime.datetime.fromtimestamp(startTime/1000).strftime("%d/%m/%Y")
        print(table_data)
        self.render("templates/reports/basic.html", location_name=location_name, gate_name=gate_name, table_data=table_data, date=date)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[  # Binds the handlers
            (r"/", LandingHandler),
            (r"/websock", AshiotoWebSocketHandler),
            (r"/img/(?P<filename>.+\.jpg)?", LogoHandler),
            (r"/count_update", CountHandler),
            (r"/bus_update", BusDataHandler),
            (r"/event_confirm", EventCodeConfirmHandler),
            (r"/per_gate", PerGate_DataProvider),
            (r"/dashboard/([a-zA-Z_0-9]+)", DashboardHandler),
            (r"/dashboard/([a-zA-Z_0-9]+)/", DashboardHandler),
            (r"/event_time_start/([a-zA-Z_0-9]+)", StartTimeHandler),
            (r"/event_time_start/([a-zA-Z_0-9]+)/", StartTimeHandler),
            (r"/userstats", UserStatsHandler),
            (r"/userstats/", UserStatsHandler),
            (r"/createUser", CreateUser),
            (r"/createUser/", CreateUser),
            (r"/confirmUser/([a-zA-Z_0-9]+)", ConfirmUser),
            (r"/confirmUser/([a-zA-Z_0-9]+)/", ConfirmUser),
            (r"/login", LoginHandler),
            (r"/login/", LoginHandler),
            (r"/flow_rate", FlowRateHandler),
            (r"/listEvents", EventsListHandler),
            (r"/listGates", GatesListHandler),
            (r"/rewatData", RewatDataHandler),
            (r"/mobileauth", MobileAuthHandler),
            (r"/report", ReportHandler)
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static_files"),
        cookie_secret=cookie_secret
    )
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    # http_server.start(0)
    # http_server.bind(options.port)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
