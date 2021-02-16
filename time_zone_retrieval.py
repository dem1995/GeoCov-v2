import time
import math
from datetime import datetime
from pytz import timezone, utc
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="GeoPy")
tf = TimezoneFinder()

def get_UTC_offset_from_latlong(lat, lng):
	"""
	returns a latlong location's time-zone offset from UTC in (-)HH:MM
	"""
	today = datetime.now()
	tz_target = timezone(tf.certain_timezone_at(lng=lng, lat=lat))
	# ATTENTION: tz_target could be None! handle error case

	# Find the offset and convert it to a time object (to be turned into HH:MM)
	today_target = tz_target.localize(today)
	today_utc = utc.localize(today)
	offset = (today_utc - today_target).total_seconds()
	mag_offset = abs(offset)
	ty_res = time.gmtime(mag_offset)

	# Tack on + or - as needed for UTC format
	formatted_offset = time.strftime("%H:%M",ty_res)
	formatted_offset_prefix = '+' if offset<0 else '-'
	formatted_offset = formatted_offset_prefix + formatted_offset
	return formatted_offset

def get_UTC_offset(location:str):
	"""
	returns a named location's time-zone offset from UTC in (-)HH:MM
	"""
	location = geolocator.geocode(location)
	return get_UTC_offset_from_latlong(location.latitude, location.longitude)


minute_offset = get_UTC_offset("St. Louis, MO")
print("St. Louis:", minute_offset)
minute_offset = get_UTC_offset("Trondheim, Norway")
print("Trondheim:", minute_offset)

