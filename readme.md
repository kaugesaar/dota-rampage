# Finding rampages with Opendota

This microservice / scraper gets and saves matches which has at least one rampage. Match id, replay url and match date is saved to sqlite database.

## Configuration
You need to set envoirment variable ```D2_API_KEY``` - you can get your Steam Web API key [here](http://steamcommunity.com/dev/apikey).

    pip install -r requirements.txt

Run the scraper

    pyhton -u main.py
