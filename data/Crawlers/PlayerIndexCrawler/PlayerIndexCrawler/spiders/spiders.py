#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import uuid
from urllib.parse import urljoin

import scrapy
from PlayerIndexCrawler.items import PlayerIndex
from bs4 import BeautifulSoup


class PlayerIndexSpider(scrapy.Spider):
    name = "PlayerIndexSpider"
    custom_settings = {
        "LOG_LEVEL": "INFO",
    }

    def __init__(self):
        super().__init__()

    def start_requests(self):
        base_url = "https://www.basketball-reference.com/players/{}/"
        for start_letter_unicode in range(ord("a"), ord("z") + 1):
            start_letter = chr(start_letter_unicode)
            start_url = base_url.format(start_letter)
            yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, "lxml")
        player_table_ele = soup.select_one("#players tbody")

        # remove header line
        player_table_header_eles = player_table_ele.select("tr.thread")
        for header in player_table_header_eles:
            header.decompose()
        player_tr_eles = player_table_ele.select("tr")
        for tr_ele in player_tr_eles:
            try:
                player_index_item = PlayerIndex()
                player_index_item["record_id"] = str(uuid.uuid1())

                player_th_ele = tr_ele.select_one("th[data-stat='player']")

                player_a_ele = player_th_ele.select_one("strong a")
                if player_a_ele is not None:
                    player_index_item["active"] = True
                else:
                    player_index_item["active"] = False
                player_a_ele = player_th_ele.select_one("a")

                player_id = player_a_ele["href"]
                player_index_item["player_id"] = player_id

                player_url = urljoin(response.url, player_id)
                player_index_item["player_url"] = player_url

                player_name = player_a_ele.text.strip()
                player_index_item["player_name"] = player_name

                from_year_ele = tr_ele.select_one("td[data-stat='year_min']")
                from_year = from_year_ele.text.strip()
                player_index_item["from_year"] = from_year

                to_year_ele = tr_ele.select_one("td[data-stat='year_max']")
                to_year = to_year_ele.text.strip()
                player_index_item["to_year"] = to_year

                player_index_item["create_date"] = datetime.date.today()
                player_index_item["need_update"] = True

                yield player_index_item
            except Exception:
                self.logger.error("An exception occurs on page %s", response.url)
                self.logger.error("", exc_info=True)
