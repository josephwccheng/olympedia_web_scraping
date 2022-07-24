from olympedia_scraper import OlympediaScraper
from mockito import when
import unittest
from tests.resources import mock_athletes

class TestOlympediaScraper(unittest.TestCase):
    def test_get_country_list(self):
        olympedia_scraper = OlympediaScraper()
        # MOCK HTML Response
        COUNTRIES_HTML_PATH = "tests/resources/countries_page.html"
        with open(COUNTRIES_HTML_PATH, "r") as f:
            country_html = f.read()
        when(olympedia_scraper.olympedia_client).get_request_content('/countries', 'get countries list').thenReturn(
            country_html
        )
        expected_result = [['AFG', 'Afghanistan'], ['ALB', 'Albania'], ['ALG', 'Algeria'], ['ASA', 'American Samoa']]
        
        result = olympedia_scraper.get_country_list()
        assert result == expected_result

    def test_get_olympics_games(self):
        olympedia_scraper = OlympediaScraper()
        result = olympedia_scraper.get_olympics_games()
        assert type(result) == list

    #TODO
    def test_get_event_athletes_results_from_country(self):
        olympedia_scraper = OlympediaScraper()
        # result = olympedia_scraper.get_event_athletes_results_from_country('AUS')
        assert True
    
    def test_get_bio_and_results_from_athlete_id(self):
        olympedia_scraper = OlympediaScraper()
        michael_phelps_id = '93860'
        result = olympedia_scraper.get_bio_and_results_from_athlete_id(michael_phelps_id)
        athlete_bio = result['athlete_bio_info']
        athlete_results = result['athlete_results']
        assert athlete_bio['athlete_id'] == mock_athletes.MICHAEL_PHELPS_BIO['athlete_id']
        assert athlete_results[0]['athlete_id'] == michael_phelps_id

    #TODO
    def test_get_html_from_result_id(self):
        olympedia_scraper = OlympediaScraper()
        result = olympedia_scraper.get_html_from_result_id('8772')
        assert True

if __name__ == '__main__':
    unittest.main()