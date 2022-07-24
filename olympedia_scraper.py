from bs4 import BeautifulSoup
from typing import List, Dict
from olympedia_client import OlympediaClient
import re

SINGLE_ATHLETE_COLUMN_COUNT = 4
MULTI_ATHLETE_COLUMN_COUNT = 2

class OlympediaScraper():
    def __init__(self):
        self.olympedia_client = OlympediaClient()

    # 1. Get Table of all active partipating countries
    # Output Format: [[country_noc, country_name], ... ]
    def get_country_list(self) -> List[list]:
        countries_page = self.olympedia_client.get_request_content('/countries', 'get countries list')
        countries_soup = BeautifulSoup(countries_page, 'html.parser')
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
    def get_olympics_games(self) -> List[list]:
        games_page = self.olympedia_client.get_request_content('/editions', 'get Olympic games list')
        games_soup = BeautifulSoup(games_page, 'html.parser')
        
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
    def get_event_athletes_results_from_country(self, country_noc: str):
        country_page = self.olympedia_client.get_request_content('/countries/' + country_noc, 'get event athletes results from Country noc')
        country_soup = BeautifulSoup(country_page, 'html.parser')
        olympic_table = country_soup.select_one('body > div.container > table:nth-child(11)')
        if olympic_table is None:
            return
        # Get a list of results url for each Edition based on country
        result_extensions = [olympic['href'] for olympic in olympic_table.select('tbody > tr > td:nth-child(6) > a')]
        editions = [edition.text for edition in olympic_table.select('tbody > tr > td:nth-child(1) > a')]
        event_athletes = []
        for edition, result_extension in zip(editions,result_extensions):
            event_athletes.extend(self._get_event_athlete_from_result_url(result_extension, edition, country_noc))
        return event_athletes

    # <Helper Function>
    # Get event, athlete information from the result page
    def _get_event_athlete_from_result_url(self, result_extension: str, edition: str="", country_noc: str=""):
        result_page = self.olympedia_client.get_request_content(result_extension, 'get event athlete from result url')
        result_soup = BeautifulSoup(result_page, 'html.parser')
        result_table = result_soup.select_one('table')
        result_rows = result_table.find_all("tr")
        
        event_athletes = []
        sport = ""
        event = ""
        event_url = ""
        pos =""
        medal = ""
        for row in result_rows:
            isAthlete = False
            athlete = ""
            athlete_url = ""
            if row.h2:
                sport = row.h2.text
                continue
            else:
                row_elements = row.find_all("td")
                if len(row_elements) == SINGLE_ATHLETE_COLUMN_COUNT or len(row_elements) != MULTI_ATHLETE_COLUMN_COUNT: # Row containing single athlete or header of multiple athletes
                    if row_elements[0].find('a'): #First column: event information
                        event = row_elements[0].find('a').text
                        event_url = row_elements[0].find('a')['href']
                    if row_elements[1].find('a'): #Second column: athlete information
                        athlete = row_elements[1].find('a').text
                        athlete_url = row_elements[1].find('a')['href']
                        isAthlete = True
                    if row_elements[2].text != "": #Third column: Position information
                        pos = row_elements[2].text
                    #Fourth column: Medal information
                    medal = row_elements[3].text
                    if isAthlete:
                        event_athletes.append(
                            {
                                "edition": edition,
                                "country_noc": country_noc,
                                "sport": sport,
                                "event": event,
                                "event_id": event_url.split('/')[2],
                                "athlete": athlete,
                                "athlete_id": athlete_url.split('/')[2],
                                "pos": pos,
                                "medal": medal,
                                "isTeamSport": False
                            }
                        )
                elif len(row_elements) == MULTI_ATHLETE_COLUMN_COUNT: # Row containing multiple athletes
                    multi_athletes = row_elements[1].find_all('a')
                    for multi_athlete in multi_athletes:
                        event_athletes.append(
                            {
                                "edition": edition,
                                "country_noc": country_noc,
                                "sport": sport,
                                "event": event,
                                "event_id": event_url.split('/')[2],
                                "athlete": multi_athlete.text,
                                "athlete_id": multi_athlete['href'].split('/')[2],
                                "pos": pos,
                                "medal": medal,
                                "isTeamSport": True
                            }
                        )
        return event_athletes

    # Get athlete's biography from athlete's url
    def get_bio_and_results_from_athlete_id(self, athlete_id: str):
        athlete_page = self.olympedia_client.get_request_content('/athletes/' + athlete_id, 'get bio and results from athlete_id')
        athlete_soup = BeautifulSoup(athlete_page, 'html.parser')
        
        # Obtaining athlete bio info
        athlete_bio_info = self._process_athlete_bio(athlete_id, athlete_soup)
        
        # Populating a table of all the game the athele participated in and their position / medal
        result_table = athlete_soup.find_all('h2', string='Results')[0].find_next()
        athlete_results = self._process_athlete_result_table(athlete_id, result_table)
        return { 'athlete_bio_info': athlete_bio_info, 'athlete_results': athlete_results }

    # <Helper Function>
    def _process_athlete_bio(self, athlete_id:str, athlete_soup) -> Dict:
        bio_keys_items = athlete_soup.select('body > div.container > table.biodata > tr > th')
        bio_values_items = athlete_soup.select('body > div.container > table.biodata > tr > td')
        description = athlete_soup.select('body > div.container > div.description')
        special_notes = athlete_soup.select('body > div.container > ul > li')
        keys_bio = [item.get_text() for item in bio_keys_items]
        values_bio = [item.get_text() for item in bio_values_items]
        raw_athlete_bio_info = {keys_bio[i]: values_bio[i] for i in range(len(keys_bio))}
        noc = athlete_soup.find('th', string='NOC').find_next()
        athlete_bio_info = {
            'athlete_id': athlete_id,
            'name': re.sub('[^0-9a-zA-Z]+', ' ', raw_athlete_bio_info.get('Used name')),
            'sex': raw_athlete_bio_info.get('Sex'),
            'born': '',
            'height': '',
            'weight': '',
            'country': raw_athlete_bio_info.get('NOC'),
            'country_noc': noc.select('a')[0]['href'].split('/')[2],
            'description': '',
            'special_notes': ''
        }

        if raw_athlete_bio_info.get('Born') is not None:
            athlete_bio_info['born'] = raw_athlete_bio_info.get('Born').split(' in ')[0]
        
        if raw_athlete_bio_info.get('Measurements') is not None:
            measurement = raw_athlete_bio_info.get('Measurements').split(' / ')
            if len(measurement) > 1:
                athlete_bio_info['height'] = measurement[0].split(' cm')[0]
                athlete_bio_info['weight'] = measurement[1].split(' kg')[0]
        
        if description:
            athlete_bio_info['description'] = " ".join(description[0].text.split())
        else:
            athlete_bio_info['description'] = ""
        
        if special_notes:
            athlete_bio_info['special_notes'] = " ".join([" ".join(i.text.split()) for i in special_notes])
        else:
           athlete_bio_info['special_notes'] = ""
        
        return athlete_bio_info

    # <Helper Function>
    def _process_athlete_result_table(self, athlete_id:str, result_table) -> List[Dict]:
        
        edition_items = result_table.select('table.table > tbody > tr > td:nth-child(1)')
        sport_items = result_table.select('table.table > tbody > tr > td:nth-child(2) > a:nth-child(1)')
        noc_items = result_table.select('table.table > tbody > tr > td:nth-child(3)')
        pos_items = result_table.select('table.table > tbody > tr > td:nth-child(4)')
        medal_items = result_table.select('table.table > tbody > tr > td:nth-child(5)')
        name_items = result_table.select('table.table > tbody > tr > td:nth-child(6)')
        # Create & Insert athlete info
        olympic_games = [item.get_text() for item in edition_items]
        disciplines = [item.get_text() for item in sport_items]
        results_ids = [item['href'].split('/')[2] for item in sport_items]

        noc = [item.get_text() for item in noc_items] 
        pos = [item.get_text() for item in pos_items]
        medals = [item.get_text() for item in medal_items]
        name = [item.get_text() for item in name_items]
        athlete_results = []
        # Getting the olympic games and sport
        cur_olympic_game = ''
        cur_dicipline = ''
        cur_noc = ''
        cur_name = ''
        for i in range(len(olympic_games)):
            if olympic_games[i].strip() != '':
                cur_olympic_game = olympic_games[i].strip()
                cur_dicipline = disciplines[i]
                cur_noc = noc[i]
                cur_name = name[i]
            else:
                event_result = {
                    'edition': cur_olympic_game,
                    'country_noc': cur_noc,
                    'sport': cur_dicipline,
                    'event': disciplines[i],
                    'result_id': results_ids[i],
                    'athlete': cur_name,
                    'athlete_id': athlete_id,
                    'pos': pos[i],
                    'medals': medals[i]
                }
                athlete_results.append(event_result)
        return athlete_results

    def get_html_from_result_id(self, result_id: str):
        result_page = self.olympedia_client.get_request_content('/results/' + result_id, 'get html from result id')
        result_soup = BeautifulSoup(result_page, 'html.parser')
        return result_soup.prettify('utf-8')
