#!/usr/bin/env python3

import sys
import os
import argparse
import requests
from datetime import datetime, timedelta
import json

city = 'NewYork'
country = 'US'
prayers_url = 'http://api.aladhan.com/v1/timingsByCity?method=2&city={}&country={}'.format(city, country)
prayers_file = os.path.expanduser('~/.config/prayers')
prayers_arabic = {
    'Fajr': 'الفجر',
    'Sunrise': 'الشروق',
    'Dhuhr': 'الظهر',
    'Asr': 'العصر',
    'Maghrib': 'المغرب',
    'Isha': 'العشاء'
}
prayers_arabic_compact = {
    'Fajr': 'فجر',
    'Dhuhr': 'ظهر',
    'Asr': 'عصر',
    'Maghrib': 'مغرب',
    'Isha': 'عشا'
}

def update():
    try:
        prayers_info = requests.get(prayers_url).json()
        with open(prayers_file, 'w') as f:
            json.dump(prayers_info, f)
        return prayers_info
    except:
        return None

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--compact', action='store_true', help='Show less text in output')
    parser.add_argument('--next', action='store_true', help='Show time remaining for next salah')
    parser.add_argument('--update', action='store_true', help='Force update of prayers file')
    args = parser.parse_args(arguments)
    
    if args.update or not os.path.exists(prayers_file):
        prayers_info = update()
    else:
        with open(prayers_file, 'r') as f:
            prayers_info = json.load(f)
    
    if not prayers_info:
        return -1
    
    prayers_date = datetime.fromtimestamp(int(prayers_info['data']['date']['timestamp'])).date()
    if prayers_date < datetime.today().date():
        prayers_info = update()
        if not prayers_info:
            return -1
    
    items = filter(lambda item: item[0] in (prayers_arabic if not args.compact else prayers_arabic_compact), prayers_info['data']['timings'].items())
    items = [(
        prayers_arabic[item[0]] if not args.compact else prayers_arabic_compact[item[0]], 
        datetime.combine(prayers_date, datetime.strptime(item[1], '%H:%M').time())
        ) for item in items]
    items.append((items[0][0], items[0][1] + timedelta(days=1))) # add next day fajr

    if args.next:
        now = datetime.now()
        next_prayers = list(filter(lambda item: item[1] > now, items))
        if next_prayers: 
            next_prayer = min(next_prayers, key=lambda item: abs(item[1] - now))
            time_remaining = next_prayer[1] - now
            print(next_prayer[0], next_prayer[1].strftime('%-I:%M%P' if not args.compact else '%-I:%M'), '(' + ('متبقي ' if not args.compact else '')  + ':'.join(str(time_remaining).split(':')[:2]) + ')')
    else:
        for idx in range(len(items) - 1):
            print(items[idx][0], items[idx][1].strftime('%-I:%M%P' if not args.compact else '%-I:%M'))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
