from typing import List
import xmltodict
import time
import requests
from bs4 import BeautifulSoup
from artrefsync.api.r34_model import R34_Post, parse_r34_post

import logging
logger = logging.getLogger(__name__)


def main():
    pass
    

class R34_Client():
    """
    Class to handle requesting and handling messages from the image board E621
    """
    def __init__(self, api_string):
        self.r34_api_string = api_string
        self.base_url = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index"
        self.hostname = "rule34.xxx"
        self.limit = 1000
        self.retries = 3
        self.last_run = time.time()

    def _build_url_request(self, tag, page) -> str:
        return f"{self.base_url}{self.r34_api_string}&limit={self.limit}&tags={tag}&pid={page}"

    def get_posts(self, tag) -> R34_Post:
        posts = []
        response = requests.get(self._build_url_request(tag, self.limit), timeout= 2.0)
        soup = BeautifulSoup(response.content, features="xml")
        for p in soup.find_all("post"):
            r34_post = parse_r34_post(p)
            posts.append(r34_post)
        return posts
if __name__ == "__main__":
    main()