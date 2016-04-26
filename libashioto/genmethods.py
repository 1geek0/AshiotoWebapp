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
def sendConfirmEmail(user_email, confirmCode):
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
    html = """\
        <html>
        <head></head>
        <body>
        <p>Hey,<br>
        Here is the confirmation <a href=http://""" + serverhost + ":8888" + """/confirm/""" + confirmCode + """>link</a></p></body></html>"""
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    yield smtp_client.send_message(msg)
    yield smtp_client.quit()


def generateConfirmCode():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
