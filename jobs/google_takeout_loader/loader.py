import mailbox, json, sys, datetime, pprint, itertools, re, os, copy, requests, time
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne
from pymongo import MongoClient
import zipfile, tempfile


class LocationHistoryLoader:
	def __init__(self, db, takeout_path):
		self.collection = db['google_location_history']
		self.json_path = os.path.join(takeout_path, "Location History", "Location History.json")

	def grouper_it(self, n, iterable):
	    it = iter(iterable)
	    while True:
	        chunk_it = itertools.islice(it, n)
	        try:
	            first_el = next(chunk_it)
	        except StopIteration:
	            return
	        yield itertools.chain((first_el,), chunk_it)
	def run(self):
		with open(self.json_path, 'r') as f:
			print("Loading Location History")
			locations = json.load(f)
			total = len(locations['locations'])
			processed = 0
			for chunk in self.grouper_it(20000, locations['locations']):
				ops = [UpdateOne({'timestamp':datetime.datetime.fromtimestamp(int(loc['timestampMs'])/1000)},{"$setOnInsert":{"created_date":datetime.datetime.now()}, "$set":{'timestamp':datetime.datetime.fromtimestamp(int(loc['timestampMs'])/1000), 'heading':loc.get('heading', None), 'velocity':loc.get('velocity',None), 'altitude':loc.get('altitude', None), 'latitude':loc['latitudeE7']/10000000, 'longitude':loc['longitudeE7']/10000000}}, upsert=True) for loc in chunk]
				self.collection.bulk_write(ops)
				processed+=20000
				print('%d/%d' % (processed, total))

class MailLoader:
	def __init__(self, db, takeout_path):
		self.collection = db['location_history']
		self.db = db
		self.mbox_path = os.path.join(takeout_path, "Mail", "All mail Including Spam and Trash.mbox")
#		self.mbox_path = os.path.join(takeout_path, "Mail", "chunk_1.txt")
		self.airlines = ['United Airlines, Inc. <unitedairlines@united.com>', '"Southwest Airlines" <SouthwestAirlines@luv.southwest.com>', 'American Airlines <no-reply@notify.email.aa.com>']
	def objectify_message(self, msg):
		o_msg = dict([ (k.lower(), v) for (k,v) in msg.items() ])
		part = [p for p in msg.walk()][0]
		o_msg['contentType'] = part.get_content_type()
		o_msg['content'] = part.get_payload()
		return o_msg
	def grouper_it(self, n, iterable):
	    it = iter(iterable)
	    while True:
	        chunk_it = itertools.islice(it, n)
	        try:
	            first_el = next(chunk_it)
	        except StopIteration:
	            return
	        yield itertools.chain((first_el,), chunk_it)
	def run(self):
		print("Loading Mail")
		mbox = mailbox.mbox(self.mbox_path)
		queue = []
		for message in mbox:
#			print(message['From'], message['Subject'])
			if message['From'] in self.airlines:
				print('Found possible flight reservation', message['Subject'])
				existing = self.db['flights'].find_one({'message-id':message['Message-ID']})
				if not existing:
					payload = {'email':message.as_string(), 'mailbox_id':os.environ['TRAXO_MAILBOX_ID']}
					r = requests.post('https://api.traxo.com/v2/emails', headers={'client_id':os.environ['TRAXO_CLIENT_ID'], 'client_secret':os.environ['TRAXO_CLIENT_SECRET']}, json=payload)
					msg_id = r.json()['id']
					for i in range(10):
						r = requests.get('https://api.traxo.com/v2/emails/%s' % msg_id, params={'include':'results'}, headers={'client_id':os.environ['TRAXO_CLIENT_ID'], 'client_secret':os.environ['TRAXO_CLIENT_SECRET']}).json()
						if r['status'] == 'Processed':
							r['message-id'] = message['Message-ID']
							self.db['flights'].replace_one({'id':r['id']}, r, upsert=True)
							break
						else:
							time.sleep(5)

def extract():
	client = MongoClient(os.environ['MONGODB_URI'])
	db = client[os.environ['DB_NAME']]
	candidates = [file_path for file_path in os.listdir(os.environ['SEARCH_FOLDER']) if re.match('takeout-\d{8}T\d{6}Z-001.zip', file_path)]

	newest = None
	for c in candidates:
		timestamp = datetime.datetime.strptime(c.split('-')[1], '%Y%m%dT%H%M%SZ')
		if not newest or newest[1] < timestamp:
			newest = (c, timestamp)
	if newest:
		prefix = '-'.join(newest[0].split('-')[:2])
		to_unzip = [f for f in os.listdir(os.environ['SEARCH_FOLDER']) if re.match(prefix+'-\d{3}', f)]
		print(to_unzip)
		temp = tempfile.mkdtemp()
		for zip in to_unzip:
			z = zipfile.ZipFile(os.path.join(os.environ['SEARCH_FOLDER'], zip))
			z.extractall(path=temp)
		takeout_path = os.path.join(temp, 'Takeout')

#	takeout_path = os.path.join(os.environ['SEARCH_FOLDER'], 'Takeout')
#	mail_loader = MailLoader(db, takeout_path)
#	mail_loader.run()
	lh_loader = LocationHistoryLoader(db, takeout_path)
	lh_loader.run()





extract()
