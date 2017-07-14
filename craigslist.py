
import constants

from models import *
from tinydb import TinyDB


db = TinyDB(DATABASE)

engine = SearchEngine(db)
listings = engine.search()
