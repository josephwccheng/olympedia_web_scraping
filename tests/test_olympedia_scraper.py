from olympedia_scraper import OlympediaScraper
from mockito import when
import unittest
from tests.resources import mock_athletes

class TestOlympediaScraper(unittest.TestCase):
    def test_get_countries_list(self):
        olympedia_scraper = OlympediaScraper()
        # MOCK HTML Response
        COUNTRIES_HTML_PATH = "tests/resources/countries_page.html"
        with open(COUNTRIES_HTML_PATH, "r") as f:
            country_html = f.read()
        when(olympedia_scraper.olympedia_client).get_all_countries_page().thenReturn(
            country_html
        )
        expected_result = [['AFG', 'Afghanistan'], ['ALB', 'Albania'], ['ALG', 'Algeria'], ['ASA', 'American Samoa']]
        
        result = olympedia_scraper.get_countries_list()
        assert result == expected_result

    def test_get_olympics_games(self):
        olympedia_scraper = OlympediaScraper()
        # MOCK HTML Response
        EDITIONS_HTML_PATH = "tests/resources/editions_page.html"
        with open(EDITIONS_HTML_PATH, "r") as f:
            editions_html = f.read()
        when(olympedia_scraper.olympedia_client).get_all_editions_page().thenReturn(
            editions_html
        )
        result = olympedia_scraper.get_olympics_games()
        assert result[0] == ['1996 Summer Olympics', '24', '/editions/24', 'Summer', '1996', 'Atlanta', '/images/flags/USA.png', 'USA', '19 July', ' 4 August', '20 July –  4 August', '']

    def test_get_event_athletes_results_from_country(self):
        olympedia_scraper = OlympediaScraper()
        country_noc = 'AUS'
        # MOCK HTML Response
        AUS_HTML_PATH = "tests/resources/AUS_page.html"
        AUS_2020_SUMMER_PATH = "tests/resources/AUS_2020_Summer_page.html"
        AUS_2022_WINTER_PATH = "tests/resources/AUS_2022_Winter_page.html"
        with open(AUS_HTML_PATH, "r") as f: 
            aus_html = f.read()
        with open(AUS_2020_SUMMER_PATH, "r") as f:
            aus_2020_summer_html = f.read()
        with open(AUS_2022_WINTER_PATH, "r") as f:
            aus_2022_winter_html = f.read()

        when(olympedia_scraper.olympedia_client).get_country_page(country_noc).thenReturn(
            aus_html
        )
        when(olympedia_scraper.olympedia_client).get_country_olympic_results_page(country_noc='AUS',index='61').thenReturn(
            aus_2020_summer_html
        )
        when(olympedia_scraper.olympedia_client).get_country_olympic_results_page(country_noc='AUS',index='62').thenReturn(
            aus_2022_winter_html
        )

        result = olympedia_scraper.get_event_athletes_results_from_country('AUS')
        assert result[0] == {'edition': '2020 Summer Olympics', 'edition_id': '61', 'country_noc': 'AUS', 'sport': 'Archery', 'event': 'Individual, Men', 'event_id': '18000492', 'athlete': 'Taylor Worth', 'athlete_id': '121560', 'pos': '=9', 'medal': '', 'isTeamSport': False}
    
        # Testing filters for year and season
        result_all = olympedia_scraper.get_event_athletes_results_from_country(country_noc='AUS', year_filter = 'all', season_filter ='all')
        assert result_all == result
        result_year = olympedia_scraper.get_event_athletes_results_from_country(country_noc='AUS', year_filter = '2022', season_filter ='all')
        assert result_year[0]['edition'] == '2022 Winter Olympics'
        result_season = olympedia_scraper.get_event_athletes_results_from_country(country_noc='AUS', year_filter = 'all', season_filter ='summer')
        assert result_season[0]['edition'] == '2020 Summer Olympics'

    def test_get_bio_and_results_from_athlete_id(self):
        olympedia_scraper = OlympediaScraper()
        michael_phelps_id = '93860'
        result = olympedia_scraper.get_bio_and_results_from_athlete_id(michael_phelps_id)
        athlete_bio = result['athlete_bio_info']
        athlete_results = result['athlete_results']
        assert athlete_bio['athlete_id'] == mock_athletes.MICHAEL_PHELPS_BIO['athlete_id']
        assert athlete_results[0]['athlete_id'] == michael_phelps_id
    
    def test_get_medal_table_from_editions_id(self):
        olympedia_scraper = OlympediaScraper()
        tokyo_olympics_2020_id = '61'
        TOKYO_2020_OLYMPICS_EDITION_PATH = "tests/resources/2020_summer_olympics_editions_page.html"
        with open(TOKYO_2020_OLYMPICS_EDITION_PATH, "r") as f: 
            tokyo_2020_edition_html = f.read()

        when(olympedia_scraper.olympedia_client).get_edition_page(tokyo_olympics_2020_id).thenReturn(
            tokyo_2020_edition_html
        )

        medal_table = olympedia_scraper.get_medal_table_from_editions_id(tokyo_olympics_2020_id)
        assert medal_table['country'][0] == 'United States'
        assert medal_table['noc'][0] == 'USA'
        assert medal_table['gold'][0] == '39'
        assert medal_table['silver'][0] == '41'
        assert medal_table['bronze'][0] == '33'
        assert medal_table['total'][0] == '113'
    
    def test_get_result_info_from_result_id(self):
        olympedia_scraper = OlympediaScraper()
        SAMPLE_RESULT_ID = '8466'
        result_info = olympedia_scraper.get_result_info_from_result_id(SAMPLE_RESULT_ID)
        assert result_info['edition_id'] == '25'
        assert result_info['sport'] == 'Swimming'
if __name__ == '__main__':
    unittest.main()