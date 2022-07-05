Olympedia Scraping Script
Date: 28/07/2022
Author: Joseph

Base URL: http://www.olympedia.org/
Language: Python3 3.8 and above

Main Objective
1. Table of all of Olympics Games
2. Table of all active partipating countries
3. Table of all distinct athelete's id
4. (Goal) Table of all players participating in the sporting event
    - Include position/rank for each sporting event
5. (Extension) Tables of all sporting events and their unique table schema
    - Tables will have different schemas based on different sports

Complexity
- Each Event's Result table will be different based on the sport (i.e. Swimming contains Time Complete, Pentathlon contains Point, Fencing, Swimming, Riding, and Running & Shooting)

Key Data to Obtain
- Position for each event (Pos) - Value from 1 - N


Main Object 1 - Table of all Olympics games

Main Object 2 - Table of all distinct partipating countries



Steps 1 - Get the list of all atheletes who participated in olympics:
1. List down all the countries that participates in modern olympics from https://www.olympedia.org/countries
    1.1. URL provides list of countries and their details in the extension of their country accrynom i.e. countries/USA
        1.1.1. Focusing on the <h2>Participations by edition</h2><h3>Olympic Games</h3>
    1.2. First Column "Edition" includes: <yyyy> <Season> Olympics
        1.2.1. Last Column "Results" href contains extension i.e. countries/USA/editions/<id>
        1.2.2. countries/USA/editions/<id> contains:
            sport (h2)
            event (href containing /results/<id>)
            participant (href containing /athleet/<id>)
            ranking (third td)
            medal (Gold, Silver, Bronze, or none)
2. Get the Host Country from the Olympics Event
    2.1. List of all the Olympics games from https://www.olympedia.org/editions
    2.2. Concat to get the year and season (Summer or Winter) as key and the host city as the value
3. From step 1, 


Meta Data for olympedia endpoints
    Base URL: http://www.olympedia.org/
- /countries
    - Abbreviation, Country, Competed in Modern Olympics
- /countries/<Country Abbreviation>
    - Edition, As, Men, Women, Total, Results
        - Edition - <yyyy> <Season> Olympics
-  /countries/<Country Abbreviation>/editions/<Index>
    - Sport, Athelete, Rank, Medal
- /athletes/<Player ID>


Meta Data for Kaggle Dataset (All players particiating in the sporting event)
    - ID,Name,Sex,Age,Height,Weight,Team,NOC,Games,Year,Season,City,Sport,Event,Medal
    - Limitation - medal only contains gold, silver, bronze

Other useful links:
1. https://www.kaggle.com/code/heesoo37/olympic-history-data-a-thorough-analysis/report
2. https://medium.com/nerd-for-tech/data-exploration-of-historical-olympics-dataset-2d50a7d0611d
3. https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results?resource=download
4. https://github.com/UOSCS/Olympic_Athletes
5. https://medium.com/@lminhnguyen/winter-olympic-data-scraping-an-end-to-end-project-using-scrapy-6d064eb62e2e



