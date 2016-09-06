from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import requests
import dota2api
import time
import settings
import traceback

engine = create_engine('sqlite:///matches.db', echo=False)

Base = declarative_base()

class Match(Base):
    """
    A table to store matches
    """

    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer)
    replay_url = Column(String)
    match_date = Column(DateTime)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
dota_api = dota2api.Initialise()

def get_recent_matches():
    """
    Get recent games from dota api
    """

    latest_match = dota_api.get_match_history()['matches'][0]['match_seq_num']
    seq_number = latest_match - settings.BACK_SEQ

    recent_matches = []

    for match in dota_api.get_match_history_by_seq_num(seq_number)['matches']:
        recent_matches.append(match['match_id'])

    return recent_matches

def scrape_match(match_id):
    """
    Scrape the match details from opendota API and return match
    details if the match has a rampage
    """
    response = requests.get(settings.BASE_API + str(match_id))
    match_details = response.json()

    if 'replay_url' in match_details and len(match_details['players']) > 2:
        for player in match_details['players']:
            try:
                if player['multi_kills'] is not None and '5' in player['multi_kills']:
                    print('We got a rampage: http://www.opendota.com/matches/%s' % match_details['match_id'])
                    return match_details
            except Exception as exc:
                print('We had an Error... %s'  % match_details['match_id'])
                traceback.print_exc()

    time.sleep(settings.OPENDOTA_SLEEP)
    pass

def post_game_info_to_db(result):
    """
    Saves games with replay to database
    """
    session.add(Match(
        match_id=result['match_id'],
        replay_url=result['replay_url'],
        match_date=datetime.fromtimestamp(result['start_time'])
    ))
    session.commit()

def do_scrape():
    """
    Runs the opendota scrape, and posts data to db.
    """
    all_results = []

    for match_id in get_recent_matches():
        result = scrape_match(match_id)
        if result is not None:
            all_results.append(result)
        pass

    print("{}: Got {} results".format(time.ctime(), len(all_results)))

    for result in all_results:
        post_game_info_to_db(result)
        pass
