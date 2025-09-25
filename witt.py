#!/usr/bin/env python
import datetime
import time
import argparse
import pickle
from utils import *
from untislib import *
import os
import untislib
from types import SimpleNamespace
import webbrowser

# =================================================== CONFIG =================================================
# Cache live time in seconds
cache_live_time = 3600
teacher_name_live_time = 360 * 24 * 60 # 60 days

# save files 
cache_directory = os.path.expanduser("~") + "/.cache/witt"
filenames = SimpleNamespace(
    timetables=f'{cache_directory}/saved_timetables.pkl',
    classen=f'{cache_directory}/saved_classes.pkl',
    teacher_full_names=f'{cache_directory}/saved_teacher_full_names.pkl'
)







# Handling args
arg_parser = argparse.ArgumentParser(description='Teacher Finder using data from Webuntis', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# arguments
arg_parser.add_argument('-C', '--clear-cache', help='Clears current cache', action='store_true')
arg_parser.add_argument('-t', '--timetable', action='store_true', help='Show timetable instead of current subject')
arg_parser.add_argument('-r', '--rooms', action='store_true', help='Show the room too (only works with --timetable)')
arg_parser.add_argument('-l', '--list-teachers', action='store_true', help='See a list of available teachers (Only short form)')
arg_parser.add_argument('-f', '--full', action='store_true', help='Show full names of teachers (Only works with --list-teachers)')
arg_parser.add_argument('-B', '--browser', help='Browser that you use', type=str,
                        choices=[browser.value for browser in Browser],
                        default=Browser.FIREFOX.value)
arg_parser.add_argument('-d', '--date', help='Date to get timetable for. Only works with timetable option true. Enter like YYYYMMDD. Notice, that cache will be cleared if this date is not found')
arg_parser.add_argument('-n', '--name', help='The name of the teacher to search for')
arg_parser.add_argument('-cn', '--classname', help='The name of the class to search for')
arg_parser.add_argument('-s', '--super-speed', action='store_true', help='Use this if you want to try fast load. May cause problems')
config = vars(arg_parser.parse_args())
# ==================================================== BEFORE START ========================================
# If config directory does not exist, create it
if not os.path.exists(cache_directory):
    os.makedirs(cache_directory)

# clear cache if in config
if config['clear_cache']:
    os.remove(filenames.timetables) if os.path.exists(filenames.timetables) else None
    os.remove(filenames.classen) if os.path.exists(filenames.classen) else None
    os.remove(filenames.teacher_full_names) if os.path.exists(filenames.teacher_full_names) else None
    print('Cache cleared')

if config['date']:
    if not validate_date(config['date']):
        print('Date must be in format YYYYMMDD')
        exit(1)
    untislib.date_to_look = f"{config['date'][:4]}-{config['date'][4:6]}-{config['date'][6:8]}"

# Check if authenticated
try:
    get_classes()
except Exception as e:
    print('Not authenticated. Browser will open, please login there, then try again')
    time.sleep(2)
    webbrowser.open("https://melete.webuntis.com/WebUntis/?school=htl-hl#/basic/login")
    exit(1)


# ==================================================== MAIN PART ===========================================







# Load data
timetables = {}
classen = {}
teachers = {}


cache_updated = False
# LOAD CLASSES
try:
    with open(filenames.classen, 'rb') as f:
        classen = pickle.load(f)
    print(f'Cached {len(classen['data'])} classes found and loaded')

except Exception:
    print('No classes saved. Loading...')
    classen['data'] = get_classes()
    classen['timestamp'] = time.time()
    cache_updated = True
    print(f'Loaded {len(classen['data'])} classes successfully')
if time.time() - classen['timestamp'] > cache_live_time:
    print('Classes cache expired')
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
        if not config['super_speed']:
            time.sleep(0.06)
        printProgressBar(i + 1, l, prefix='Progress:', suffix='Complete', length=50)
    timetables['timestamp'] = time.time()
    cache_updated = True
try:
    with open(filenames.timetables, 'rb') as f:
        timetables = pickle.load(f)
    print(f'Cached {len(timetables['data'])} timetables found and loaded')
except Exception:
    print('No timetable saved. Loading...')
    download_timetables()
    print(f'Loaded {len(timetables['data'])} timetables successfully')
if time.time() - timetables['timestamp'] > cache_live_time:
    print('Timetables cache expired')
    download_timetables()
    print(f'Loaded {len(timetables['data'])} timetables successfully')

# LOAD TEACHER FULL NAMES

try:
    with open(filenames.teacher_full_names, 'rb') as f:
        teachers = pickle.load(f)
    print(f'Cached {len(teachers['data'])} teacher full names found `and loaded')
except Exception:
    print('No teacher full names saved. Loading...')
    teachers['data'] = get_teacher_full_names()
    teachers['timestamp'] = time.time()
    cache_updated = True
    print(f'Loaded {len(teachers['data'])} teacher full names successfully')
if time.time() - teachers['timestamp'] > teacher_name_live_time:
    print('Teacher full names cache expired')
    print('Loading new...')
    teachers['data'] = get_teacher_full_names()
    teachers['timestamp'] = time.time()
    cache_updated = True
    print(f'Loaded {len(teachers['data'])} teacher full names successfully')

# Save cache if it was updated
if cache_updated:
    with open(filenames.classen, 'wb') as f:
        pickle.dump(classen, f)
    with open(filenames.timetables, 'wb') as f:\
        pickle.dump(timetables, f)
    with open(filenames.teacher_full_names, 'wb') as f:
        pickle.dump(teachers, f)

# PARSE DATA

# parse data
all_periods = []
all_uobjects = []
def parse_periods_and_uobjects():
    global all_periods, all_uobjects
    for current_timetable in timetables['data'].values():
        periods = get_periods(current_timetable)
        for period in periods:
            all_periods.append(period)
        untis_objects = get_untis_objects(current_timetable)
        for untis_object in untis_objects:
            all_uobjects.append(untis_object)
parse_periods_and_uobjects()
# look if the date is in the periods, otherwise load other timetable
date_that_must_be_here = date_to_look.replace('-', '')[:8]
if config['date']:
    date_that_must_be_here = config['date']
date_exists = False
for period in all_periods:
    if str(period.date) == date_that_must_be_here:
        date_exists = True
        break
if not date_exists:
    print('Date was not found in cache, downloading new one')
    download_timetables()
    with open(filenames.timetables, 'wb') as f:\
        pickle.dump(timetables, f)
    parse_periods_and_uobjects()

# Print a list of teachers
teacher_list = []
teachers_names = []
for uo in all_uobjects:
    if uo.type == 2 and uo.name not in teachers_names:
        teacher_list.append(uo)
        teachers_names.append(uo.name)
if config['list_teachers'] and not config['full']:
    print('Available teachers:')
    sorter_teacher_list = sorted(teacher_list, key=lambda x: x.name)
    for teacher in sorter_teacher_list:
        print(teacher.name, end=', ')
    print()
if config['list_teachers'] and config['full']:
    print('Available teachers (Full names):')
    sorter_teacher_list = sorted(teacher_list, key=lambda x: x.name)
    for teacher in sorter_teacher_list:
        full_name = next((t['teacherFullName'] for t in teachers['data'] if f'({teacher.name})' in str(t['teacher'])), None)
        if full_name:
            print(f'{teacher.name} - {full_name}')
        else:
            print(f'{teacher.name} - No full name found')
    print()



# Check if name is given
if not config['name'] and not config['classname']:
    print('No name or classname given')
    exit(0)
if config['name'] and config['classname']:
    print('You can only search for a teacher or a class, not both at the same time')
    exit(0)


#Find the looked teacher or class
found_periods = []
if config['name']:
    #Find the looked teacher
    searched_teacher = None
    for uo in teacher_list:
        if uo.name.lower() == config['name'].lower():
            searched_teacher = uo
            print(f'Found {uo.name}')
            break
    if not searched_teacher:
        print('No teacher found')
        exit(1)

    #Find all periods for this teacher
    for period in all_periods:
        for element in period.objects:
            if element['type'] == 2 and element['id'] == searched_teacher.id:
                found_periods.append(period)
elif config['classname']:
    #Find the looked class
    searched_class = None
    for uo in all_uobjects:
        if uo.type == 1 and uo.name.lower() == config['classname'].lower():
            searched_class = uo
            print(f'Found {uo.name}')
            break
    if not searched_class:
        print('No class found')
        exit(1)
    
    for period in all_periods:
        for element in period.objects:
            if element['type'] == 1 and element['id'] == searched_class.id:
                found_periods.append(period)

# Sort them
sorted_periods = sorted(found_periods, key=lambda period: (period.date, period.start_time))


# Print timetable
if config['timetable']:
    from tabulate import tabulate
    if config['name']:
        print(f"Timetable for {config['name']} ({get_week_range(str(all_periods[0].date))})")
    else:
        print(f"Timetable for {config['classname']} ({get_week_range(str(all_periods[0].date))})")

    time_slots = sorted(list(set((p.start_time, p.end_time) for p in sorted_periods)))

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    timetable = {f'{str(start)[:-2]}:{str(start)[-2:]} - {str(end)[:-2]}:{str(end)[-2:]}': {day: "" for day in days_of_week} for start, end in time_slots}

    for period in sorted_periods:
        if config['date'] and config['date'] != str(period.date):
            continue

        date_str = str(period.date)
        day_of_week = datetime.strptime(date_str, "%Y%m%d").strftime("%A")
        time_str = f'{str(period.start_time)[:-2]}:{str(period.start_time)[-2:]} - {str(period.end_time)[:-2]}:{str(period.end_time)[-2:]}'

        subject = ''
        room = ''
        class_name = ''
        teacher_name = ''

        for obj in period.objects:
            u_obj = find_object_by_id(all_uobjects, obj['id'])
            if u_obj:
                if u_obj.type == 3:
                    subject = u_obj.name
                elif u_obj.type == 4:
                    room = u_obj.name
                elif u_obj.type == 1:
                    class_name = u_obj.name
                elif u_obj.type == 2:
                    teacher_name = u_obj.name
        
        if config['name']:
            if config['rooms']:
                timetable[time_str][day_of_week] = f"{subject}" + f"\n{room}" + f"\n{class_name}"
            else:
                timetable[time_str][day_of_week] = f"{subject}" + f"\n{class_name}"
        else:
            if config['rooms']:
                timetable[time_str][day_of_week] = f"{subject}" + f"\n{room}" + f"\n{teacher_name}"
            else:
                timetable[time_str][day_of_week] = f"{subject}" + f"\n{teacher_name}"


    headers = ["Time"] + days_of_week
    table_data = []
    for time_slot, days in timetable.items():
        row = [time_slot] + [days[day] for day in days_of_week]
        table_data.append(row)

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

# print current class
if not config['timetable']:
    if config['name']:
        print('The teacher is now: ')
    else:
        print('The class is now: ')
    found = False
    for period in sorted_periods:
        if str(period.date) == date_that_must_be_here and is_time_in_lesson_range(period.start_time, period.end_time):
            from tabulate import tabulate
            if config['name']:
                headers = ["Day", "Time", "Subject", "Room", "Class"]
            else:
                headers = ["Day", "Time", "Subject", "Room", "Teacher"]
            table_data = []
            date_str = str(period.date)
            day_of_week = datetime.strptime(date_str, "%Y%m%d").strftime("%A")
            time_str = f'{str(period.start_time)[:-2]}:{str(period.start_time)[-2:]} - {str(period.end_time)[:-2]}:{str(period.end_time)[-2:]}'
            
            subject = ''
            room = ''
            class_name = ''
            teacher_name = ''
            
            for obj in period.objects:
                u_obj = find_object_by_id(all_uobjects, obj['id'])
                if u_obj:
                    if u_obj.type == 3:
                        subject = u_obj.name
                    elif u_obj.type == 4:
                        room = u_obj.name
                    elif u_obj.type == 1:
                        class_name = u_obj.name
                    elif u_obj.type == 2:
                        teacher_name = u_obj.name
            
            if config['name']:
                table_data.append([day_of_week, time_str, subject, room, class_name])
            else:
                table_data.append([day_of_week, time_str, subject, room, teacher_name])

            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            found = True
    if not found:
        print('Having a free time!')
