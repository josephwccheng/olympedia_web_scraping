# Importing config files
from config_file import *
import pandas as pd
from datetime import datetime
import re

# Data Cleaning on the following Files Scrapped by Olympedia.org



# 1. Cleaning Olympic_Athlete_Bio.csv
# - Replace null values in all columns to 'na'
# - Convert all string date values to date objects (dd MONTH_String yyyy or just yyyy) to yyyy-mm-dd

def clean_olympic_athlete_bio():
    olympic_athlete_bio_df = pd.read_csv(olympic_athlete_bio_csv_path)
    olympic_athlete_bio_df.fillna('na', inplace=True)

    for index, row in olympic_athlete_bio_df.iterrows():
        born = row['born']
        pattern_year_only = re.compile('^\d\d\d\d$')
        pattern_day_month_year = re.compile('^[\d]* [a-zA-z]* [\d]*')
        pattern_month_year = re.compile('^[a-zA-z]* \d\d\d\d')

        if born == 'na':
            continue
        elif pattern_year_only.match(born): # when there's only the year they are born in - assume they are born in January 1st of the year
            date_object = datetime.strptime(born, '%Y').date()
            olympic_athlete_bio_df.loc[index, 'born'] = date_object
        elif pattern_day_month_year.match(born):
            date_object = datetime.strptime(born, '%d %B %Y').date()
            olympic_athlete_bio_df.loc[index, 'born'] = date_object
        elif pattern_month_year.match(born):
            date_object = datetime.strptime(born, '%B %Y').date()
        else:
            continue

        olympic_athlete_bio_df.loc[index, 'born'] = date_object
    # Save Dataframe to CSV file
    olympic_athlete_bio_df.to_csv(cleaned_olympic_athlete_bio_csv_path, index=False)

# 2. Cleaning Olympics_Games.csv
# - Replace null values in all columns to 'na'
# - coverting start_date, end_date to date objects (dd Month_String yyyy) to yyyy-mm-dd
# - converted competition_date to date obejects and created columns: competition_start_date and competition_end_date
def clean_olympic_games():
    olympic_games_df = pd.read_csv(olympic_games_csv_path)
    olympic_games_df.fillna('na', inplace=True)

    for index, row in olympic_games_df.iterrows():
        year = row['year']
        # start_date processing
        start_date = row['start_date']
        if start_date != 'na':
            if len(start_date.split()) == 2: # when the format of start_date is dd Month_String
                date_object = datetime.strptime(f'{start_date} {year}', '%d %B %Y').date()
                olympic_games_df.loc[index, 'start_date'] = date_object
            elif len(start_date.split()) == 3: # when the format is dd Month_String yyyy
                date_object = datetime.strptime(start_date, '%d %B %Y').date()
                olympic_games_df.loc[index, 'start_date'] = date_object
        # end_date processing
        end_date = row['end_date']
        if end_date != 'na':
            if len(end_date.split()) == 2: # when the format of start_date is dd Month_String
                date_object = datetime.strptime(f'{end_date} {year}', '%d %B %Y').date()
                olympic_games_df.loc[index, 'end_date'] = date_object
            elif len(end_date.split()) == 3: # when the format is dd Month_String yyyy
                date_object = datetime.strptime(start_date, '%d %B %Y').date()
                olympic_games_df.loc[index, 'end_date'] = date_object
        # competition_date processing
        competition_date = row['competition_date']
        if competition_date != 'na':
            comptition_date_list = competition_date.split()
            if len(comptition_date_list) == 5: # if competition_date is between different months
                date_object = datetime.strptime(f'{comptition_date_list[0]} {comptition_date_list[1]} {year}', '%d %B %Y').date()
                olympic_games_df.loc[index, 'competition_start_date'] = date_object
                date_object = datetime.strptime(f'{comptition_date_list[3]} {comptition_date_list[4]} {year}', '%d %B %Y').date()
                olympic_games_df.loc[index, 'competition_end_date'] = date_object
            elif len(comptition_date_list) == 4: # if competition_date are in the same month
                date_object = datetime.strptime(f'{comptition_date_list[0]} {comptition_date_list[3]} {year}', '%d %B %Y').date()
                olympic_games_df.loc[index, 'competition_start_date'] = date_object
                date_object = datetime.strptime(f'{comptition_date_list[2]} {comptition_date_list[3]} {year}', '%d %B %Y').date()
                olympic_games_df.loc[index, 'competition_end_date'] = date_object
    olympic_games_df.fillna('na', inplace=True)
    olympic_games_df = olympic_games_df.drop(columns=['competition_date'])
    olympic_games_df.to_csv(cleaned_olympic_games_csv_path, index=False)

# 3. Clean Olympic_Athlete_Event_Results.csv
# - fill in null values with na
def clean_olympic_athlete_event_results():
    olympic_athlete_event_results = pd.read_csv(olympic_athlete_event_results_csv_path)
    olympic_athlete_event_results.fillna('na', inplace=True)
    olympic_athlete_event_results.to_csv(cleaned_olympic_athlete_event_results_csv_path, index=False)

# 4. Clean Olympic_Events.csv
# - result_date: different underscore ' — ' This is for time (e.g. 23 February 2010 — 11:00), ' – ' This is for date (e.g. 11 – 12 August 1908 or 28 July –  6 August 2012)
# <TODO> Clean up the code and make it more modular
def clean_olympic_events():
    olympic_events_df = pd.read_csv(olympic_results_csv_path)
    for index, row in olympic_events_df.iterrows():
        result_date = row['result_date']
        start_date, end_date, time = ['na', 'na', 'na']
        time_splitter = ' — '
        date_range_splitter = ' – '
        if time_splitter in result_date: # result_date is time
            date, time = result_date.split(time_splitter)
            date_list = date.split()
            if len(date_list) == 3:
                start_date = datetime.strptime(date, '%d %B %Y').date()
            elif len(date_list) == 5: # if date list within the same month (e.g. 11 – 12 August 1908)
                date_object = datetime.strptime(f'{date_list[0]} {date_list[3]} {date_list[4]}', '%d %B %Y').date()
                start_date = date_object
                date_object = datetime.strptime(f'{date_list[2]} {date_list[3]} {date_list[4]}', '%d %B %Y').date()
                end_date = date_object
            elif len(date_list) == 6: # if competition_date are in different month (e.g. 28 July –  6 August 2012)
                date_object = datetime.strptime(f'{date_list[0]} {date_list[1]} {date_list[5]}', '%d %B %Y').date()
                start_date = date_object
                date_object = datetime.strptime(f'{date_list[3]} {date_list[4]} {date_list[5]}', '%d %B %Y').date()
        elif date_range_splitter in result_date: # result_date date range
            date_list = result_date.split()
            if len(date_list) == 5: # if date list within the same month (e.g. 11 – 12 August 1908)
                date_object = datetime.strptime(f'{date_list[0]} {date_list[3]} {date_list[4]}', '%d %B %Y').date()
                start_date = date_object
                date_object = datetime.strptime(f'{date_list[2]} {date_list[3]} {date_list[4]}', '%d %B %Y').date()
                end_date = date_object
            elif len(date_list) == 6: # if competition_date are in different month (e.g. 28 July –  6 August 2012)
                date_object = datetime.strptime(f'{date_list[0]} {date_list[1]} {date_list[5]}', '%d %B %Y').date()
                start_date = date_object
                date_object = datetime.strptime(f'{date_list[3]} {date_list[4]} {date_list[5]}', '%d %B %Y').date()
                end_date = date_object
        elif len(result_date.split()) == 3:
            start_date = datetime.strptime(result_date, '%d %B %Y').date()
        olympic_events_df.loc[index, 'start_date'] = start_date
        olympic_events_df.loc[index, 'end_date'] = end_date
        olympic_events_df.loc[index, 'time'] = time
    olympic_events_df = olympic_events_df.drop(columns=['result_date'])
    olympic_events_df.fillna('na', inplace=True)
    olympic_events_df.to_csv(cleaned_olympic_results_csv_path, index=False)
if __name__ == "__main__":
    clean_olympic_athlete_bio()
    clean_olympic_games()
    clean_olympic_athlete_event_results()
    clean_olympic_events()
    print('data cleaning done')