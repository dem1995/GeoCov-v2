#!/bin/bash
source venv/bin/activate

for city in "London ON"
do
	city_formatted="$(echo "$city" | sed -e 's/[^A-Za-z0-9_-]/_/g')"
	job_out="${city_formatted}JobOut.txt"
	python gather_tweets.py --since '2019-01' --until '2020-12' --splitmode=m "${city}" > "${job_out}" --radius 10
done
