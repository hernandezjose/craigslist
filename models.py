
import datetime
import requests

from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
from util import *

class Listing:
    def __init__(self, info):
        # url, price, location, kind, transit, bicycling, posted, available
        self.info = info

    def is_nearby(self):
        if self.info['bicycling'] and self.info['bicycling'] <= 25:
            return True
        elif self.info['transit'] and self.info['transit'] <= 30:
            return True
        else:
            return False

    def is_recent(self, max_days_old=4):
        tokens = [int(tok) for tok in self.info['posted'].split()[0].split('-')]
        posted_date = datetime.date(tokens[0], tokens[1], tokens[2])
        delta = datetime.date.today() - posted_date
        return delta.days <= max_days_old

    def to_str(self):
        s = self.info['available'] + ', ' + self.info['url'] + ', ' + self.info['price']
        if self.info['bicycling'] and self.info['transit']:
            s += (', bicycling ' + str(self.info['bicycling']))
            s += (', transit ' + str(self.info['transit']))
        return s

    def from_url(db, url):
        results = db.search(Query().url == url)
        if len(results) > 0:
            return Listing(results[0])
        print("FETCHED: ", url)
        info = get_info_from_url(url)
        if 'location' in info and 'price' in info:
            info['transit'] = get_transit_time(info['location'])
            info['bicycling'] = get_bicycling_time(info['location'])
            info['stanford'] = get_stanford_time(info['location'])
        listing = Listing(info)
        db.insert(listing.info)
        return listing


class SearchEngine:
    def __init__(self, db):
        self.db = db
        self.base_url_apt = "https://sfbay.craigslist.org/search/apa"
        self.base_url_roo = "https://sfbay.craigslist.org/search/roo"

    def fetch(self, start_index=0, max_listings=100):
        listings, done = [], False
        while len(listings) < max_listings:
            partial_listings = self.__fetch_page(start_index)
            start_index += len(partial_listings)
            listings += partial_listings
        return listings

    def __fetch_page(self, start_index=0):
        payload = {'search_distance': 6,
                   'postal': 94103,
                   's': start_index,
                   'min_price': 500,
                   'max_price': 3000,
                   'min_bedrooms': 2,
                   'max_bedrooms': 3,
                   'min_bathrooms': 1,
                   'max_bathrooms': 3,
                   'availabilityMode': 0,
                   'format': 'rss'}
        resp_tuple = ('apt', requests.get(self.base_url_apt, params=payload))
        soup = BeautifulSoup(resp_tuple[1].content, 'lxml')
        urls = [r.find('dc:source').string for r in soup.find_all('item')]
        kind = resp_tuple[0]

        listings = []
        for i, url in enumerate(urls):
            listing = Listing.from_url(self.db, url)
            listings.append(listing)
        return listings

    def search(self):
        Info = Query()
        infos = self.db.search(Info.bicycling.exists() & Info.transit.exists())
        listings = [Listing(info) for info in infos]
        relevant = [l for l in listings if l.is_nearby() and l.is_recent()]
        return sorted(relevant, key=lambda l: l.info['transit'])
