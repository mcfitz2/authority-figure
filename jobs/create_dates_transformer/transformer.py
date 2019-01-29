from pymongo import MongoClient, ReplaceOne, UpdateOne
import os, sys, time
import datetime

client = MongoClient(os.environ['MONGODB_URI']) 
queue = []
for collection in client['auth'].collection_names():
        print("Processing %s..." % collection)
        for document in client['auth'][collection].find({"created_date":{"$exists":False}}):
                ts = document['_id'].generation_time
                queue.append(UpdateOne({'_id':document['_id']}, {"$set":{"created_date":ts}}))
                if len(queue) > 50000:
                        client['auth'][collection].bulk_write(queue)
                        queue = []

        if len(queue) > 0:
                client['auth'][collection].bulk_write(queue)
                queue = []


