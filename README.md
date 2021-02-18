# GeoCov-v2
GeoCov v2 (requires Twitter API v2 access to produce additional datasets). Dataset for geographically-specified tweets during Covid and the year prior, along with scripts for producing more for other locations.

Installation guide:
 1. Run `git clone https://github.com/dem1995/GeoCov-v2.git`.
 2. Navigate inside the project directory (`cd GeoCov-v2`)
 3. Replace the key in `auth_keys.json` with your bearer token (go to <https://developer.twitter.com/en/portal/dashboard>, click on your academic project, and then press the key symbol under "Project App".
 4. Run `python -m venv venv`
 5. Run `source venv/bin/activate` (or `./venv/Scripts/activate.bat` (without the `source` command) on Windows
 6. Run `pip install -r requirements.txt`

You're good to go! Now you can run `python gather_tweets.py -h` to learn what specific arguments you can use. I've provided two example commands below:

`python gather_tweets.py "Toronto, ON" --since '2021-01' --until '2021-12' --splitmode=m --radius=20 > log.txt`
- Grabs Tweets from within 20 miles of Toronto's center for the entire year of 2021, splitting up the results by month.

`python gather_tweets.py "St. Louis, MO" --since '2021-01' --until '2021-07-04' --splitmode=d --radius=40 > log.txt`
- Grabs tweets from within 40 miles of St. Louis's center from the start of 2021 until the Fourth of July (inclusive), splitting up the results by day.

If your location is ambiguous, feel free to be more specific - Toronto, ON, Canada, for example. You can check `metainfo.txt` within an output folder to see exactly what location was used.
