from bs4 import BeautifulSoup
from typing import List, Dict
from olympedia_client import OlympediaClient
import re
import bs4

SINGLE_ATHLETE_COLUMN_COUNT = 4
MULTI_ATHLETE_COLUMN_COUNT = 2

class OlympediaScraper():
    def __init__(self):
        self.olympedia_client = OlympediaClient()

    # 1. Get Table of all active partipating countries
    # Output Format: [[country_noc, country_name], ... ]
    def get_countries_list(self) -> List[list]:
        countries_page = self.olympedia_client.get_all_countries_page()
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
        games_page = self.olympedia_client.get_all_editions_page()
        games_soup = BeautifulSoup(games_page, 'html.parser')
        
        summer_table = games_soup.select_one('body > div.container > table:nth-child(5)')
        summer_extracted = self._extract_content_from_editions_table(summer_table, 'Summer Olympics')
        winter_table = games_soup.select_one('body > div.container > table:nth-child(7)')
        winter_extracted = self._extract_content_from_editions_table(winter_table, 'Winter Olympics')

        games = summer_extracted['games'] + winter_extracted['games']
        edition_urls = summer_extracted['edition_urls'] + winter_extracted['edition_urls']
        years = summer_extracted['years'] + winter_extracted['years']
        cities = summer_extracted['cities'] + winter_extracted['cities']
        countries_flag_url = summer_extracted['countries_flag_url'] + winter_extracted['countries_flag_url']
        countries_noc = summer_extracted['countries_noc'] + winter_extracted['countries_noc']
        start_date = summer_extracted['start_date'] + winter_extracted['start_date']
        end_date = summer_extracted['end_date'] + winter_extracted['end_date']
        competition_date = summer_extracted['competition_date'] + winter_extracted['competition_date']
        isHeld = summer_extracted['isHeld'] + winter_extracted['isHeld']

        return [[games[i], edition_urls[i], years[i], cities[i], countries_flag_url[i], countries_noc[i], start_date[i], end_date[i], competition_date[i], isHeld[i]] for i in range(len(years))]

    # Helper function for get_olympics game
    def _extract_content_from_editions_table(self, editions_table: bs4.element.Tag, season_olympics:str = ""):
        edition_url = [item['href'] for item in editions_table.select('tr > td:nth-child(2) > a')]
        years = [item.get_text() for item in editions_table.select('tr > td:nth-child(2)')]
        games = [item + f' {season_olympics}' for item in years]
        cities = [item.get_text() for item in editions_table.select('tr > td:nth-child(3)')]
        countries_flag_url = [item['src'] for item in editions_table.select('tr > td:nth-child(4) > img')]
        countries_noc = [item.split('/')[-1].split('.')[0] for item in  countries_flag_url]
        start_date = [item.get_text() for item in editions_table.select('tr > td:nth-child(5)')]
        end_date = [item.get_text() for item in editions_table.select('tr > td:nth-child(6)')]
        competition_date = [item.get_text() for item in editions_table.select('tr > td:nth-child(7)')]
        isHeld = [item.get_text().strip() for item in editions_table.select('tr > td:nth-child(8)')]

        return {'edition_urls': edition_url, 'years': years, 'games': games, 'cities': cities, 'countries_flag_url': countries_flag_url, 'countries_noc': countries_noc, 'start_date': start_date, 'end_date': end_date, 'competition_date': competition_date, 'isHeld': isHeld}

    # 3. Table of all distinct players
    # Input: country noc
    # Output: list of players who played for the ocuntry
    # Filters: year_filter - 4 digit year and it will obtain only the olympics from that year onwards
    #          season_filter - 'all', 'winter' or 'summer'
    def get_event_athletes_results_from_country(self, country_noc: str, year_filter: str='all', season_filter: str='all'):
        # Input Filter Check
        year_filter_flag = False
        season_filter_flag = False
        if len(year_filter) == 4 and year_filter.isdigit():
            year_filter_flag = True
        elif year_filter != 'all':
            raise ValueError(
                "year_filter value incorrect. It must be a 4 digit number or all."
            )
        if season_filter.lower() == 'winter' or season_filter.lower() == 'summer':
            season_filter_flag = True
        elif season_filter.lower() != 'all':
            raise ValueError(
                "season_filter value incorrect. It must be either summer, winter or all."
            )            

        country_page = self.olympedia_client.get_country_page(country_noc)
        country_soup = BeautifulSoup(country_page, 'html.parser')
        olympic_table = country_soup.find('h2', string='Participations by edition').find_next().find_next()
        if olympic_table is None or olympic_table.name != 'table':
            return
        # Get a list of results url for each Edition based on country
        result_extensions = [olympic['href'] for olympic in olympic_table.select('tbody > tr > td:nth-child(6) > a')]
        editions = [edition.text for edition in olympic_table.select('tbody > tr > td:nth-child(1) > a')]
        event_athletes = []
        for edition, result_extension in zip(editions,result_extensions):
            year, season, _ = edition.split()
            country_result_index = result_extension.split('/')[4]
            if year_filter_flag == True and season_filter_flag == True:
                if int(year) >= int(year_filter) and season_filter.lower() == season.lower():
                    event_athletes.extend(self._get_event_athlete_from_result_url(country_noc, country_result_index, edition))
            elif year_filter_flag == True and season_filter_flag == False:
                if int(year) >= int(year_filter):
                    event_athletes.extend(self._get_event_athlete_from_result_url(country_noc, country_result_index, edition))
            elif year_filter_flag == False and season_filter_flag == True:
                if season_filter.lower() == season.lower():
                    event_athletes.extend(self._get_event_athlete_from_result_url(country_noc, country_result_index, edition))
            else:
                event_athletes.extend(self._get_event_athlete_from_result_url(country_noc, country_result_index,edition))
        return event_athletes

    # <Helper Function>
    # Get event, athlete information from the result page
    def _get_event_athlete_from_result_url(self, country_noc: str="", country_result_index: str="", edition: str=""):
        result_page = self.olympedia_client.get_country_olympic_results_page(country_noc=country_noc, index=country_result_index)
        result_soup = BeautifulSoup(result_page, 'html.parser')
        result_table = result_soup.select_one('table')
        result_rows = result_table.find_all("tr")
        
        event_athletes = []
        sport, event, event_url, pos, medal = "", "", "", "", ""
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
        athlete_page = self.olympedia_client.get_athlete_page(athlete_id)
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
        result_page = self.olympedia_client.get_result_page(result_id)
        result_soup = BeautifulSoup(result_page, 'html.parser')
        return result_soup.prettify('utf-8')

    def get_medal_table_from_editions_id(self, editions_id):
        medal_page = self.olympedia_client.get_edition_page(editions_id)
        medal_soup = BeautifulSoup(medal_page, 'html.parser')
        medal_table = medal_soup.find_all('h2', string='Medal table')
        
        if len(medal_table) > 0:
            medal_table = medal_table[0].find_next()
            country_items = [item.get_text()for item in medal_table.select('table.table > tr > td:nth-child(1)')]
            noc_items = [item.get_text().lstrip() for item in medal_table.select('table.table > tr > td:nth-child(2)')]
            gold_items = [item.get_text() for item in medal_table.select('table.table > tr > td:nth-child(3)')]
            silver_items = [item.get_text() for item in medal_table.select('table.table > tr > td:nth-child(4)')]
            bronze_items = [item.get_text() for item in medal_table.select('table.table > tr > td:nth-child(5)')]
            total_items = [item.get_text() for item in medal_table.select('table.table > tr > td:nth-child(6)')]
            return {'country':country_items, 'noc':noc_items, 'gold': gold_items, 'silver':silver_items, 'bronze': bronze_items, 'total': total_items}
        else:
            return {}
    
    def get_result_info_from_result_id(self, result_id : str) -> dict:
        # <BUG Fix> - Results 18001004, 18001046, 18001088 have 500 error code
        # <TODO> - Change the logic on how the results info is retrieved rom results page
        if result_id not in ['18001004', '18001046', '18001088']:
            result_page = self.olympedia_client.get_result_page(result_id)
            result_soup = BeautifulSoup(result_page, 'html.parser')

            breadcrumb = result_soup.select('body > div.container > ol.breadcrumb > li')
            edition = breadcrumb[2].get_text()
            sport = breadcrumb[3].get_text()
            sport_url = breadcrumb[3].select('a')[0]['href']
            event_title = result_soup.select('body > div.container > h1.event_title')[0].get_text()

            event_bio_table = result_soup.select('body > div.container > table.biodata')[0]
            event_bio_header = [item.get_text() for item in event_bio_table.select('table > tr > th')]
            event_bio_value = [item.get_text() for item in event_bio_table.select('table > tr > td')]
            result_date, result_location, result_participants,result_format, result_description, result_detail = ['na' for i in range(6)]

            if 'Date' in event_bio_header:
                result_date = event_bio_value[event_bio_header.index('Date')]
            if 'Location' in event_bio_header:
                result_location = event_bio_value[event_bio_header.index('Location')]
            if 'Participants' in event_bio_header:
                result_participants = event_bio_value[event_bio_header.index('Participants')]
            if 'Format' in event_bio_header:
                result_format = event_bio_value[event_bio_header.index('Format')]
            if 'Details' in event_bio_header:
                result_detail = event_bio_value[event_bio_header.index('Details')]
            
            if len(result_soup.select('body > div.container > div.description')) > 0:
                result_description = result_soup.select('body > div.container > div.description')[0].get_text()
            return {'result_id': result_id, 'event_title': event_title, 'edition': edition, 'sport': sport, 'sport_url':sport_url, 'result_date': result_date, 'result_location': result_location, 'result_participants': result_participants, 'result_format': result_format, 'result_detail': result_detail, 'result_description': result_description}
        else:
            return None