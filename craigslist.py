import datetime
import time

from constants import Constants
from models import *
from tinydb import TinyDB

db = TinyDB(Constants.DATABASE())
engine = SearchEngine(db)

while True:
    time.sleep(Constants.PAUSE())
    with open(Constants.LOGFILE(), 'a') as log:
        date = str(datetime.datetime.now())
        log.write(date + '\n')
        print ('\n====================', date, '====================\n')
    listings = engine.search()
