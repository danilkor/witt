#!/usr/bin/python3
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
import os


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
arg_parser.add_argument('-t', '--timetable', action='store_true', help='Show timetable instead of current subject')
arg_parser.add_argument('-d', '--date', help='Date to get timetable for. Only works with timetable option true')
config = vars(arg_parser.parse_args())

# ==================================================== BEFORE START ========================================
# clear cache if in config
if config['clear_cache']:
    os.remove('saved_timetables.pkl')
    os.remove('saved_classen.pkl')


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

# parse data
all_periods = []
all_uobjects = []
for current_timetable in timetables['data'].values():
    periods = get_periods(current_timetable)
    for period in periods:
        all_periods.append(period)
    untis_objects = get_untis_objects(current_timetable)
    for untis_object in untis_objects:
        all_uobjects.append(untis_object)

#Parse all teachers
searched_teacher = None
for uo in all_uobjects:
    if uo.type == 2:
        if uo.name.lower() == config['name'].lower():
            searched_teacher = uo
            print(f'Found {uo.name}')

#Find all periods for this teacher
found_periods = []
for period in all_periods:
    for element in period.objects:
        if element['type'] == 2 and element['id'] == searched_teacher.id:
            found_periods.append(period)
# Sort them
sorted_periods = sorted(found_periods, key=lambda period: period.date)

if config['timetable']:
    print('========================================')
    for period in sorted_periods:
        print(format_datetime_range(str(period)))
        for object in period.objects:
            print(find_object_by_id(all_uobjects, object['id']))
        print('======================================')
