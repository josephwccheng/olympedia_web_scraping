from olympedia_scraping import OlympediaScraper
from os.path import exists
import multiprocessing
import csv
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

if __name__ == "__main__":

    olympic_scraper = OlympediaScraper()

    olympic_country_csv_path = 'data/Olympics_Country.csv'
    olympic_games_csv_path = 'data/Olympics_Games.csv'
    olympic_athlete_id_csv_path = 'data/Olympic_Athlete_id.csv'
    olympic_athlete_bio_csv_path = 'data/Olympic_Athlete_Bio.csv'
    olympic_athlete_event_results_csv_path = 'data/Olympic_Athlete_Event_Results.csv'

    # 1. Get Country List
    country_rows = olympic_scraper.get_country_list()
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
        games_rows = olympic_scraper.get_olympics_games()
        games_header = ['games', 'years', 'cities', 'start_date', 'end_date', 'held']
        with open(olympic_games_csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(games_header)
            writer.writerows(games_rows)
    else:
        print('Olympic_Games.csv file already exist')

    # # 3. Get All athlete ids and their results
    # country_noc = [i[0] for i in country_rows]
    # if multiprocessing.cpu_count() > 0:
    #     cpu_count = multiprocessing.cpu_count()
    # else:
    #     cpu_count = 5
    # print(f'detected {cpu_count} cpu cores')
    # with Pool(processes=cpu_count) as p:
    #     country_athlete_ids = list(tqdm(p.imap(olympic_scraper.get_athlete_id_from_country, country_noc), total=len(country_noc), desc= 'processing multiple countries to retrieve athlete ids'))
    # athlete_ids_output = set()
    # for athlete_ids in country_athlete_ids:
    #     if athlete_ids is not None:
    #         athlete_ids_output.update(athlete_ids)
    # with open(olympic_athlete_id_csv_path, 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(['athlete_id'])
    #     for athlete_id in athlete_ids_output:
    #         writer.writerow([athlete_id])

    # # 4. Get athelete bio information and results from all the events they parcipated in
    # with open(olympic_athlete_id_csv_path) as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #     athlete_ids = [item for row in csv_reader for item in row]

    # if multiprocessing.cpu_count() > 0:
    #     cpu_count = multiprocessing.cpu_count()
    # else:
    #     cpu_count = 5
    # print(f'detected {cpu_count} cpu cores')
    # with Pool(processes=cpu_count) as p:
    #     athletes_bio_and_results = list(tqdm(p.imap(olympic_scraper.get_bio_and_results_from_athlete_id, athlete_ids[1:]), total=len(athlete_ids[1:]), desc= 'processing athlete ids to obtain bio and results information'))
    
    # bio_header = ['athlete_id', 'name', 'sex', 'born', 'height', 'weight', 'noc']
    # events_header = ['athlete_id','olympic_game', 'dicipline', 'event', 'noc', 'pos', 'medals']
    # with open(olympic_athlete_bio_csv_path, 'w') as f_bio, open(olympic_athlete_event_results_csv_path,'w') as f_events:
    #     writer_bio = csv.writer(f_bio)
    #     writer_events = csv.writer(f_events)
    #     writer_bio.writerow(bio_header)
    #     writer_events.writerow(events_header)
    #     for athlete_bio_and_results in athletes_bio_and_results:
    #         athlete_bio = athlete_bio_and_results['athelete_bio_info']
    #         writer_bio.writerow(list(athlete_bio.values()))
    #         athlete_results = athlete_bio_and_results['athelete_results']
    #         for athlete_result in athlete_results:
    #             writer_events.writerow(list(athlete_result.values()))