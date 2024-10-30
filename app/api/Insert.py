import endpoints as ep
import requests
from settings import Settings

settings = Settings()


class Insert:
    def __init__(self):
        self.url = settings.API_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + settings.API_KEY,
        }

    def ix_head_titles(self, data):
        url = self.url + ep.POST_HEAD_TITLES
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def ix_non_numerics(self, data):
        url = self.url + ep.POST_NON_NUMERICS
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def ix_non_fractions(self, data):
        url = self.url + ep.POST_NON_FRACTIONS
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def label_locs(self, data):
        url = self.url + ep.POST_LABEL_LOCS
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def label_arcs(self, data):
        url = self.url + ep.POST_LABEL_ARCS
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def label_values(self, data):
        url = self.url + ep.POST_LABEL_VALUES
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def cal_locs(self, data):
        url = self.url + ep.POST_CAL_LOCS
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def cal_arcs(self, data):
        url = self.url + ep.POST_CAL_ARCS
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def pre_locs(self, data):
        url = self.url + ep.POST_PRE_LOCS
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def pre_arcs(self, data):
        url = self.url + ep.POST_PRE_ARCS
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def def_locs(self, data):
        url = self.url + ep.POST_DEF_LOCS
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def def_arcs(self, data):
        url = self.url + ep.POST_DEF_ARCS
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def sources(self, data):
        url = self.url + ep.POST_SOURCES
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def schemas(self, data):
        url = self.url + ep.POST_SCHEMAS
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def file_path(self, data):
        url = self.url + ep.POST_FILE_PATH
        response = requests.post(url, headers=self.headers, json=data)
        return response

    def qualitative(self, data):
        url = self.url + ep.POST_QUALITATIVE
        response = requests.post(url, headers=self.headers, json=data)
        return response
