import datetime
import time
import argparse
import browser_cookie3
import requests
import requests.cookies
import pprint
import pickle
from utils import *
from enum import Enum

server = 'melete.webuntis.com' # e.g., klio.webuntis.com
# Define the Browser Enum
class Browser(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    OPERA = "opera"
    BRAVE = "brave"
    VIVALDI = "vivaldi"
    LIBREWOLF = "librewolf"
    LYNX = "lynx"
    W3M = "w3m"
    ARC = "arc"

class UntisObject:
    def __init__(self, type: int, id: int, name, longname = ''):
        self.type = type
        self.id = id
        self.name = name
        self.longname = longname if longname is not None else ''

    def __str__(self):
        return f'{self.type}-{self.id}: {self.name}, {self.longname}'
class Period:
    def __init__(self, date, start_time, end_time):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.objects = []

    def add_element(self, element: dict):
        self.objects.append(element)

    def __str__(self):
        return f'{self.date}-{self.start_time}-{self.end_time}'
def get_webuntis_cookies() -> dict:
    # Get all Firefox cookies
    all_cookies = browser_cookie3.firefox()
    # Specify the domain you want (e.g., 'example.com')
    target_domain = 'webuntis.com'
    # Filter cookies for the specific domain
    filtered_cookies = requests.cookies.RequestsCookieJar()
    for cookie in all_cookies:
        if target_domain in cookie.domain:
            filtered_cookies.set(
                cookie.name,
                cookie.value,
                domain=cookie.domain,
                path=cookie.path,
                secure=cookie.secure,
                expires=cookie.expires
            )
    # pprint.pprint(filtered_cookies.items())
    dict_cookies = {}
    for cookie in filtered_cookies.items():
        dict_cookies[cookie[0]] = cookie[1]
    return dict_cookies
cookies = get_webuntis_cookies()
def webuntis_jsonrpc_do_request(method, params):
    url = f'https://{server}/WebUntis/jsonrpc.do'
    payload = {
        'id': f'req-{method}-{int(time.time())}',
        'method': method,
        'params': params,
        'jsonrpc': '2.0'
    }
    try:
        response = requests.post(url, cookies=cookies, json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get('id') != payload['id']:
            raise Exception(f"Request ID mismatch: sent {payload['id']}, received {data.get('id')}")
        if 'error' in data:
            print(data['error']['message'])
            raise Exception(f"API Error: {data['error']['message']}")
        return data['result']
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
def get_classes():
    return webuntis_jsonrpc_do_request('getKlassen', {})
def get_timetable_for_week(class_id: int):
    url = f'https://melete.webuntis.com/WebUntis/api/public/timetable/weekly/data?elementType=1&elementId={class_id}&date={datetime.date.today()}'
    try:
        response = requests.get(url, cookies=cookies)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            print(data['error']['message'])
            raise Exception(f"API Error: {data['error']['message']}")
        return data['data']['result']['data']
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
def get_untis_objects(timetable) -> list:
    elements = timetable['elements']
    objects = []
    for element in elements:
        objects.append(UntisObject(element['type'], element['id'], element['name'], element.get('longName')))
    return objects
def get_periods(timetable) -> list:
    element_periods = timetable['elementPeriods'][str(timetable['elementIds'][0])]
    periods = []
    for element in element_periods:
        period = Period(element['date'], element['startTime'], element['endTime'])
        for e in element['elements']:
            new_element = {
                'type': e['type'],
                'id': e['id'],
            }
            period.add_element(new_element)
        periods.append(period)
    return periods