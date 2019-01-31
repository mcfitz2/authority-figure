import os, datetime, pprint, time, sys
from pymongo import MongoClient, UpdateOne
import pymongo
client = MongoClient(os.environ['MONGODB_URI'])

print("Connected to DB")

client['core']['location'].create_index("timestamp")
last_run = list(client['auth']['transformer_runs'].find({'name':'location_transformer'}).sort([("timestamp",pymongo.DESCENDING)]).limit(1))
if last_run:
        last_run_date = last_run[0]['timestamp']
else:
        last_run_date = datetime.datetime(2000, 1, 1)
print(last_run_date)


this_run_date = datetime.datetime.now()-datetime.timedelta(minutes=5)
print(this_run_date)
g_location = client['auth']['google_location_history'].find({"created_date":{"$gte":last_run_date}})
o_location = client['auth']['owntracks_location_history'].find({"created_date":{"$gte":last_run_date}})

queue = []
for loc in g_location:
        del loc['created_date']
        del loc['_id']
        loc['grade'] = None
        queue.append(UpdateOne({"timestamp":loc["timestamp"]}, {"$set":loc, "$setOnInsert":{"created_date":datetime.datetime.now()}}, upsert=True))
        if len(queue) > 20000:
                client['core']['location'].bulk_write(queue)
                print("Upserted %d documents" % len(queue))
                queue = []

for loc in o_location:
        del loc['created_date']
        del loc['_id']
        loc['grade'] = None
        loc['velocity'] = None
        loc['heading'] = None
        loc['latitude'] = loc['loc']['coordinates'][0]
        loc['longitude'] = loc['loc']['coordinates'][1]
        loc['timestamp'] = loc['ts']
        del loc['ts']
        loc['altitude'] = loc.get('alt', None)
        try:
                del loc['alt']
        except KeyError:
                pass
        queue.append(UpdateOne({"timestamp":loc["timestamp"]}, {"$set":loc, "$setOnInsert":{"created_date":datetime.datetime.now()}}, upsert=True))
        if len(queue) > 20000:
                client['core']['location'].bulk_write(queue)
                print("Upserted %d documents" % len(queue))
                queue = []


if len(queue) > 0:
        client['core']['location'].bulk_write(queue)
        print("Upserted %d documents" % len(queue))


client['auth']['transformer_runs'].insert({"name":"location_transformer", "timestamp":this_run_date, "status":"success"})
