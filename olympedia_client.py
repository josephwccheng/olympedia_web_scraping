import requests

class OlympediaClient:
    def __init__(self):
        self.base_url =  'http://www.olympedia.org'
    
    def make_request(self, url_extension, method_name):
        response = requests.get(self.base_url + url_extension)
        if response.status_code == 200:
            return response
        else:
            raise ValueError(
                "[{}] recieved response code: {}.".format(
                    method_name, response.status_code)
            )
    
    def get_all_countries_page(self):
        countries_page = self.make_request('/countries', 'get countries page')
        return countries_page.content

    def get_country_page(self, country_noc: str):
        country_page = self.make_request('/countries/' + country_noc, 'get countries page')
        return country_page.content

    def get_country_olympic_results_page(self, country_noc: str, index: str):
        # Note: expect extension url to be /countries/<country_noc>/editions/<#>
        country_olympic_results = self.make_request(f'/countries/{country_noc}/editions/{index}', 'get event athlete from result url')
        return country_olympic_results.content

    def get_all_editions_page(self):
        editions_page = self.make_request('/editions', 'get Olympic games page')
        return editions_page.content

    def get_athlete_page(self, athlete_id: str):
        athlete_page = self.make_request('/athletes/' + athlete_id, 'get bio and results from athlete_id')
        return athlete_page.content
    
    def get_result_page(self, result_id: str):
        result_page = self.make_request('/results/' + result_id, 'get html from result id')
        return result_page.content