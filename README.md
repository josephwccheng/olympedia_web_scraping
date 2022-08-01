# Olympedia Scraping Script

**Date**: 28/07/2022

**Author**: Joseph Cheng

**Programming Language**: Python3.8 and above

## Main Objective

Perform Web Scraping on the [olympedia website](http://www.olympedia.org/) to obtain data for Summer and Winter Olympics from 1896 to 2022 Winter Olympics. The main data extracted from the website include:

1. **Olympics Athelte Biological Information**
    1. **Headers:** athlete_id, name, sex, born, height, weight, country, country_noc, description, special_notes
    2. **File:** "Olympic_Athlete_Bio.csv"
2. **Olympics Games Medal Tally**
    1. **Headers:** edition, edition_id, year, country, country_noc, gold, silver, bronze, total
    2. **File:** "Olympic_Games_Medal_Talley.csv"
3. **Olympics Athlete Event Results**
    1. **Headers:** edition, country_noc, sport,event, result_id, athlete, athlete_id, pos, medal, isTeamSport
    2. **File:** "Olympic_Athlete_Event_Results.csv"
4. **Olympic Games List**
    1. **Headers:** games, edition_url, years, cities, start_date, end_date, competition_date, isHeld
    2. **File:** "Olympics_Games.csv"
<em>Note 1: All files are located in the data folder </em> 

<em>Note 2: This is inspired by [Kaggle: 120 years of Olympic history: athletes and results
](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results?resource=download)</em>

<em>Note 3: This project is for Non commercial purpose, the goal is to provide up to Olympics data for the open community to perform all sort of insights and analytics </em>

<em>Note 4: Multi-Threading and Multi-Processing is used in the main function to speed up the process of scraping multiple pages - This may or may not cause issues due to hardware limitation</em>


## How to Run ##
1. **Installing required python packages**
    1. **Run Command**: "pip install -Ur requirements.txt" or "make init"
2. **Configuration File** : configure config_file.py
    1. Contains file paths of where the CSV will be saved and stored
    2. Contains a "trigger" dictionary which will allow you to choose which steps of the main function to run - toggle the step to "True" to run the job, otherwise "False".
3. **Running the Main Code**
    
    Run "python main.py" or "make run" command

    **step 1** - Get Country List
        
        Obtains a list of Countries participated in the Olympics and Save it to "Olympics_Country.csv" file.

    **step 2** - Get Olympic Games List
        
        Obtains a list of Summer / Winter Olympics Games and Save it to "Olympics_Games.csv" file.

    **step 3** - Get All Athlete to Event Results from the Country List
        
        Obtains a list of Athlete to Event Results and Save it to "Olympic_Athlete_Event_Results.csv" file.

    **step 4** - Get Distinct Athlete ID and Event Information into new CSV Files
        
        From the "Olympic_Athlete_Event_Results.csv" file, obtain a distinct list of Atheletes and Results used to obtain Athlete bio and Results for Step 5. Files are saved as "_distinct_athlete_id.csv" and "_distinct_result_id.csv" respectively.

    **step 5** - Get athlete bio information and results from all the events they parcipated in
        
        From the "_distinct_athlete_id.csv" generated from Step 4, obtain all the ahlete's biological information and events that they participated in and save it in "Olympic_Athlete_Bio.csv" and "Olympic_Athlete_Event_Results_Athlete_Based.csv"

    **step 6** - Saving country medal data from the Olympics_Games Csv file

        Obtain Medal tallies of Olympic Games and Countries who has won gold, silver, and bronze medals and save it to "Olympic_Games_Medal_Tally.csv" file

    **step 7** - Download Results html into local repository

        Download Raw HTML files of all the results from the "_distinct_result_id.csv" file. This is a todo for future work for those who would like to dive down more on each specific events and their performances

    <em>Note: "Olympic_Athlete_Event_Results.csv" and "Olympic_Athlete_Event_Results_Athlete_Based.csv" have the same schema but is retrieved differently. One is derived from the Countries Page and another from all the Athlete's Page. It is recommended to use "Olympic_Athlete_Event_Results.csv" as it has been data validated.</em>

## Testing ##
    - Run "pytest" or make test to run unit tests

## Data Validation ##
    - Run "python data_validation.py" to run data validation on the "Olympic_Athlete_Event_Results.csv" file. The validation is run to ensure Event level data aggregated medal count matches with the Medal Tally provided by the source data.

## Issues Identified and Status of Fix ##
    1. Country list did not include "ROC" - Russian Olympic Committee, so the data was manually appended to the country list. (Temporary Hardcoded Fix)
    2. Issue with results page not listing all player for the sport: Monobob
        - for example: https://www.olympedia.org/countries/CAN/editions/62 did not list any players playing in the event on Monobob
        - (Temporary Hardcoded Fix)
    3. There is a 99.1% Match of the medal counts for the "Olympic_Athlete_Event_Results.csv" File. The mismatch is known for some rows between 1896 - 1924 Olympics Game because there were some events which allows "Mixed / Multiple" Countries and the mixed games should not contribute to the medal counts of the country. In our Script we assume them as a medal count and hence why there is a mismatch of data.
        - (Not Fixed)

## Future Work ##
    1. Create / Perform Exploratory Data Analysis on the dataset
    2. Creating Features for Machine Learning Models on the dataset

## Links and References used for this project
1. https://www.kaggle.com/code/heesoo37/olympic-history-data-a-thorough-analysis/report
2. https://medium.com/nerd-for-tech/data-exploration-of-historical-olympics-dataset-2d50a7d0611d
3. https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results?resource=download
4. https://github.com/UOSCS/Olympic_Athletes
5. https://medium.com/@lminhnguyen/winter-olympic-data-scraping-an-end-to-end-project-using-scrapy-6d064eb62e2e

## Links for Machine Learning Models Training Process
1. https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
2. https://katstam.com/regression-feature_importance/
3. https://www.kaggle.com/code/saxinou/imbalanced-data-xgboost-tunning
4. https://www.kaggle.com/code/carlosdg/xgboost-with-scikit-learn-pipeline-gridsearchcv/notebook
5. https://www.kaggle.com/code/alexisbcook/xgboost
6. https://towardsdatascience.com/understanding-feature-engineering-part-2-categorical-data-f54324193e63