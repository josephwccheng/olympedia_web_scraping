import requests

class OlympediaClient:
    def __init__(self):
        self.base_url =  'http://www.olympedia.org'
    
    def get_request_content(self, url_extension, method_name):
        response = requests.get(self.base_url + url_extension)
        if response.status_code == 200:
            return response.content
        else:
            # TODO is throwing an exception the best way of handling this? Should add exception handlinig at top level probs
            raise ValueError(
                "[{}] recieved response code: {}.".format(
                    method_name, response.status_code)
            )