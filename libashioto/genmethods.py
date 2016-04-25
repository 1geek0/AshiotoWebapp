#Returns total count of all the gates in the gates' list provided
def total(gates):
    total_counts = 0
    for gate in gates:
        total_counts += int(gate['count'])
    return total_counts

#Returns latest counts at all gates with last sync time and name of each gate
def gates_top(event_code, start_time):
    event_request = events[event_code]

    gates_number = len(event_request['gates'])
    gates = []
    mega = 0
    i = 1
    while i <= gates_number:
        query = db.ashioto_data.find(
            {"eventCode":event_code,
             "gateID":i, "timestamp" : {"$gte" : start_time}}).sort([("timestamp",-1)]).limit(1)
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
