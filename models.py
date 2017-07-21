
import requests

from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
from util import *

class Listing:
    def __init__(self, info):
        # url, price, location, kind, transit, bicycling
        self.info = info

    def from_url(db, url):
        results = db.search(Query().url == url)
        if len(results) > 0:
            print("CACHED: ", url)
            return Listing(results[0])
        print("SEARCHED: ", url)
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

    def search(self, start_index=0, max_listings=100):
        listings, done = [], False
        while len(listings) < max_listings:
            partial_listings = self.__search_page(start_index)
            start_index += len(partial_listings)
            listings += partial_listings
        return listings

    def __search_page(self, start_index=0):
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

    def retrieve_transit(self):
        return self.db.search(Query().transit.test(lambda val: val and int(val) <= 30))

    def retrieve_bicycling(self):
        return self.db.search(Query().bicycling.test(lambda val: val and int(val) <= 30))
