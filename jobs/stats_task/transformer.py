from pymongo import MongoClient, ReplaceOne, UpdateOne
import os, sys, time
import datetime

client = MongoClient(os.environ['MONGODB_URI']) 
print("calculating  stats")
inserted_last24 = [(collection, client['auth'][collection].count_documents({"created_date":{"$gt":datetime.datetime.now() - datetime.timedelta(days=1)}})) for collection in client['auth'].list_collection_names()]
inserted_lastweek = [(collection, client['auth'][collection].count_documents({"created_date":{"$gt":datetime.datetime.now() - datetime.timedelta(days=7)}})) for collection in client['auth'].list_collection_names()]
client['auth']['stats'].update_one({},  {"$set":{"inserts":{"last_day":{"total":sum([i[1] for i in inserted_last24]), "by_collection":inserted_last24}, "last_week":{"total":sum([i[1] for i in inserted_lastweek]), "by_collection":inserted_lastweek}}, "updated_date": datetime.datetime.now()}}, upsert=True)
