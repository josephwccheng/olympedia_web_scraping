# Author: Joseph Cheng
# Main Objective: to scrape the data from olympedia.org to proivde the data community with up to date olympian data including players, events, and winter / summer sports
# Note: this project is for non-commercial purposes


from olympedia_scraper import OlympediaScraper
from os.path import exists
import csv
import pandas as pd
from tqdm import tqdm

# Multi-processing - not used as threading proivdes a faster option
import multiprocessing
from multiprocessing import Pool, cpu_count

# Multi-threading
import concurrent.futures


def get_event_athlete_results_from_country_into_csv(country_noc:str, file_path: str='data/Olympic_Athlete_Event_Results_test.csv'):
    event_athlete_results = olympic_scraper.get_event_athletes_results_from_country(country_noc)
    with open(file_path, 'a+', newline='') as f:
        writer= csv.writer(f)
        if event_athlete_results is not None:
            for event_athlete_result in event_athlete_results:
                writer.writerow(list(event_athlete_result.values()))
    return country_noc


def get_athlete_bio_and_results_into_csv(athlete_id:str, bio_file_path: str='data/Olympic_Athlete_Bio_test.csv', event_file_path='data/Olympic_Athlete_Event_Results_test_2.csv'):

    athlete_bio_and_results = olympic_scraper.get_bio_and_results_from_athlete_id(athlete_id)
    with open(bio_file_path, 'a+', newline='') as f_bio, open(event_file_path, 'a+', newline='') as f_events:
        writer_bio = csv.writer(f_bio)
        writer_events = csv.writer(f_events)

        athlete_bio = athlete_bio_and_results['athlete_bio_info']
        writer_bio.writerow(list(athlete_bio.values()))

        athlete_results = athlete_bio_and_results['athlete_results']
        for athlete_result in athlete_results:
            writer_events.writerow(list(athlete_result.values()))
    return athlete_id

def download_html_from_result_id(result_id:str, file_path: str='data/raw_result_html_files'):
    olympic_scraper = OlympediaScraper()
    result_html = olympic_scraper.get_html_from_result_id(result_id)
    with open(file_path + '/' + result_id + '.html', 'wb') as file: # saves modified html doc
        file.write(result_html)
    return result_id

if __name__ == "__main__":

    olympic_scraper = OlympediaScraper()

    olympic_country_csv_path = 'data/Olympics_Country_test.csv'
    olympic_games_csv_path = 'data/Olympics_Games_test.csv'
    olympic_athlete_bio_csv_path = 'data/Olympic_Athlete_Bio_test.csv'
    olympic_athlete_event_results_csv_path = 'data/Olympic_Athlete_Event_Results_test.csv'
    olympic_athlete_event_results_csv_path_2 = 'data/Olympic_Athlete_Event_Results_test_2.csv'
    distinct_athlete_id_csv_path = 'data/_distinct_athlete_id_csv_path_test.csv'
    distinct_result_id_csv_path = 'data/_distinct_result_id_csv_path_test.csv'
    raw_result_html_files_path = 'data/raw_result_html_files'

    # 1. Get Country List
    if not exists(olympic_country_csv_path):
        country_rows = olympic_scraper.get_country_list()
        country_header = ['noc', 'country']
        with open(olympic_country_csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(country_header)
            writer.writerows(country_rows)
        print(f'1. {olympic_country_csv_path} file created!')
    else:
        print(f'1. {olympic_country_csv_path} file already exist')
    
    # 2. Get Olympic Games List
    if not exists(olympic_games_csv_path):
        games_rows = olympic_scraper.get_olympics_games()
        games_header = ['games', 'years', 'cities', 'start_date', 'end_date', 'held']
        with open(olympic_games_csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(games_header)
            writer.writerows(games_rows)
        print(f'2. {olympic_games_csv_path} file created!')
    else:
        print(f'2. {olympic_games_csv_path} file already exist')

    # 3. Get All athlete ids and their results
    if not exists(olympic_athlete_event_results_csv_path):
        country_noc = [i[0] for i in country_rows]
        event_athletes_header = ["edition","country_noc","sport","event","result_id","athlete","athlete_id","pos","medal","isTeamSport"]
        with open(olympic_athlete_event_results_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(event_athletes_header)
        with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
            # map will print the result in order
            results = list(tqdm(executor.map(get_event_athlete_results_from_country_into_csv, country_noc), total=len(country_noc)))
        
        print(f'3. {olympic_athlete_event_results_csv_path} file created!')
    else:
        print(f'3. {olympic_athlete_event_results_csv_path} file already exist')

    # 4. Get Distinct Athlete ID and Event Information into new CSV Files
    if not exists(distinct_athlete_id_csv_path) and not exists(distinct_result_id_csv_path):
        if exists(olympic_athlete_event_results_csv_path):
            athlte_id_header = ['athlete_id']
            result_id_header = ['result_id']
            athlete_event_results_df = pd.read_csv(olympic_athlete_event_results_csv_path)
            distinct_athlete_id_list = set(athlete_event_results_df['athlete_id'].astype(str).values.tolist())
            distinct_result_id_list = set(athlete_event_results_df['result_id'].astype(str).values.tolist())

            with open(distinct_athlete_id_csv_path, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(athlte_id_header)
                writer.writerows([[athlete_id] for athlete_id in distinct_athlete_id_list])

            with open(distinct_result_id_csv_path, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(result_id_header)
                writer.writerows([[result_id] for result_id in distinct_result_id_list])
            print(f'4. {distinct_athlete_id_csv_path} and {distinct_result_id_csv_path} files created!')
        else:
            print(f'4. {olympic_athlete_event_results_csv_path} doesn\'t exist')
    else:
        print(f'4. {distinct_athlete_id_csv_path} and {distinct_result_id_csv_path} already exist')


    # 5. Get athlete bio information and results from all the events they parcipated in
    if not exists(olympic_athlete_event_results_csv_path_2) and not exists(olympic_athlete_bio_csv_path):
        if exists(distinct_athlete_id_csv_path):
            with open(distinct_athlete_id_csv_path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                athlete_ids = [item for row in csv_reader for item in row]
            bio_header = ['athlete_id', 'name', 'sex', 'born', 'height', 'weight', 'country', 'country_noc', 'description', 'special_notes']
            # events_header = ['athlete_id','olympic_game', 'dicipline', 'event', 'noc', 'pos', 'medals']
            events_header = ['edition','country_noc','sport','event','result_id','athlete','athlete_id','pos','medals']
            with open(olympic_athlete_bio_csv_path, 'w', newline='') as f_bio, open(olympic_athlete_event_results_csv_path_2, 'w', newline='') as f_events:
                writer_bio = csv.writer(f_bio)
                writer_events = csv.writer(f_events)
                writer_bio.writerow(bio_header)
                writer_events.writerow(events_header)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
                # map will print the result in order
                results = list(tqdm(executor.map(get_athlete_bio_and_results_into_csv, athlete_ids[1:]), total=len(athlete_ids[1:])))
            print(f'5. {olympic_athlete_bio_csv_path} and {olympic_athlete_event_results_csv_path_2} files created!')  
        else:
            print(f'5. {distinct_athlete_id_csv_path} doesn\'t exist')
    else:
        print(f'5. {olympic_athlete_bio_csv_path} and {olympic_athlete_event_results_csv_path_2} already exist')
    
    # 6. Download Results into html
    download_result = False
    if download_result == True:
        if exists (distinct_result_id_csv_path):
            with open(distinct_result_id_csv_path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                event_ids = [item for row in csv_reader for item in row]
            if multiprocessing.cpu_count() > 0:
                cpu_count = multiprocessing.cpu_count()
            else:
                cpu_count = 5
            print(f'detected {cpu_count} cpu cores')
            with Pool(processes=cpu_count) as p:
                event_html = list(tqdm(p.imap(download_html_from_result_id, event_ids[1:]), total=len(event_ids[1:]), desc= 'downloading html from a list of events'))
            print(f'6. event html files downloaded to {raw_result_html_files_path}')
        else:
            print(f'6. {distinct_result_id_csv_path} does not exist')
    else:
        print(f'6. download_result is False, result html files not downloaded')

print('debug')