from libashioto.variables import *


# Returns total difference of count
def day_total(evt, day_timestamp_stop, day_timestamp_start, g_id):
    query_gate = db.ashioto_data.find({
        "eventCode": evt,
        "gateID": g_id,
        "timestamp": {"$lte": day_timestamp_stop, "$gte": day_timestamp_start}
    }).sort([("timestamp", -1)]).limit(1)[0]['outcount']
    return query_gate


def query_range(gt, lt, evt, g_id, reverse):
    tSort = 1
    if reverse:
        tSort = -1
    query_gate = db.ashioto_data.find({
        "eventCode": evt,
        "gateID": g_id,
        "timestamp": {"$gte": gt, "$lte": lt}
    }).sort([("timestamp", tSort)]).limit(1)[0]['outcount']
    return query_gate


def bar_between_days(client):
    gates_length = len(events[client.eventCode]['gates'])
    time_step = client.time_step
    time_limit = client.time_range
    time_type = client.time_type
    eventCode = client.eventCode
    timestamp_start = client.time_one
    timestamp_stop = client.time_two + 86399
    time_days = (timestamp_stop + 1 - timestamp_start) / 86400
    # Dict to be returned
    response_dict = {
        'type': "bargraph_overall",
        'data': {
            'gates': [],
            'time_step': 86400,
            'time_start': timestamp_start
        },
        'between_days': True
    }

    response_dict['data']['loop'] = time_days

    x = 1

    while x <= gates_length:
        gates_list = []
        step_number = 1
        current_day_start = timestamp_start
        current_day_end = timestamp_start + 86399
        try:
            oldCount = int(query_range(current_day_start - 86399, current_day_start, client.eventCode, x, reverse=True))
        except IndexError:
            oldCount = 0
        while step_number <= time_days:
            try:
                newCount = int(day_total(eventCode, current_day_end, current_day_start, x))
                difference = newCount - oldCount
                gates_list.append(difference)
                print("Gate: " + str(x))
                print("New Count: " + str(newCount))
                print("Old Count: " + str(oldCount));
                oldCount = newCount
            except IndexError as ie:
                client.write_message({"error": "IndexError"})
                gates_list.append(0)
            current_day_start += 86400
            current_day_end += 86400
            step_number += 1
        response_dict['data']['gates'].append(gates_list)
        print("OVERALL: " + str(response_dict))
        x += 1
    return response_dict


def bar_init(delay1, delay2, client):
    x = 1
    gates_length = len(events[client.eventCode]['gates'])
    response_dict = {
        'type': "bargraph_range_data",
        'data': {}
    }
    timestamp_start = int(db.ashioto_events.find({
        "eventCode": client.eventCode
    })[0]['time_start'])

    time_difference = int((time.time() - timestamp_start) / 60)

    response_dict['data']['time_start'] = delay1
    response_dict['data']['time_stop'] = delay2
    response_dict['data']['gates'] = []
    gates_list = []
    while x <= gates_length:
        timestamp_range = time.time() - delay1
        timestamp_buffer = time.time() - delay2
        query_lower = "";
        try:
            query_lower = db.ashioto_data.find(
                {"eventCode": client.eventCode,
                 "gateID": x,
                 "timestamp":
                     {"$lt": timestamp_range}},
                {'_id': False, 'eventCode': False}
            ).sort([("timestamp", -1)]).limit(1)[0]

            query_upper = db.ashioto_data.find(
                {"eventCode": client.eventCode,
                 "gateID": x,
                 "timestamp":
                     {"$lt": timestamp_buffer}},
                {'_id': False, 'eventCode': False}
            ).sort([("timestamp", -1)]).limit(1)[0]

        except IndexError as error:
            client.write_message({
                'type': 'bargraph_data',
                'error': "Insufficient Data"
            })
            x += 1
            continue
        x += 1

        response_dict['data']['gates'].append({
            'last': query_lower,
            'secondLast': query_upper
        })
        print("RESPONSE: " + str(response_dict))
    return response_dict


def bar_overall(client):
    gates_length = len(events[client.eventCode]['gates'])
    time_step = client.time_step
    time_limit = client.time_range
    time_type = client.time_type
    eventCode = client.eventCode

    # Dict to be returned
    response_dict = {
        'type': "bargraph_overall",
        'data': {
            'gates': []
        }
    }
    response_dict['data']['time_step'] = time_step * 60

    # For finding event start time
    x = 1
    if time_type == "event":
        timestamp_start = int(db.ashioto_events.find({
            "eventCode": client.eventCode
        })[0]['time_start'])
        timestamp_stop = int(timestamp_start + time_step * 60)

    elif time_type == "current":
        timestamp_start = int(time.time() - time_step * 60 * time_limit)
        timestamp_stop = int(time.time())
        print("LIMIT: " + str(time_limit))
        print("START: " + str(timestamp_start))
        print("STOP: " + str(timestamp_stop))
    elif time_type == "day_one":
        timestamp_start = client.time_day
        timestamp_stop = timestamp_start + 86399
        time_limit = 24
    elif time_type == "day_between":
        timestamp_start = client.time_one
        timestamp_stop = client.time_two
        time_limit = int((timestamp_stop - timestamp_start) / 60)
        print("LIMIT: " + str(time_limit))
    response_dict['data']['time_start'] = timestamp_start
    timestamp_between = timestamp_start + (time_limit) * 3600
    timesToLoop = (time_limit) * 60 / time_step
    response_dict['data']['loop'] = timesToLoop

    # for fetching actual data
    z = 1
    while z <= gates_length:
        gates_list = []
        step_number = 1
        current_start = timestamp_start + time_step * 60
        current_stop = timestamp_stop
        try:
            oldCount = int(query_range(current_start - (time_step * 60), current_start, eventCode, z, reverse=True))
        except IndexError:
            oldCount = 0
        while step_number <= timesToLoop:
            try:
                newCount = int(query_range(current_start, current_stop, eventCode, z, reverse=False))
                difference = newCount - oldCount
                gates_list.append(difference)
                oldCount = newCount
            except IndexError as ie:
                client.write_message({"error": "IndexError"})
            current_start += time_step * 60
            # print("New Current Start: " + current_start)
            current_stop += time_step * 60
            # print("New Current Stop: " + current_stop)
            step_number += 1
            # print("Step: " + str(step_number))
        response_dict['data']['gates'].append(gates_list)
        print("OVERALL: " + str(response_dict))
        z += 1
    return response_dict
