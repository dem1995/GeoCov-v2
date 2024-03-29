import requests
import os
import json
import time
from typing import Generator, Dict

search_url = "https://api.twitter.com/2/tweets/search/all"

# Retrieve and format the bearer token for authorization
with open("auth_keys.json") as auth_keys_file:
	auth_keys = json.load(auth_keys_file)
bearer_token = auth_keys["BEARER_TOKEN"]
headers = {"Authorization": f"Bearer {bearer_token}"}

backoff_multiplier = 0

# Status codes:
# 200: Okay
# 429: Too many requests
# 503: Service unavailable

def endpoint_call(params) -> dict:
	"""
	Makes a call to the previously-specified endpoint with the previously specified credentials
	On the provided parameters. This is a very limited call; it returns a single page.
	To retrieve many tweets, use fetch_tweets.
	"""
	global backoff_multiplier
	endpoint_call_initial_run = True
	while backoff_multiplier == 0 or endpoint_call_initial_run or response.status_code != 200:
		endpoint_call_initial_run = False
		time.sleep(int(1.5**backoff_multiplier))
		print("backoff_multiplier", backoff_multiplier)
		response = requests.request("GET", search_url, headers=headers, params=params)
		print(response.status_code)
		if response.status_code == 429:     # Too many requests
			backoff_multiplier += 1     # Increase backoff
		elif response.status_code == 503:   # Service unavailable
			time.sleep(3600)            # Sleep for 6 minutes
		elif response.status_code == 200:   # Success
			if backoff_multiplier > 0:
				backoff_multiplier -= 1
			return response.json()
		elif backoff_multiplier > 21:
			raise Exception("Status code", response.status_code, "Text", response.text, "Multiplier", backoff_multiplier)

def fetch_tweets(params:Dict[str, str]) -> Generator[dict, None, None]:
	"""
	Returns a generator of tweet text-id pairs, each tweet in the form of a dictionary (retdict['text'], retdict['id'])
	You can use format_params to filter this
	"""
	are_more_pages = True
	while are_more_pages:
		response_json = endpoint_call(params)

		are_more_pages = 'meta' in response_json and 'next_token' in response_json['meta']
		tweets_returned = [] if 'data' not in response_json else response_json['data']

		if are_more_pages:
			params['next_token'] = response_json['meta']['next_token']

		for tweet_returned in tweets_returned:
			yield tweet_returned
		time.sleep(1)


def format_params(start_time: str, end_time:str, longlatrad:str = None, place_id:int = None, lang_code:str='en',
                  include_rts:bool = False, include_qts:bool = False,
                  include_replies:bool = False, include_ads:bool = False, user=None) -> Dict[str, str]:
	"""
	Formats the provided parameters for calls to endpoint_call or fetch_tweets.
	"""
	include_rts_query = "" if include_rts else "-is:retweet"
	include_qts_query = "" if include_qts else "-is:quote"
	include_ads_query = "" if include_ads else "-is:nullcast"
	include_replies_query = "" if include_replies else "-is:reply"
	point_radius_query = "" if longlatrad is None else f"point_radius:{longlatrad}"
	place_id_query = "" if place_id is None else f"place:{place_id}"
	user_query = '' if user is None else f'from:{user}'
	lang_query = '' if lang_code is None else f'lang:{lang_code}'

	# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
	# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
	query_params = {'query': f'{user_query} {lang_query} {point_radius_query} {place_id_query} {include_rts_query} {include_qts_query} {include_ads_query} {include_replies_query}',
	                'tweet.fields': 'id,author_id,geo,created_at,text,lang,conversation_id,public_metrics,source',
	                'start_time': start_time,
	                'end_time': end_time}

	query_params['max_results']=500

	return query_params



if __name__ == "__main__":
	params=format_params(user="DEM1995",
	                     start_time="2019-12-01T00:00:00-06:00",
	                     end_time="2019-12-04T00:00:00-06:00")
	retrieved_tweets = fetch_tweets(params)
	print(json.dumps(list(retrieved_tweets), indent=4, sort_keys=True))
