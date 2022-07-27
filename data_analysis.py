# Date: 26 July 2022
# Purpose: To Perform Basic Analysis of whether data scrapped is correct or not

import pandas as pd

olympic_country_csv_path = 'data/Olympics_Country_test.csv'
olympic_games_csv_path = 'data/Olympics_Games_test.csv'
olympic_athlete_bio_csv_path = 'data/Olympic_Athlete_Bio_test.csv'
olympic_athlete_event_results_csv_path = 'data/Olympic_Athlete_Event_Results_test.csv'
olympic_athlete_event_results_csv_path_2 = 'data/Olympic_Athlete_Event_Results_test_2.csv'
distinct_athlete_id_csv_path = 'data/_distinct_athlete_id_csv_path_test.csv'
distinct_result_id_csv_path = 'data/_distinct_result_id_csv_path_test.csv'
raw_result_html_files_path = 'data/raw_result_html_files'

# 1. Analyse the event data and aggregate it to a medal level to check if the medal count matches
# Read in CSV File
olympic_athlete_event_results_df = pd.read_csv(olympic_athlete_event_results_csv_path)

# Perform Medal Count from the data
filtered_result_df = olympic_athlete_event_results_df[['edition', 'country_noc', 'sport', 'event', 'pos', 'medal']]
# Remove duplicates from team sports
filtered_result_df = filtered_result_df.drop_duplicates()
# Drop events where medals are not won
filtered_result_df = filtered_result_df.dropna(subset=['medal'])
# Remove sports, event, and position
filtered_result_df = filtered_result_df[['edition', 'country_noc', 'medal']]

grouped_result_df = filtered_result_df.groupby(['edition', 'country_noc', 'medal'], sort=True)['medal'].count()

# Save output to csv file
grouped_result_df.to_csv('test.csv')
print('the end')