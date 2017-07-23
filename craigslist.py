import datetime
import time

from constants import *
from models import *
from tinydb import TinyDB
from util import send_email

db = TinyDB(DATABASE())
engine = SearchEngine(db)

while True:
    date = str(datetime.datetime.now())
    print ('\n', '====================', date, '====================')
    print ('\n', 'Fetching ...')
    engine.fetch()
    print ('\n', 'Searching ...')
    listings = engine.search()
    infos = [l.to_str() for l in listings]
    print ('\n', 'Emailing ...')
    send_email('Craigslist apartments: ' + date, '\n'.join(infos))
    print ('\n', 'Done!', '\n')
    time.sleep(PAUSE())
