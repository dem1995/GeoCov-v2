import requests
import os
import json
from typing import Generator

search_url = "https://api.twitter.com/2/tweets/search/all"

# Retrieve and format the bearer token for authorization
with open("auth_keys.json") as auth_keys_file:
	auth_keys = json.load(auth_keys_file)
bearer_token = auth_keys["BEARER_TOKEN"]
headers = {"Authorization": f"Bearer {bearer_token}"}

def endpoint_call(params) -> dict:
	"""
	Makes a call to the previously-specified endpoint with the previously specified credentials
	On the provided parameters. This is a very limited call; it returns a single page.
	To retrieve many tweets, use fetch_tweets.
	"""
	response = requests.request("GET", search_url, headers=headers, params=params)
	print(response.status_code)
		if response.status_code != 200:
			raise Exception(response.status_code, response.text)
	return response.json()
	
def format_params(start_time: str, end_time:str, latlongrad:str = None, lang_code:str='en',
                  include_rts:bool = False, include_replies:bool = False, user=None) -> dict[str, str]:
	"""
	Formats the provided parameters for calls to endpoint_call or fetch_tweets.
	"""
	include_rts_query = "" if include_rts else "-is:retweet"
	include_replies_query = "" if include_replies else "-is:reply"
	point_radius_query = "" if latlongrad is None else f"point_radius:{latlongrad}"
	user_query = '' if user is None else f'from:{user}'
	lang_query = '' if lang_code is None else f'lang:{lang_code}'

	# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
	# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
	query_params = {'query': f'{user_query} {lang_query} {point_radius_query} {include_rts_query} {include_replies_query}',
	                'start_time': start_time,
	                'end_time': end_time}
	
	return query_params

def fetch_tweets(params:dict[str, str]) -> Generator[dict, None, None]:
	"""
	Returns a generator of tweet text-id pairs, each tweet in the form of a dictionary (retdict['text'], retdict['id'])
	You can use format_params to filter this
	"""
	are_more_pages = True
	while are_more_pages:
		response_json = endpoint_call(params)
		
		are_more_pages = 'meta' in response_json and 'next_token' in response_json['meta']
		tweets_returned = [] if 'data' not in response_json else 
		
		if are_more_pages:
			params['next_token'] = response_json['meta']['next_token']
			
		for tweet_returned in tweets_returned:
			yield tweet_returned
		
if __name__ == "__main__":
	params=format_params(user="DEM1995",
	                     start_time="2019-12-01T00:00:00-06:00",
	                     end_time="2019-12-04T00:00:00-06:00")

	print(json.dumps(retrieved_tweets, indent=4, sort_keys=True))
