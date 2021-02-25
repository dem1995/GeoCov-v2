"""
"""

import calendar
import argparse
import re
import os
import datetime
import time
import json
from twitter_fetch import fetch_tweets, format_params
from time_zone_retrieval import get_UTC_offset_from_latlong
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="GeoPy")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('location', help="The location to search for, in whatever Google-searchable format you want." 
		" Being more specific may be important if there are more prominent locations with the same name, however.")
parser.add_argument('--since', default='2019-01-01',
		help="The day/month to start, in the format 'yyyy', 'yyyy-mm', or 'yyyy-mm-dd'")
parser.add_argument('--until', default='2020-11-30',
		help="The day/month to end (inclusive), in the format 'yyyy', 'yyyy-mm', or 'yyyy-mm-dd'")
parser.add_argument('--splitmode', default='monthly',
		help="How to split the resulting Tweets up. Options are: daily, monthly"
		", or nd, which is n-daily where n is an integer - i.e., splitmode=7d would be weekly from the start day")
parser.add_argument('--radius', nargs='?', type=int, default=40,
		help="The radius (in miles) about the location to grab Tweets for. Defaults to 40 miles.")
args = parser.parse_args()

location = geolocator.geocode(args.location)
print(f"Your selected location for [{args.location}] is: [{location}]. Radius: {args.radius}mi")
location_name = re.sub(r'[^0-9a-zA-Z]', '_', args.location)
print(f"For processing, using name: {location_name}")

radius_string = "" if args.radius==40 else f"-{args.radius}mi"
directory_name = location_name + radius_string
if not os.path.exists(directory_name):
    os.makedirs(directory_name)

with open(f'{directory_name}/metainfo.txt', mode='a+') as metafile:
	metafile.write(f'----------Run at {datetime.datetime.now()}----------\n')
	metafile.write(f'Tweets from {location} ({args.radius} mi radius of {location.latitude}, {location.longitude}) ([{args.location}]/[{location_name}])\n')
	metafile.write(f"Tweets dated {args.since} through {args.until}, chunked {args.splitmode}\n")

print(location.latitude, location.longitude)

utc_offset = get_UTC_offset_from_latlong(location.latitude, location.longitude)
start_date = [int(value) for value in args.since.split('-')]
end_date = [int(value) for value in args.until.split('-')]

def get_year_info(start_date:list, end_date:list):
	"""
	Input format: [year...]
	Chunks the interval between the two dates into years for processing.
	Returns a list of start dates, a list of end dates, and a list of filenames corresponding with each start-end date range.
	"""
	years = range(start_date[0], end_date[0]+1)
	sinces = [f"{year}-01-01T00:00:00{utc_offset}" for year in years]
	untils = [f"{year}-12-31T23:59:59{utc_offset}" for year in years]
	filenames = [f"{directory_name}/{year}-geocov" for year in years]
	return sinces, untils, filenames

def get_month_info(start_date:list, end_date:list):
	"""
	Input format: [year, month...]
	Chunks the interval between the two dates into months for processing.
	Returns a list of start dates, a list of end dates, and a list of filenames corresponding with each start-end date range.
	"""
	sinces, untils, filenames = list(), list(), list()
	for year in range(start_date[0], end_date[0]+1):
		months =  range(1, 12+1)
		if year == end_date[0]:
			months = months[ : end_date[1]]
		if year == start_date[0]:
			months = months[start_date[1]-1 : ]
		# Now that we have the months for the given year...
		for month in months:
			lastdate = calendar.monthrange(year, month)[1]
			sinces.append(f"{year}-{month:02d}-{1:02d}T00:00:00{utc_offset}")
			untils.append(f"{year}-{month:02d}-{lastdate:02d}T23:59:59{utc_offset}")
			filenames.append(f"{directory_name}/{year}-{month:02d}-geocov")
	return sinces, untils, filenames

def get_day_info(start_date:list, end_date:list, interval:int=1):
	"""
	Input format: [year, month, day...]
	Chunks the range between the two dates into interval-days-length pieces for processing.
	Returns a list of start dates, a list of end dates, and a list of filenames corresponding with each start-end date range.
	"""
	sinces, untils, filenames = list(), list(), list()
	start_date = datetime.date(start_date[0], start_date[1], start_date[2])
	end_date = datetime.date(end_date[0], end_date[1], end_date[2])

	def daterange(date1:datetime.date, date2:datetime.date, timestep:datetime.timedelta=datetime.timedelta(1)):
		curdate = date1
		while curdate <= date2:
			yield curdate
			curdate += timestep

	for dt in daterange(start_date, end_date, datetime.timedelta(interval)):
		since = datetime.datetime.combine(dt, datetime.datetime.min.time())
		until = since + datetime.timedelta(interval) - datetime.timedelta(seconds=1)
		sinces.append(since.strftime(f"%Y-%m-%dT%H:%M:%S{utc_offset}"))
		untils.append(until.strftime(f"%Y-%m-%dT%H:%M:%S{utc_offset}"))
		if since.date() == until.date():
			datestring = str(since.date())
		else:
			datestring = f"{str(since.date())}--{str(until.date())}"
		filenames.append(f"{directory_name}/{datestring}-geocov")
	return sinces, untils, filenames

if args.splitmode in {'yearly', 'y'}:
	sinces, untils, filenames = get_year_info(start_date, end_date)
elif args.splitmode in {'monthly', 'm'}:
	sinces, untils, filenames = get_month_info(start_date, end_date)
elif args.splitmode in {'daily', 'd'} or args.splitmode[1]=='d' and args.splitmode[0].isdigit():
	interval = 1 if args.splitmode[0]=='d' else int(args.splitmode[0])
	sinces, untils, filenames = get_day_info(start_date, end_date, interval)

firstrun=True
# Go through each of the time-frames and fetch/store the corresponding tweets
for filename, since, until in zip(filenames, sinces, untils):
	longlatrad = f"[{location.longitude} {location.latitude} {args.radius}mi]"
	print(f"since: {since}, until: {until}, longlatrad: {longlatrad}")
	params=format_params(start_time=since, end_time=until, longlatrad=longlatrad,
                     include_rts=False, include_replies=False, user=None)
	retrieved_tweets=fetch_tweets(params)

	# Write out results
	with open(f"{filename}.json", 'w+') as outfile, open(f"{filename}.ids", 'w+') as idfile:
		for tweet_json in retrieved_tweets:
			outfile.write(json.dumps(tweet_json) + '\n')
			idfile.write(tweet_json['id'] + '\n')

	time.sleep(600)
