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

def endpoint_call(params) -> dict:
	"""
	Makes a call to the previously-specified endpoint with the previously specified credentials
	On the provided parameters. This is a very limited call; it returns a single page.
	To retrieve many tweets, use fetch_tweets.
	"""
	global backoff_multiplier
	while backoff_multiplier == 0 or response.status_code == 429:
		time.sleep(int(1.5**backoff_multiplier))
		print("backoff_multiplier", backoff_multiplier)
		response = requests.request("GET", search_url, headers=headers, params=params)
		print(response.status_code)
		if response.status_code == 429:
			backoff_multiplier += 1
		if response.status_code == 503:
			time.sleep(3600)
		if response.status_code != 429 and response.status_code != 200 and response.status_code!=503 or backoff_multiplier > 21:
			raise Exception(response.status_code, response.text)
		if response.status_code == 200:
			return response.json()

def format_params(start_time: str, end_time:str, longlatrad:str = None, lang_code:str='en',
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
	user_query = '' if user is None else f'from:{user}'
	lang_query = '' if lang_code is None else f'lang:{lang_code}'

	# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
	# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
	query_params = {'query': f'{user_query} {lang_query} {point_radius_query} {include_rts_query} {include_qts_query} {include_ads_query} {include_replies_query}',
	                'tweet.fields': 'id,author_id,geo,created_at,text,lang',
	                'start_time': start_time,
	                'end_time': end_time}

	query_params['max_results']=500

	return query_params

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

if __name__ == "__main__":
	params=format_params(user="DEM1995",
	                     start_time="2019-12-01T00:00:00-06:00",
	                     end_time="2019-12-04T00:00:00-06:00")
	retrieved_tweets = fetch_tweets(params)
	print(json.dumps(list(retrieved_tweets), indent=4, sort_keys=True))
