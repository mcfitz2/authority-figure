import fitbit, pprint
import os, datetime, pprint, time, sys
from dateutil import parser
from pymongo import MongoClient
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
client = MongoClient(os.environ['MONGODB_URI'])

logging.info("Connected to DB")
def refresh_token(token):
        client['auth']['services'].find_one_and_update({"name":"fitbit"}, {"$set":{"access_token":token['access_token'], "refresh_token":token['refresh_token']}})
        logging.info("Refreshed token")

def buildDateList(start, end):
        delta = end - start
        return [(start + datetime.timedelta(i)).replace(hour=0, minute=0, second=0, microsecond=0) for i in range(delta.days + 1)]



def puller(dl, func, service, fb):
        for d in dl:
                if d.date() == datetime.datetime.today().date():
                        continue
                logging.info("%s %s %s %s" % (service['name'], repr(func), service['user'], d))
                while True:
                        try:
                                func(d, service, fb)
                                break
                        except fitbit.exceptions.HTTPTooManyRequests as e:
                                logging.info("hit rate limit, waiting %s seconds" % (e.retry_after_secs))
                                if os.environ['BREAK_ON_TOOMANY'] == 'true':
                                        logging.info("Canceling...")
                                        return True
                                else:
                                        time.sleep(e.retry_after_secs)
        return False
def missing_days(collection, service, fb):
        user = client['auth']['fitbit_user'].find_one({'dw_user_id':service['user']})
        days_in_db = [i['day'] for i in client['auth'][collection].find({}, projection=['day'])]
        if not user:
                user = fb.user_profile_get()['user']
                user['dw_user_id'] = service['user']
                client['auth']['fitbit_user'].find_one_and_update({'encodedId':user['encodedId']}, {"$set":user}, upsert=True)
        logging.info("getting missing days for %s" % (collection))
        logging.info("days in db: %d" % (len(days_in_db)))
        join_date = parser.parse(user['memberSince'])
        days_since_joining = buildDateList(join_date, datetime.datetime.today())
        days_to_pull = list(set(days_since_joining).difference(days_in_db))
        logging.info("join date: %s" % (join_date))
        logging.info("days to pull: %s" % (len(days_to_pull)))
        return days_to_pull
def heart_series(d, service, fb):
        data = fb.intraday_time_series('activities/heart', base_date=d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_heart_series'].find_one_and_update({"day":data['day']}, {"$set":data}, upsert=True)
def calories_series(d, service, fb):
        data = fb.intraday_time_series('activities/calories', base_date=d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_calories_series'].find_one_and_update({"day":data['day']}, {"$set":data}, upsert=True)

def steps_series(d, service, fb):
        data = fb.intraday_time_series('activities/steps', base_date=d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_steps_series'].find_one_and_update({"day":data['day']}, {"$set":data}, upsert=True)

def distance_series(d, service, fb):
        data = fb.intraday_time_series('activities/distance', base_date=d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_distance_series'].find_one_and_update({"day":data['day']}, {"$set":data}, upsert=True)

def floors_series(d, service, fb):
        data = fb.intraday_time_series('activities/floors', base_date=d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_floors_series'].find_one_and_update({"day":data['day']}, {"$set":data}, upsert=True)

def bmi_series(d, service, fb):
        data = fb.intraday_time_series('body/bmi', base_date=d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_bmi_series'].find_one_and_update({"day":data['day']}, {"$set":data}, upsert=True)

def weight_series(d, service, fb):
        data = fb.intraday_time_series('body/weight', base_date=d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_weight_series'].find_one_and_update({"day":data['day']}, {"$set":data}, upsert=True)

def fat_series(d, service, fb):
        data = fb.intraday_time_series('body/fat', base_date=d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_fat_series'].find_one_and_update({"day":data['day']}, {"$set":data}, upsert=True)
def sleep(d, service, fb):
        data = fb.sleep(d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_sleep'].find_one_and_update({'day':data['day']}, {"$set":data}, upsert=True)
def bp(d, service, fb):
        data = fb.bp(d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_bp'].find_one_and_update({'day':data['day']}, {"$set":data}, upsert=True)
def activities(d, service, fb):
        data = fb.activities(date=d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_activities'].find_one_and_update({'day':data['day']}, {"$set":data}, upsert=True)
def foods_log_water(d, service, fb):
        data = fb.foods_log_water(date=d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_foods_log_water'].find_one_and_update({'day':data['day']}, {"$set":data}, upsert=True)
def foods_log(d, service, fb):
        data = fb.foods_log(date=d)
        data['dw_user_id'] = service['user']
        data['day'] = d
        client['auth']['fitbit_foods_log'].find_one_and_update({'day':data['day']}, {"$set":data}, upsert=True)

def collect():
        services = client['auth']['services'].find({"name":"fitbit"})
        for service in services:
                logging.info("Collecting data for %s" % (service['user']))
                fb = fitbit.Fitbit(os.environ['fitbit_client_id'], os.environ['fitbit_client_secret'], access_token=service['access_token'], refresh_token=service['refresh_token'], refresh_cb=refresh_token)
                r = puller(missing_days('fitbit_heart_series', service, fb), heart_series, service, fb)
                if r: return
                r = puller(missing_days('fitbit_steps_series', service, fb), steps_series, service, fb)
                if r: return
                r = puller(missing_days('fitbit_distance_series', service, fb), distance_series, service, fb)
                if r: return
                r = puller(missing_days('fitbit_floors_series', service, fb), floors_series, service, fb)
                if r: return
                r = puller(missing_days('fitbit_bmi_series', service, fb), bmi_series, service, fb)
                if r: return
                r = puller(missing_days('fitbit_weight_series', service, fb), weight_series, service, fb)
                if r: return
                r = puller(missing_days('fitbit_calories_series', service, fb), calories_series, service, fb)
                if r: return
                r = puller(missing_days('fitbit_activities', service, fb), activities, service, fb)
                if r: return
                r = puller(missing_days('fitbit_sleep', service, fb), sleep, service, fb)
                if r: return
                r = puller(missing_days('fitbit_bp', service, fb), bp, service, fb)
                if r: return
                r = puller(missing_days('fitbit_foods_log_water', service, fb), foods_log_water, service, fb)
                if r: return
                r = puller(missing_days('fitbit_foods_log', service, fb), foods_log, service, fb)
                if r: return


logging.info("Starting")
collect()
