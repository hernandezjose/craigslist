
import requests

from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
from util import *

class Listing:
    def __init__(self, info):
        # url, price, location, kind, transit, bicycling
        self.info = info

    def from_url(db, url, kind):
        results = db.search(Query().url == url)
        if len(results) > 0:
            print("CACHED: ", url)
            return Listing(results[0]), True
        print("SEARCHED: ", url)
        info = dict()
        info['url'], info['kind'] = url, kind
        info['location'], info['price'] = get_location_and_price_from_url(url)
        if info['location'] == None or info['price'] == None:
            return None, False
        info['transit'] = get_transit_time(info['location'])
        info['bicycling'] = get_bicycling_time(info['location'])
        listing = Listing(info)
        db.insert(listing.info)
        return listing, False


class SearchEngine:
    def __init__(self, db):
        self.db = db
        self.base_url_apt = "https://sfbay.craigslist.org/search/apa"
        self.base_url_roo = "https://sfbay.craigslist.org/search/roo"

    def search_all(self, max_listings=100):
        listings, start_index, done = [], 0, False
        while not done and len(listings) < max_listings:
            partial_listings, done = self.search(start_index)
            start_index += len(partial_listings)
            listings += [l for l in partial_listings if l]
        return listings

    def search(self, start_index=0):
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
        num_cached = 0
        max_num_cached = 5
        for i, url in enumerate(urls):
            listing, cached = Listing.from_url(self.db, url, kind)
            listings.append(listing)
            if (len(urls) - max_num_cached) <= i and cached:
                num_cached += 1
        return listings, (max_num_cached <= num_cached + 1)
