from queue import Queue
from threading import Thread
import os, datetime, pprint, time, sys, requests
from dateutil import parser
from pymongo import MongoClient, UpdateOne, InsertOne, ReplaceOne
client = MongoClient(os.environ['MONGODB_URI'])

services = client['auth']['services'].find({"name":"lastfm"})
client['auth']['lastfm_tracks'].create_index("timestamp")
#        client['auth']['fitbit_heart_series'].find_one_and_replace({"day":data['day']}, data, upsert=True)
base_url = "http://ws.audioscrobbler.com/2.0/"


class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                # An exception happened in this thread
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()

def load_tracks(tracks, service):
#        start = time.time()
        def process(track):
                track['dw_user_id'] = service['user']
                track['timestamp'] = int(track['date']['uts'])
#                print(track['date']['#text'], track['artist']['#text'], track['name'])
                return UpdateOne({"timestamp":int(track['date']['uts']), "dw_user_id":track['dw_user_id']}, {"$set":track}, upsert=True)
        ops = [process(track) for track in tracks]
        ret = client['auth']['lastfm_tracks'].bulk_write(ops).bulk_api_result
#        print(ret)
#        print("= Insert complete in %2.f seconds=" % (time.time() - start))







def process_page(options):
        def f(page):
                options['page'] = page
                start = time.time()
                result = requests.get(base_url, params=options).json()
                print("page %d retrieved in %.2f seconds" % (page, time.time()-start))
                #total_tracks += len(result['recenttracks']['track'])
                load_tracks(result['recenttracks']['track'], service)
                return result
        return f

pool = ThreadPool(20)

for service in services:
        print(service)
        options = {
                "method":"user.getrecenttracks",
                "user":service['service_user_id'],
                "api_key":os.environ['lastfm_client_id'],
                "format":"json",
                "limit":"200"
        }
        worker_func = process_page(options)
        result = worker_func(1)
        pages = range(2, int(result['recenttracks']['@attr']['totalPages']))
        print(result['recenttracks']['@attr'])
        pool.map(worker_func, pages)
        pool.wait_completion()
