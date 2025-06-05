import datetime
import time
import argparse
import browser_cookie3
import requests
import requests.cookies
import pprint
import pickle
from utils import *
from untislib import *
from enum import Enum

# SOME CLASSES


# Handling args
print('That tool allows you to search where a teacher is right now')
print('Before using this, you must open browser and login into webuntis')

arg_parser = argparse.ArgumentParser(description='Teacher Finder using data from Webuntis', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# arguments
arg_parser.add_argument('-c', '--clear-cache', help='Clears current cache', action='store_true')
arg_parser.add_argument('-B', '--browser', help='Browser that you use', type=str,
                        choices=[browser.value for browser in Browser],
                        default=Browser.FIREFOX.value)
arg_parser.add_argument('name', help='The name of the teacher to search for')
config = vars(arg_parser.parse_args())
print(config)
# exit(0)


# ==================================================== MAIN PART ===========================================
cache_live_time = 3600


# Load data
timetables = {}
classen = {}

cache_updated = False
# LOAD CLASSES
try:
    with open('saved_classen.pkl', 'rb') as f:
        classen = pickle.load(f)
    print(f'Cached {len(classen['data'])} classes found and loaded')

except FileNotFoundError:
    print('No classes saved. Loading...')
    classen['data'] = get_classes()
    classen['timestamp'] = time.time()
    cache_updated = True
    print(f'Loaded {len(classen['data'])} classes successfully')
if time.time() - classen['timestamp'] > cache_live_time:
    print('Cache expired')
    print('Loading new...')
    classen['data'] = get_classes()
    classen['timestamp'] = time.time()
    cache_updated = True
    print(f'Loaded {len(classen['data'])} classes successfully')

# LOAD TIMETABLES

def download_timetables():
    global cache_updated
    timetables['data'] = {}
    l = len(classen['data'])
    printProgressBar(0, l, prefix='Progress:', suffix='Complete', length=50)
    for i, c in enumerate(classen['data']):
        timetables['data'][c['id']] = get_timetable_for_week(c['id'])
        time.sleep(0.06)
        printProgressBar(i + 1, l, prefix='Progress:', suffix='Complete', length=50)
    timetables['timestamp'] = time.time()
    cache_updated = True
try:
    with open('saved_timetables.pkl', 'rb') as f:
        timetables = pickle.load(f)
    print(f'Cached {len(timetables['data'])} timetables found and loaded')
except FileNotFoundError:
    print('No timetable saved. Loading...')
    download_timetables()
    print(f'Loaded {len(timetables['data'])} timetables successfully')




if time.time() - timetables['timestamp'] > cache_live_time:
    print('Cache expired')
    download_timetables()
    print(f'Loaded {len(timetables['data'])} timetables successfully')

# Save cache if it was updated
if cache_updated:
    with open('saved_classen.pkl', 'wb') as f:
        pickle.dump(classen, f)
    with open('saved_timetables.pkl', 'wb') as f:\
        pickle.dump(timetables, f)

# PARSE DATA
teachers = []
for current_timetable in timetables['data'].values():
    periods = get_periods(current_timetable)
    untis_objects = get_untis_objects(current_timetable)
    for uo in untis_objects:
        print(uo)
        if uo.type == 2:
            teachers.append(uo.name)
    # for p in periods:
    #     print(p)
    # for o in untis_objects:
    #     print(o)

print(list(set(teachers)))