from libashioto.variables import db
import random
import time

counts = {
'gate1': 0,
'gate2': 0
}

while True:
    for x in range(1,3):
        counts['gate'+str(x)] = counts['gate'+str(x)] + random.randint(1,200)  # Number of People
        gateID = x  # GateID
        eventCode = "test"  # Event Code
        times = int(time.time())  # Unix Timestamp
        count_item = {
            'gateID': gateID,
            'timestamp': times,
            'outcount': counts['gate'+str(x)],
            'eventCode': eventCode
        }
        print(count_item)
        db.ashioto_data.insert(count_item)
    time.sleep(60)
