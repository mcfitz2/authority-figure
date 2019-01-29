from pymongo import MongoClient, ReplaceOne, UpdateOne
import os, sys, time



a_client = MongoClient(os.environ['MONGODB_URI'])
o_client = MongoClient(os.environ['OWNTRACKS_MONGO_URI'])




with o_client[os.environ['OWNTRACKS_DB']]['owntracks'].watch() as stream:
    for change in stream:
        print(change)
#queue = []
#for document in o_client[os.environ['OWNTRACKS_DB']]['owntracks'].find():
#        if len(queue) > 50000:
#                print("Writing %d objects" % len(queue))
#                a_client['auth']['owntracks_location_history'].bulk_write(queue)
#                queue = []
#        queue.append(UpdateOne({"_id":document['_id']}, {"$set":document}, upsert=True))
#
#print("Writing %d objects" % len(queue))
#a_client['auth']['owntracks_location_history'].bulk_write(queue)
