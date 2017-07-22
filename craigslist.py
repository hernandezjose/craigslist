import datetime
import time

from constants import *
from models import *
from tinydb import TinyDB

db = TinyDB(DATABASE())
engine = SearchEngine(db)

while True:
    with open(LOGFILE(), 'a') as log:
        date = str(datetime.datetime.now())
        log.write(date + '\n')
        print ('\n====================', date, '====================\n')
    listings = engine.search()
    time.sleep(PAUSE())
