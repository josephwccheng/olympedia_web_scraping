import multiprocessing
from bs4 import BeautifulSoup
from typing import List, Dict
import requests
import csv
import re
from os.path import exists
from tqdm import tqdm
from multiprocessing import Pool, cpu_count


base_url = 'http://www.olympedia.org'

# 1. Get Table of all active partipating countries
# Output Format: [[country_noc, country_name], ... ]
def get_country_list() -> List[list]:
    countries_page = requests.get(base_url + '/countries')
    countries_soup = BeautifulSoup(countries_page.content, 'html.parser')
    countries_table = countries_soup.select_one('body > div.container > table:nth-child(5)')
    country_nocs = [item.get_text() for item in countries_table.select('tbody > tr > td:nth-child(1) > a')]
    country_name = [item.get_text() for item in countries_table.select('tbody > tr > td:nth-child(2) > a')]
    # Note: competed in modern olympics flag -> glyphicon-ok = yes, glyphicon-remove = no
    isModernOlympics = [item['class'] for item in countries_table.select('tbody > tr > td:nth-child(3) > span')]
    countries = []
    
    for i in range(len(country_nocs)):
        if isModernOlympics[i][1] == 'glyphicon-ok':
            countries.append([country_nocs[i], country_name[i]])

    return countries

# 2. Creating a dictionary to know the host city for the Olympics
# Output Format: [[year + season), City, Competition_Date, Held]
def get_olympics_games() -> List[list]:
    games_page = requests.get(base_url + '/editions')
    games_soup = BeautifulSoup(games_page.content, 'html.parser')
    
    summer_table = games_soup.select_one('body > div.container > table:nth-child(5)')
    summer_years = [item.get_text() for item in summer_table.select('tr > td:nth-child(2)')]
    summer_games = [item + ' Summer Olympics' for item in summer_years]
    summer_cities = [item.get_text() for item in summer_table.select('tr > td:nth-child(3)')]
    summer_start_date = [item.get_text() for item in summer_table.select('tr > td:nth-child(5)')]
    summer_end_date = [item.get_text() for item in summer_table.select('tr > td:nth-child(6)')]
    summer_held = [item.get_text().strip() for item in summer_table.select('tr > td:nth-child(8)')]
    
    winter_table = games_soup.select_one('body > div.container > table:nth-child(7)')
    winter_years = [item.get_text() for item in winter_table.select('tr > td:nth-child(2)')]
    winter_games = [item + ' Winter Olympics' for item in winter_years]
    winter_cities = [item.get_text() for item in winter_table.select('tr > td:nth-child(3)')]
    winter_start_date = [item.get_text() for item in winter_table.select('tr > td:nth-child(5)')]
    winter_end_date = [item.get_text() for item in winter_table.select('tr > td:nth-child(6)')]
    winter_held = [item.get_text().strip() for item in winter_table.select('tr > td:nth-child(8)')]
    
    games = summer_games + winter_games
    years = summer_years + winter_years
    cities = summer_cities + winter_cities
    start_date = summer_start_date + winter_start_date
    end_date = summer_end_date + winter_end_date
    held = summer_held + winter_held

    return [[games[i], years[i], cities[i], start_date[i], end_date[i], held[i]] for i in range(len(years))]

# 3. Table of all distinct players
# Input: country noc
# Output: list of players who played for the ocuntry
def get_athlete_id_from_country(country_noc: str):
    country_url = base_url + '/countries/' + country_noc
    country_page = requests.get(country_url)
    country_soup = BeautifulSoup(country_page.content, 'html.parser')
    olympic_table = country_soup.select_one('body > div.container > table:nth-child(11)')
    if olympic_table is None:
        return
    # Get a list of results url for each Edition based on country
    result_urls = [base_url + olympic['href'] for olympic in olympic_table.select('tbody > tr > td:nth-child(6) > a')]
    athlete_ids = []
    for result_url in result_urls:
        athlete_ids.extend(get_athlete_id_from_result_url(result_url))
    return set(athlete_ids)

# <Helper Function>
# Get 'athlete_id' from the result page
def get_athlete_id_from_result_url(result_url: str):
    result_page = requests.get(result_url)
    result_soup = BeautifulSoup(result_page.content, 'html.parser')
    result_table = result_soup.select_one('table')
    athlete_ids = [athlete['href'].split("/")[2] for athlete in result_table.select('tbody > tr > td:nth-child(2) > a')]
    return athlete_ids

# Get athlete's biography from athlete's url
def get_bio_and_results_from_athlete_id(athlete_id: str):
    athlete_url = base_url + '/athletes/' + athlete_id
    athlete_page = requests.get(athlete_url)
    athlete_soup = BeautifulSoup(athlete_page.content, 'html.parser')
    
    # Obtaining athlete bio info
    bio_keys_items = athlete_soup.select('body > div.container > table.biodata > tr > th')
    bio_values_items = athlete_soup.select('body > div.container > table.biodata > tr > td')
    athlete_bio_info = process_athelete_bio(athlete_id, bio_keys_items,bio_values_items)

    # Populating a table of all the game the athele participated in and their position / medal
    olympic_games_items = athlete_soup.select('body > div.container > table.table > tbody > tr > td:nth-child(1)')
    discipline_items = athlete_soup.select('body > div.container > table.table > tbody > tr > td:nth-child(2) > a:nth-child(1)')
    noc_items = athlete_soup.select('body > div.container > table.table > tbody > tr > td:nth-child(3)')
    pos_items = athlete_soup.select('body > div.container > table.table > tbody > tr > td:nth-child(4)')
    medal_items = athlete_soup.select('body > div.container > table.table > tbody > tr > td:nth-child(5)')
    athlete_results = process_athlete_result_table(athlete_id, olympic_games_items, discipline_items, noc_items, pos_items, medal_items)
    return { 'athelete_bio_info': athlete_bio_info, 'athelete_results': athlete_results }

def process_athelete_bio(athelete_id: str, bio_keys_items: list, bio_values_items: list) -> Dict:
    keys_bio = [item.get_text() for item in bio_keys_items]
    values_bio = [item.get_text() for item in bio_values_items]
    raw_athlete_bio_info = {keys_bio[i]: values_bio[i] for i in range(len(keys_bio))}
    athlete_bio_info = {
        'athlete_id': athelete_id,
        'name': re.sub('[^0-9a-zA-Z]+', ' ', raw_athlete_bio_info.get('Used name')),
        'sex': raw_athlete_bio_info.get('Sex'),
        'born': '',
        'height': '',
        'weight': '',
        'noc': raw_athlete_bio_info.get('NOC')
    }
    if raw_athlete_bio_info.get('Born') is not None:
        athlete_bio_info['born'] = raw_athlete_bio_info.get('Born').split(' in ')[0]
    if raw_athlete_bio_info.get('Measurements') is not None:
        measurement = raw_athlete_bio_info.get('Measurements').split(' / ')
        if len(measurement) > 1:
            athlete_bio_info['height'] = measurement[0].split(' cm')[0]
            athlete_bio_info['weight'] = measurement[1].split(' kg')[0]
    return athlete_bio_info

def process_athlete_result_table(athlete_id:str, olympic_games_items:list, discipline_items:list, noc_items:list, pos_items:list, medal_items:list) -> List[Dict]:
    # Create & Insert athlete info
    olympic_games = [item.get_text() for item in olympic_games_items]
    disciplines = [item.get_text() for item in discipline_items]
    noc = [item.get_text() for item in noc_items] 
    pos = [item.get_text() for item in pos_items]
    medals = [item.get_text() for item in medal_items]
    result_table = []
    # Getting the olympic games and sport
    cur_olympic_game = ''
    cur_dicipline = ''
    cur_noc = ''
    for i in range(len(olympic_games)):
        if olympic_games[i].strip() != '':
            cur_olympic_game = olympic_games[i].strip()
            cur_dicipline = disciplines[i]
            cur_noc = noc[i]
        else:
            event_result = {
                'athlete_id': athlete_id,
                'olympic_game': cur_olympic_game,
                'dicipline': cur_dicipline,
                'event': disciplines[i],
                'noc': cur_noc,
                'pos': pos[i],
                'medals': medals[i]
            }
            result_table.append(event_result)
    return result_table

if __name__ == "__main__":
    olympic_country_csv_path = 'data/Olympics_Country.csv'
    olympic_games_csv_path = 'data/Olympics_Games.csv'
    olympic_athlete_id_csv_path = 'data/Olympic_Athlete_id.csv'
    olympic_athlete_bio_csv_path = 'data/Olympic_Athlete_Bio.csv'
    olympic_athlete_event_results_csv_path = 'data/Olympic_Athlete_Event_Results.csv'

    # 1. Get Country List
    country_rows = get_country_list()
    if not exists(olympic_country_csv_path):
        country_header = ['noc', 'country']
        with open(olympic_country_csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(country_header)
            writer.writerows(country_rows)
    else:
        print('Olympic_Country.csv file already exist')
    
    # 2. Get Olympic Games List
    if not exists(olympic_games_csv_path):
        games_rows = get_olympics_games()
        games_header = ['games', 'years', 'cities', 'start_date', 'end_date', 'held']
        with open(olympic_games_csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(games_header)
            writer.writerows(games_rows)
    else:
        print('Olympic_Games.csv file already exist')

    # 3. Get All athlete ids and their results
    country_noc = [i[0] for i in country_rows]
    if multiprocessing.cpu_count() > 0:
        cpu_count = multiprocessing.cpu_count()
    else:
        cpu_count = 5
    print(f'detected {cpu_count} cpu cores')
    with Pool(processes=cpu_count) as p:
        country_athlete_ids = list(tqdm(p.imap(get_athlete_id_from_country, country_noc), total=len(country_noc), desc= 'processing multiple countries to retrieve athlete ids'))
    athlete_ids_output = set()
    for athlete_ids in country_athlete_ids:
        if athlete_ids is not None:
            athlete_ids_output.update(athlete_ids)
    with open(olympic_athlete_id_csv_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['athlete_id'])
        for athlete_id in athlete_ids_output:
            writer.writerow([athlete_id])

    # 4. Get athelete bio information and results from all the events they parcipated in
    with open(olympic_athlete_id_csv_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        athlete_ids = [item for row in csv_reader for item in row]

    if multiprocessing.cpu_count() > 0:
        cpu_count = multiprocessing.cpu_count()
    else:
        cpu_count = 5
    print(f'detected {cpu_count} cpu cores')
    with Pool(processes=cpu_count) as p:
        athletes_bio_and_results = list(tqdm(p.imap(get_bio_and_results_from_athlete_id, athlete_ids[1:]), total=len(athlete_ids[1:]), desc= 'processing athlete ids to obtain bio and results information'))
    
    bio_header = ['athlete_id', 'name', 'sex', 'born', 'height', 'weight', 'noc']
    events_header = ['athlete_id','olympic_game', 'dicipline', 'event', 'noc', 'pos', 'medals']
    with open(olympic_athlete_bio_csv_path, 'w') as f_bio, open(olympic_athlete_event_results_csv_path,'w') as f_events:
        writer_bio = csv.writer(f_bio)
        writer_events = csv.writer(f_events)
        writer_bio.writerow(bio_header)
        writer_events.writerow(events_header)
        for athlete_bio_and_results in athletes_bio_and_results:
            athlete_bio = athlete_bio_and_results['athelete_bio_info']
            writer_bio.writerow(list(athlete_bio.values()))
            athlete_results = athlete_bio_and_results['athelete_results']
            for athlete_result in athlete_results:
                writer_events.writerow(list(athlete_result.values()))
