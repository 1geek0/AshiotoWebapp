import random
import string

from tornado.gen import coroutine
from tornado_smtp.client import TornadoSMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from libashioto.variables import *


# Returns total count of all the gates in the gates' list provided
def total(gates):
    total_counts = 0
    for gate in gates:
        total_counts += int(gate['count'])
    return total_counts


# Returns latest counts at all gates with last sync time and name of each gate
def gates_top(event_code, start_time):
    event_request = events[event_code]

    gates_number = len(event_request['gates'])
    gates = []
    mega = 0
    i = 1
    while i <= gates_number:
        query = db.ashioto_data.find(
            {"eventCode": event_code,
             "gateID": i, "timestamp": {"$gte": start_time}}).sort([("timestamp", -1)]).limit(1)
        count = 0
        last = 0
        for item in query:
            count = item['outcount']
            mega += count
            last = item['timestamp']

        index = i - 1

        gates.append({
            "name": str(events[event_code]['gates'][index]['name']),
            "count": int(count),
            "last_sync": int(last) + 19800
        })
        i += 1
    response = {
        'Gates': gates
    }
    return response


@coroutine
def sendConfirmEmail(user_email, password):
    print('Sending Email')
    smtp_client = TornadoSMTP('smtp.mailgun.org')
    yield smtp_client.starttls()
    yield smtp_client.login(smpt_login, smpt_password)

    # MIME Generation
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your Key To Ashioto!"
    msg['From'] = smpt_login
    msg['To'] = user_email

    # Email Body
    text = "This is an email to activate your Ashioto Analytics account"
    html = '''\
        <html>
        <head></head>
        <body>
        <p>Hey,<br>
        Your account for Ashioto analytics has been created.<br>
        Your password is: ''' + password + '''<br>
        If any assistance is needed, please contact geek@ashioto.in<br>
        Proceed to Ashioto dashboard by logging in : <a href=http://''' + serverhost + '''/login>Log in</a></body></html>'''
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    yield smtp_client.send_message(msg)
    yield smtp_client.quit()


def generateConfirmCode():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


def showDashboard(user, event_requested):
    start_time = db.ashioto_events.find({"eventCode": event_requested})[0]['time_start']
    name = events[event_requested]['event_name']
    theme_primary = events[event_requested]['theme_primary']
    theme_accent = events[event_requested]['theme_accent']
    theme_text = events[event_requested]['theme_text']
    logo = events[event_requested]['logo_name']
    background = events[event_requested]['background']
    call = gates_top(event_requested, start_time)
    all_gates = call['Gates']
    realtime = events[event_requested]['realtime']
    total_count = total(all_gates)
    size = 6
    if len(all_gates) == 1:
        size = 12
    user.render(
        "../templates/template_dashboard.html",
        event_title=name,
        total_count=total_count,
        gates=all_gates,
        size=size,
        theme_primary=theme_primary,
        theme_accent=theme_accent,
        theme_text=theme_text,
        eventCode=event_requested,
        logo_name=logo,
        background=background,
        realtime=realtime)

def showRally(user, event_requested):
    start_time = db.ashioto_events.find({"eventCode": event_requested})[0]['time_start']
    name = events[event_requested]['event_name']
    theme_primary = events[event_requested]['theme_primary']
    theme_accent = events[event_requested]['theme_accent']
    theme_text = events[event_requested]['theme_text']
    logo = events[event_requested]['logo_name']
    background = events[event_requested]['background']
    call = gates_top(event_requested, start_time)
    all_gates = call['Gates']
    realtime = events[event_requested]['realtime']
    total_count = total(all_gates)

    tapovanCount = int(4.5*(all_gates[0]['count'] + all_gates[1]['count']))
    tapovanLatest = max(all_gates[0]['last_sync'], all_gates[1]['last_sync'])

    rkCount = int(4.5*all_gates[2]['count'])
    rkLatest = all_gates[2]['last_sync']
    size = 6
    if len(all_gates) == 1:
        size = 12
    user.render(
        "../templates/template_mrally.html",
        event_title=name,
        total_count=total_count,
        gates=all_gates,
        tapovanCount=tapovanCount,
        tapovanLatest=tapovanLatest,
        rkCount=rkCount,
        rkLatest=rkLatest,
        size=size,
        theme_primary=theme_primary,
        theme_accent=theme_accent,
        theme_text=theme_text,
        eventCode=event_requested,
        logo_name=logo,
        background=background,
        realtime=realtime)

#Give a list of names of all the public events
def listEvents():
    events_dict = {}
    events_list = []
    events_db = db.ashioto_events.find({}, {"eventCode": 1, "_id": 0})
    x = 0
    for event in events_db:
        events_list.append(event['eventCode'])
    events_dict['Events'] = events_list
    return events_dict

def confirmUser(code):
    try:
        db.ashioto_users.update(
            {'tempCode': code},
            {'$unset': {'tempCode': ''}, '$set': {'state': 'active'}},
            False)
        return True
    except IndexError:
        return False
