from libashioto.variables import db
import random
import time

counts = {
'gate1': 0,
'gate2': 0
}

times = int(time.time())
addition1 = 0

while True:
    for x in range(1,3):
        if x == 1:
            addition1 = random.randint(1,200)
            counts['gate1'] = counts['gate1'] + addition1 # Number of People
        elif x==2:
            counts['gate2'] = counts['gate2'] + random.randint(1, addition1-1)
        gateID = x  # GateID
        eventCode = "test"  # Event Code
        times = times+random.randint(55,63)
          # Unix Timestamp
        count_item = {
            'gateID': gateID,
            'timestamp': times,
            'outcount': counts['gate'+str(x)],
            'eventCode': eventCode
        }
        print(count_item)
        db.ashioto_data.insert(count_item)
