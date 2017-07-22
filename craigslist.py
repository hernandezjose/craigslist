import datetime
import time

from constants import *
from models import *
from tinydb import TinyDB
from util import send_email

db = TinyDB(DATABASE())
engine = SearchEngine(db)

for i in range(1):
    with open(LOGFILE(), 'a') as log:
        date = str(datetime.datetime.now())
        log.write(date + '\n')
        print ('\n====================', date, '====================\n')
    engine.fetch()
    listings = engine.search()
    urls = [l.info['url'] for l in listings]
    send_email('Craigslist apartments: ' + date, '\n'.join(urls))
    # time.sleep(PAUSE())

# send_email('Craigslist apartments: FINISHED', 'Start over!')
