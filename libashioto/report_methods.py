import datetime
import time
from libashioto.variables import db, events

def getNearest(timestamp, eventCode, gateID):
    countItem = db.get_collection("ashioto_data").find_one(
        {"eventCode": eventCode, "gateID": gateID, "timestamp": {"$gt": timestamp}})
    if countItem == None:
        return 0
    else:
        return countItem['outcount']
# Get 24-hour counts of a particular gate
def getHourlyDayGate(startTimestamp, eventCode, gateID):
    print("getting data")
    gateHourlyCounts = []
    nextHour = 1
    currentTimestamp = startTimestamp
    nextTimestamp = currentTimestamp + 3600000
    while nextHour <= 24:
        startCount = getNearest(currentTimestamp, eventCode, gateID)
        endCount = getNearest(nextTimestamp, eventCode, gateID)
        hourIncrement = endCount - startCount
        gateHourlyCounts.append(hourIncrement)
        currentTimestamp = nextTimestamp
        nextTimestamp += 3600000
        nextHour += 1
    return gateHourlyCounts


def getHourlyDayAll(startTimestamp, eventCode):
    hourlyData = []
    gateNumber = len(events[eventCode]['gates'])
    currentGateNumber = 1
    while currentGateNumber <= gateNumber:
        print("gate number: " + str(currentGateNumber))
        gateItem = {}
        gateItem['data'] = getHourlyDayGate(
            startTimestamp, eventCode, currentGateNumber)
        gateItem['name'] = events[eventCode][
            'gates'][currentGateNumber - 1]['name']
        hourlyData.append(gateItem)
        currentGateNumber += 1
    return hourlyData

def getStartTimestampDay():
    timeCurrent = round(time.time())
    date = datetime.datetime.fromtimestamp(timeCurrent)
    return (round(date.timestamp()/86400)*86400)-19800

def getGateID(gateName, event):
    namesList = [] 
    for item in events[event]["gates"]:
        namesList.append(item['name'])
    return namesList.index(gateName)+1
