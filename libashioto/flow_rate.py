from tornado.web import RequestHandler
import time
from tornado_cors import CorsMixin
from libashioto.variables import db

class FlowRateHandler(CorsMixin, RequestHandler):
    CORS_ORIGIN = '*'
    CORS_HEADERS = 'Content-Type'
    CORS_METHODS = 'POST'
    def post(self):
        gateID = int(self.get_argument("gateID", 0))
        event = self.get_argument("event")
        time_interval = int(self.get_argument("time_interval")) #Time interval in seconds
        time_lt = int(time.time())
        time_gt = time_lt - time_interval
        print("LT: " + str(time_lt))
        print("GT: " + str(time_gt))
        flow_rate = str(getDiff(time_gt, time_lt, event, gateID))
        self.write(flow_rate)


def getDiff(gt, lt, evt, g_id):
    if g_id > 0:
        query_gate1 = db.ashioto_data.find({
            "eventCode": evt,
            "gateID": g_id,
            "timestamp": {"$gte": gt, "$lte": lt}
        }).sort("timestamp", -1).limit(1)[0]['outcount']
        query_gate2 = db.ashioto_data.find({
            "eventCode": evt,
            "gateID": g_id,
            "timestamp": {"$gte": gt, "$lte": lt}
        }).sort("timestamp", 1).limit(1)[0]['outcount']
        rate = query_gate1 - query_gate2
    else:
        noOfGates = len(db.ashioto_events.find({"eventCode": evt})[0]['gates'])
        newSum = 0
        oldSum = 0
        for i in range(1,noOfGates+1):
            newSum = newSum + db.ashioto_data.find({
                "eventCode": evt,
                "gateID": i,
                "timestamp": {"$gte": gt, "$lte": lt}
            }).sort("timestamp", -1).limit(1)[0]['outcount']

            oldSum = oldSum + db.ashioto_data.find({
                "eventCode": evt,
                "gateID": i,
                "timestamp": {"$gte": gt, "$lte": lt}
            }).sort("timestamp", 1).limit(1)[0]['outcount']
        rate = newSum - oldSum
    return rate
