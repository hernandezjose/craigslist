import datetime
import requests
import smtplib
import time

from bs4 import BeautifulSoup
from constants import *


def addr_from_maps_url(maps_url):
    prefixes = ['https://maps.google.com/?q=loc%3A+',
                'https://maps.google.com/maps/preview/@']
    if maps_url.startswith(prefixes[0]):
        return maps_url.split(prefixes[0])[1]
    elif maps_url.startswith(prefixes[1]):
        return ','.join(maps_url.split(prefixes[1])[1].split(',')[0:2])

def get_stanford_time(maps_url):
    address = addr_from_maps_url(maps_url)
    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/xml'
    payload = {'origins': address,
               'destinations': 'Palo+Alto+Transit+Center',
               'mode': 'transit',
               'key': API_KEY()}
    resp = requests.get(base_url, params=payload)
    soup = BeautifulSoup(resp.content, 'lxml')
    if soup.find('text') == None:
        return None
    return get_time_in_mins(soup.find('text').string)

def get_transit_time(maps_url):
    address = addr_from_maps_url(maps_url)
    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/xml'
    payload = {'origins': address,
               'destinations': 'Airbnb+HQ',
               'mode': 'transit',
               'key': API_KEY()}
    resp = requests.get(base_url, params=payload)
    soup = BeautifulSoup(resp.content, 'lxml')
    if soup.find('text') == None:
        return None
    return get_time_in_mins(soup.find('text').string)

def get_bicycling_time(maps_url):
    address = addr_from_maps_url(maps_url)
    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/xml'
    payload = {'origins': address,
               'destinations': 'Airbnb+HQ',
               'mode': 'bicycling',
               'key': API_KEY()}
    resp = requests.get(base_url, params=payload)
    soup = BeautifulSoup(resp.content, 'lxml')
    if soup.find('text') == None:
        return None
    return get_time_in_mins(soup.find('text').string)

def get_time_in_mins(time_str):
    tokens = time_str.split(' ')
    mins = 0
    if not tokens[-1].startswith('min'):
        return 240 # random big number
    if tokens[-1].startswith('min'):
        mins += int(tokens[-2])
    if len(tokens) > 2 and tokens[-3].startswith('hour'):
        mins += int(tokens[-4]) * 60
    return mins

def get_info_from_url(url):
    time.sleep(3)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    kind = url.split('craigslist.org/')[1][4:7]
    title = soup.find('title')
    location = soup.find('p', class_='mapaddress')
    price = soup.find('span', class_='price')
    posted = soup.find('time', class_='timeago')
    available = soup.find('span', class_='housing_movein_now')
    info = {'url': url, 'kind': kind}
    if title:
        info['title'] = title.string
    if location:
        info['location'] = location.find('a')['href']
    if price:
        info['price'] = price.string
    if available:
        info['available'] = available.string
    if posted:
        info['posted'] = posted.string
    return info

def send_email(subject, body):
    tokens = list()
    tokens.append('From: ' + FROM_EMAIL())
    tokens.append('To: ' + TO_EMAIL())
    tokens.append('Subject: ' + subject)
    tokens.append('')
    tokens.append(body)
    msg = '\r\n'.join(tokens)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(FROM_EMAIL(), PASSWORD())
    server.sendmail(FROM_EMAIL(), TO_EMAIL(), msg)
    server.quit()
