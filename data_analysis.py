# Purpose: To Perform Basic Analysis of whether data scrapped is correct or not

import pandas as pd

olympic_athlete_event_results_csv_path = 'data/Olympic_Athlete_Event_Results.csv'
olympic_games_medal_tally = 'data/Olympic_Games_Medal_Tally.csv'

# 1. Analyse the event data and aggregate it to a medal level to check if the medal count matches
# Read in CSV File
olympic_athlete_event_results_df = pd.read_csv(olympic_athlete_event_results_csv_path)

# Perform Medal Count from the data

filtered_result_df = olympic_athlete_event_results_df[['edition', 'country_noc', 'sport', 'event', 'pos', 'medal', 'isTeamSport']]
# Team results
team_results_df = filtered_result_df[filtered_result_df['isTeamSport'] == True]
# Remove duplicates from team results
team_results_df = team_results_df.drop_duplicates()

# Combing de-duplicated team results back
grouped_medal_count_result_df = filtered_result_df[filtered_result_df['isTeamSport'] == False]

grouped_medal_count_result_df = grouped_medal_count_result_df.append(team_results_df)
# Drop events where medals are not won
grouped_medal_count_result_df = grouped_medal_count_result_df.dropna(subset=['medal'])
# Remove sports, event, and position
grouped_medal_count_result_df = grouped_medal_count_result_df[['edition', 'country_noc', 'medal']]
grouped_medal_count_result_df = grouped_medal_count_result_df.groupby(['edition', 'country_noc', 'medal'], sort=True)['medal'].count().reset_index(name="medal_count")

# Creating a template of nulls and list of unique olympic games and country noc 
final_result_df = olympic_athlete_event_results_df[['edition', 'country_noc']].drop_duplicates()
default_medal_values = [0 for i in range(len(final_result_df))]
final_result_df['gold'] = default_medal_values
final_result_df['silver'] = default_medal_values
final_result_df['bronze'] = default_medal_values
final_result_df['total'] = default_medal_values

for _, row in grouped_medal_count_result_df.iterrows():
    condition = (final_result_df['edition'] == row['edition']) & (final_result_df['country_noc'] == row['country_noc'])
    final_result_df.loc[condition, row['medal'].lower()] = row['medal_count']

# Obtain total count from medal counts
for index, row in final_result_df.iterrows():
   final_result_df.loc[index, 'total']= row['bronze'] + row['silver'] + row['gold']

# Source of Trueth
source_of_truth_df = pd.read_csv(olympic_games_medal_tally)

matched = 0
un_matched = 0
for index, row in source_of_truth_df.iterrows():
    agg_row = final_result_df[(final_result_df['edition'] == row['edition']) & (final_result_df['country_noc'] == row['country_noc'])]
    if len(agg_row) == 0:
        print(f"{row['edition']} - {row['country_noc']} - row not found")
        continue
    if agg_row['gold'].values[0] != row['gold']:
        un_matched = un_matched + 1
        print(f"{row['edition']} - {row['country_noc']} - gold - does not match")
        continue
    if agg_row['silver'].values[0] != row['silver']:
        un_matched = un_matched + 1
        print(f"{row['edition']} - {row['country_noc']} - silver - does not match")
        continue
    if agg_row['bronze'].values[0] != row['bronze']:
        un_matched = un_matched + 1
        print(f"{row['edition']} - {row['country_noc']} - bronze - does not match")
        continue
    matched = matched + 1

percent_medal_match = "{:.2f}".format(100 * matched / (matched + un_matched))

print(f'{percent_medal_match}% of matches on medal counts')

# Save output to csv file
# final_result_df.to_csv('data/_aggregated_medal_tally_from_athlete_event_results.csv', index=False)
print('End of Data Validation')