import logging
from typing import List

from selectolax.parser import HTMLParser
import requests


class TlcTripScraper:
    URL = "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page"

    @staticmethod
    def run() -> List[str]:
        """
        :return: list of scraped urls pointing to TLC Trip Record Data
        """
        res = requests.get(TlcTripScraper.URL)
        if res.status_code != 200:
            logging.error(f"www.nyc.gov status {res.status_code}")
            raise RuntimeError
        tree = HTMLParser(res.text)
        links = [node.attributes.get('href') for node in
                 tree.css('.faq-v1 > div > table > tbody > tr > td > ul > li > a')]
        return links
