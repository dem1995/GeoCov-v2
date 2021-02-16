import requests
import os
import json

search_url = "https://api.twitter.com/2/tweets/search/all"

# Retrieve and format the bearer token for authorization
with open("auth_keys.json") as auth_keys_file:
	auth_keys = json.load(auth_keys_file)
bearer_token = auth_keys["BEARER_TOKEN"]
headers = {"Authorization": f"Bearer {bearer_token}"}

def connect_to_endpoint(params):
	
	aggregate_json = []
	first_page=True:
	while first_page or 

	response = requests.request("GET", search_url, headers=headers, params=params)
	print(response.status_code)
	if response.status_code != 200:
		raise Exception(response.status_code, response.text)

	
	
	return response.json()

def fetch_tweets(start_time: str, end_time:str, latlongrad:list = None, lang_code:str='en',
                     include_rts:bool = False, include_replies:bool = False, user=None):
	include_rts_query = "" if include_rts else "-is:retweet"
	include_replies_query = "" if include_replies else "-is:reply"
	point_radius = "" if latlongrad is None else f"point_radius:{latlongrad}"
	user_query = '' if user is None else f'from:{user}'
	lang_query = '' if lang_code is None else f'lang:{lang_code}'

	# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
	# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
	query_params = {'query': f'{user_query} {lang_query} {point_radius} {include_rts_query} {include_replies_query}',
	                'start_time': start_time,
	                'end_time': end_time}

	#if latlongrad is not None:
	                #query_params['point_radius'] = latlongrad

	return connect_to_endpoint(query_params)

if __name__ == "__main__":
	retrieved_tweets=fetch_tweets(user="DEM1995",
	                                 start_time="2019-12-01T00:00:00Z",
	                                 end_time="2019-12-04T00:00:00Z")
	print(json.dumps(retrieved_tweets, indent=4, sort_keys=True))
