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


# Creating function to save event ahtlete results for multi-threading / processing
def get_event_athlete_results_from_country_into_csv(country_noc:str, file_path: str=""):
    if not file_path:
        raise ValueError("file path not found")
    event_athlete_results = olympic_scraper.get_event_athletes_results_from_country(country_noc)
    with open(file_path, 'a+', newline='') as f:
        writer= csv.writer(f)
        if event_athlete_results is not None:
            for event_athlete_result in event_athlete_results:
                writer.writerow(list(event_athlete_result.values()))
    return country_noc

# Creating function to athlete's bio and results for multi-threading / processing
def get_athlete_bio_and_results_into_csv(athlete_id:str, bio_file_path: str="", event_file_path: str=""):
    if not bio_file_path or not event_file_path:
        raise ValueError("file path not found")
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

# Creating function to download html files for multi-threading / processing
def download_html_from_result_id(result_id:str, file_path: str=""):
    if not file_path:
        raise ValueError("file path not found")
    olympic_scraper = OlympediaScraper()
    result_html = olympic_scraper.get_html_from_result_id(result_id)
    with open(file_path + '/' + result_id + '.html', 'wb') as file: # saves modified html doc
        file.write(result_html)
    return result_id

# 1. Get Country List
def save_country_list_to_csv(olympic_country_csv_path: str=""):
    country_rows = olympic_scraper.get_countries_list()
    country_header = ['noc', 'country']
    with open(olympic_country_csv_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(country_header)
        writer.writerows(country_rows)
    print(f'1. {olympic_country_csv_path} file created!')
    return True

# 2. Get Olympic Games list
def save_olympic_games_list_to_csv(olympic_games_csv_path: str):
    games_rows = olympic_scraper.get_olympics_games()
    games_header = ['games', 'edition_url', 'years', 'cities', 'start_date', 'end_date', 'competition_date', 'isHeld']
    with open(olympic_games_csv_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(games_header)
        writer.writerows(games_rows)
    print(f'2. {olympic_games_csv_path} file created!')
    return True

# 3. Get all athlete ids and their results
# TODO - issue with results page not listing all player -> https://www.olympedia.org/countries/CAN/editions/62 -> Monobob
def save_all_athlete_and_results_from_country_noc_to_csv(country_noc: list, output_athlete_event_results_csv_path: str):
    event_athletes_header = ["edition","country_noc","sport","event","result_id","athlete","athlete_id","pos","medal","isTeamSport"]
    country_noc_threading = [[noc, output_athlete_event_results_csv_path] for noc in country_noc]
    with open(output_athlete_event_results_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(event_athletes_header)
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
        # map will print the result in order
        results = list(tqdm(executor.map(lambda p: get_event_athlete_results_from_country_into_csv(*p), country_noc_threading), total=len(country_noc)))
    
    print(f'3. {output_athlete_event_results_csv_path} file created!')
    return True

# 4. Get Distinct Athlete ID and Event Information into new CSV Files
def get_distinct_athlete_and_events_from_athlete_event_csv(athlete_event_results_csv_path: str, output_distinct_athlete_id_csv_path: str, output_distinct_result_id_csv_path: str):
    if exists(athlete_event_results_csv_path):
        athlte_id_header = ['athlete_id']
        result_id_header = ['result_id']
        athlete_event_results_df = pd.read_csv(athlete_event_results_csv_path)
        distinct_athlete_id_list = set(athlete_event_results_df['athlete_id'].astype(str).values.tolist())
        distinct_result_id_list = set(athlete_event_results_df['result_id'].astype(str).values.tolist())

        with open(output_distinct_athlete_id_csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(athlte_id_header)
            writer.writerows([[athlete_id] for athlete_id in distinct_athlete_id_list])

        with open(output_distinct_result_id_csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(result_id_header)
            writer.writerows([[result_id] for result_id in distinct_result_id_list])
        print(f'4. {distinct_athlete_id_csv_path} and {distinct_result_id_csv_path} files created!')
        return True
    else:
        print(f'4. {olympic_athlete_event_results_csv_path} doesn\'t exist')
        return False

# 5. Get athlete bio information and results from all the events they parcipated in
def get_athlete_bio_and_results_from_athlete_id_list(athlete_ids: list, output_athlete_bio_csv_path:str, output_athlete_event_results_csv_path:str):
    bio_header = ['athlete_id', 'name', 'sex', 'born', 'height', 'weight', 'country', 'country_noc', 'description', 'special_notes']
    events_header = ['edition','country_noc','sport','event','result_id','athlete','athlete_id','pos','medals']
    athlete_id_threading = [[athlete_id, output_athlete_bio_csv_path, output_athlete_event_results_csv_path] for athlete_id in athlete_ids]
    with open(output_athlete_bio_csv_path, 'w', newline='') as f_bio, open(output_athlete_event_results_csv_path, 'w', newline='') as f_events:
        writer_bio = csv.writer(f_bio)
        writer_events = csv.writer(f_events)
        writer_bio.writerow(bio_header)
        writer_events.writerow(events_header)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
        # map will print the result in order
        results = list(tqdm(executor.map(lambda p: get_athlete_bio_and_results_into_csv(*p), athlete_id_threading), total=len(athlete_ids)))
    print(f'5. {output_athlete_bio_csv_path} and {output_athlete_event_results_csv_path} files created!')  

# 6. Saving Medal results to CSV file
# TODO - Multi Process to make this faster
def save_medel_results_to_csv(olympic_games_csv_path: str , output_medal_results_csv_path: str):
    olympic_games_df = pd.read_csv(olympic_games_csv_path)
    medal_result = []
    header = ['game', 'edition_id', 'year', 'country', 'noc', 'gold', 'silver', 'bronze', 'total']

    for _, row in tqdm(olympic_games_df.iterrows(), total= len(olympic_games_df), desc="6. saving medal results from olympic games"): # Loop for each olympic game
        edition_id = row['edition_url'].split('/')[2]
        medal_table = olympic_scraper.get_medal_table_from_editions_id(edition_id)
        if medal_table:
            for i in range(len(medal_table['country'])):
                medal_result.append([row['games'], edition_id, row['years'], medal_table['country'][i], medal_table['noc'][i], medal_table['gold'][i], medal_table['silver'][i], medal_table['bronze'][i], medal_table['total'][i]])
    with open(output_medal_results_csv_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(medal_result) 
    return True

# 7. Download Results html into local repository
def download_result_html_to_path(event_ids: list, output_result_html_files_path: str):
    event_ids_multi_processing = [[event_id, output_result_html_files_path] for event_id in event_ids]
    if multiprocessing.cpu_count() > 0:
        cpu_count = multiprocessing.cpu_count()
    else:
        cpu_count = 5
    print(f'detected {cpu_count} cpu cores')
    with Pool(processes=cpu_count) as p:
        event_html = list(tqdm(p.starmap(download_html_from_result_id, event_ids_multi_processing), total=len(event_ids), desc= 'downloading html from a list of events'))
    print(f'7. event html files downloaded to {output_result_html_files_path}')

if __name__ == "__main__":

    olympic_scraper = OlympediaScraper()

    olympic_country_csv_path = 'data/Olympics_Country.csv'
    olympic_games_csv_path = 'data/Olympics_Games.csv'
    olympic_athlete_bio_csv_path = 'data/Olympic_Athlete_Bio.csv'
    olympic_athlete_event_results_csv_path = 'data/Olympic_Athlete_Event_Results.csv'
    olympic_athlete_event_results_csv_path_2 = 'data/Olympic_Athlete_Event_Results_2.csv'
    distinct_athlete_id_csv_path = 'data/_distinct_athlete_id.csv'
    distinct_result_id_csv_path = 'data/_distinct_result_id.csv'
    olympic_games_medal_tally = 'data/Olympic_Games_Medal_Tally.csv'
    raw_result_html_files_path = 'data/raw_result_html_files'

    # Note: You can control the trigger to choose which steps you want to run or not
    trigger = {
        'step_1': False,
        'step_2': False,
        'step_3': False,
        'step_4': False,
        'step_5': False,
        'step_6': True,
        'step_7': False
    }

    # 1. Get Country List
    if trigger['step_1']:
        save_country_list_to_csv(olympic_country_csv_path)
    else:
        print('step 1 - Get Country List - disabled')
    
    # 2. Get Olympic Games List
    if trigger['step_2']:
        save_olympic_games_list_to_csv(olympic_games_csv_path)
    else:
        print('step 2 - Get Olympic Games List - disabled')
    
    # 3. Get All athlete ids and their results
    # Warning: This will take a long time as it is looping through 233 countries and all the results page on each olympics they participated
    if trigger['step_3']:
        country_rows = olympic_scraper.get_countries_list()
        country_noc = [i[0] for i in country_rows]
        save_all_athlete_and_results_from_country_noc_to_csv(country_noc, olympic_athlete_event_results_csv_path)
    else:
        print('step 3 - Get All athlete ids and their results - disabled')

    #  4. Get Distinct Athlete ID and Event Information into new CSV Files
    if trigger['step_4']:
        get_distinct_athlete_and_events_from_athlete_event_csv(olympic_athlete_event_results_csv_path, distinct_athlete_id_csv_path, distinct_result_id_csv_path)
    else:
        print('step 4 - Get Distinct Athlete ID and Event Information into new CSV Files - disabled')   

    # 5. Get athlete bio information and results from all the events they parcipated in
    # Warning: This will take a long time as it is looping through 150,000 athlete pages
    if trigger['step_5']:
        with open(distinct_athlete_id_csv_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            athlete_ids = [item for row in csv_reader for item in row]
        get_athlete_bio_and_results_from_athlete_id_list(athlete_ids[1:], olympic_athlete_bio_csv_path, olympic_athlete_event_results_csv_path_2)
    else:
        print('step 5 - Get athlete bio information and results from all the events they parcipated in - disabled')   
    
    # 6. Saving country medal data from the Olympics_Games Csv file
    if trigger['step_6']:
        save_medel_results_to_csv(olympic_games_csv_path, olympic_games_medal_tally)
    else:
        print('step 6 - Saving country medal data from the Olympics_Games Csv file - disabled') 

    # 7. Download Results html into local repository
    # Warning: This will take a long time as it is looping through 8,000 events and downloading the html page
    if trigger['step_7']:
        with open(distinct_result_id_csv_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            event_ids = [item for row in csv_reader for item in row]
        download_result_html_to_path(event_ids[1:], raw_result_html_files_path)
    else:
        print('step 7 - Download Results html into local repository - disabled') 

    print('Olympedia Web Scrapping Completed')