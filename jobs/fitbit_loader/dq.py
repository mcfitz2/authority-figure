import os
import fitbit
import os, datetime, pprint, time, sys
from dateutil import parser
from pymongo import MongoClient

client = MongoClient(os.environ['MONGODB_URI'])

print("Connected to DB")
def refresh_token(token):
        client['auth']['services'].find_one_and_update({"name":"fitbit"}, {"$set":{"access_token":token['access_token'], "refresh_token":token['refresh_token']}})
        print("Refreshed token")
def buildDateList(start, end):
        delta = end - start
        return [(start + datetime.timedelta(i)).replace(hour=0, minute=0, second=0, microsecond=0) for i in range(delta.days + 1)]

def stats(collection, service, fb):
        user = client['auth']['fitbit_user'].find_one({'dw_user_id':service['user']})
        days_in_db = [i['day'] for i in client['auth'][collection].find({}, projection=['day'])]
        join_date = parser.parse(user['memberSince'])
        days_since_joining = buildDateList(join_date, datetime.datetime.today())
        days_to_pull = list(set(days_since_joining).difference(days_in_db))
        print("=======================")
        print(collection)
        print("days in db: %d" % len(days_in_db))
        print("days since joining: %d" % len(days_since_joining))
        print("days to pull: %d" % len(days_to_pull))
        print("%.1f complete" % (((float((len(days_since_joining)-len(days_to_pull)-1)))/len(days_since_joining))*100))
        dq_c = {"dw_user_id":service["user"], "collection":collection, "records_in_db":len(days_in_db), "max_record_count":len(days_since_joining)-1} 
        client['auth']['data_completeness'].find_one_and_replace({"collection":collection, "dw_user_id":service["user"]}, dq_c, upsert=True)

services = client['auth']['services'].find({"name":"fitbit"})
for service in services:
    print("Collecting data for", service['user'])
    fb = fitbit.Fitbit(os.environ['fitbit_client_id'], os.environ['fitbit_client_secret'], access_token=service['access_token'], refresh_token=service['refresh_token'], refresh_cb=refresh_token)
    stats('fitbit_heart_series', service, fb)
    stats('fitbit_steps_series', service, fb)
    stats('fitbit_distance_series', service, fb)
    stats('fitbit_floors_series', service, fb)
    stats('fitbit_bmi_series', service, fb)
    stats('fitbit_weight_series', service, fb)
    stats('fitbit_calories_series', service, fb)
    stats('fitbit_activities', service, fb)
    stats('fitbit_sleep', service, fb)
    stats('fitbit_bp', service, fb)
    stats('fitbit_foods_log_water', service, fb)
    stats('fitbit_foods_log', service, fb)
