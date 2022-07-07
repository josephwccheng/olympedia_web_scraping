# Olympedia Scraping Script

**Date**: 28/07/2022

**Author**: Joseph

**Base URL**: http://www.olympedia.org/

**Programming Language**: Python3.8 and above

## Main Objective

Perform web scraping on the olympedia website to obtain information on the olympics events and player level events

1. Table of all of Olympics Games (i.e. 2020 Summer Olympics, Tokyo)
2. Table of all active partipating countries (i.e. USA, United States)
3. Table of all athletes and their biography (i.e. DOB, sex, country)
3. Table of all athletes participating in each sporting event in each olympics
5. (Extension) Tables of all sporting events and their unique table schema
    - Each Event's Result table will have different schema based on the sport (i.e. Swimming contains Time Complete, Pentathlon contains Point, Fencing, Swimming, Riding, and Running & Shooting)

## Logical Approach
1. Obtain a list of countries and their NOC from the olympedia's /countries endpoint
2. Obtain all the player list from the Results link from the olympedia's /countries endpoint
    - Each result link is corresponded to each olympic game
    - result link includes a list of all athletes particiapted on the specific olympic game divided into different sporting categories
    - de-duplicate the athlete to obtain an unique list of 
3. Loop through the countries list and obtain all the athletes from step 2
4. From receiving a distinct list of all the athletes id, use the /athletes/athlete_id endpoint to obtain bio information and all the events the athlete has participated in
5. (Optional) Create the tables and store them into CSV file

## Meta Data for olympedia endpoints
- /countries
    - Abbreviation, Country, Competed in Modern Olympics
- /countries/Country_Noc
    - Edition, As, Men, Women, Total, Results
        - Edition - yyyy Season Olympics
-  /countries/Country_Noc>/editions/Index
    - Sport, Athelete, Rank, Medal
- /athletes/athlete_id

## Meta Data for Kaggle Dataset
- ID,Name,Sex,Age,Height,Weight,Team,NOC,Games,Year,Season,City,Sport,Event,Medal
- Limitation - medal only contains gold, silver, bronze

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