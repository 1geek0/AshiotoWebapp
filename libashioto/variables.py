from pymongo import MongoClient

#MongoDB init
client = MongoClient(host="52.5.163.54",port=27017)
client.ashioto_data.authenticate("rest_user", "Ashioto_8192")
db = client.ashioto_data

#api keys
event_codes = []

events = {}
db_events = db.ashioto_events.find()
for event in db_events:
    event_codes.append(event['eventCode'])
    events[event['eventCode']] = event
client_dict = {} #Browser clients
bar_range_clients_dict = {} #Range Graph Clients
bar_overall_clients_dict = {} #Overall Graph Clients

# Email Vars
smpt_login = 'Welcome@ashioto.in'
smpt_password = 'Ashioto1024Welcome'

serverhost = 'localhost' #Server host