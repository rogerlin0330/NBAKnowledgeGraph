#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re
from urllib.parse import urljoin

import mysql.connector
import scrapy
from GameIndexCrawler.items import GameIndex
from bs4 import BeautifulSoup


class GameIndexSpider(scrapy.Spider):
    name = "GameIndexSpider"
    base_url = (
        "https://www.espn.com/nba/team/schedule/_/name/{}/season/{}/seasontype/{}"
    )
    game_year_range = list(range(2003, 2020 + 1))
    game_type_range = [2, 3]  # 2: regular, 3: playoff
    start_urls = []
    conn = None
    custom_settings = {
        "LOG_LEVEL": "INFO",
    }

    def __init__(self):
        super().__init__()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise RuntimeError(
                "The DB_SETTINGS need to be configured before activating the database pipeline."
            )

        spider = super().from_crawler(crawler, *args, **kwargs)

        db_conn = mysql.connector.connect(
            host=db_settings["host"],
            database=db_settings["db"],
            user=db_settings["user"],
            password=db_settings["passwd"],
        )
        db_conn.set_charset_collation("utf8mb4", "utf8mb4_unicode_ci")
        spider.conn = db_conn

        cursor = None
        try:
            cursor = db_conn.cursor(buffered=True)

            sql = """
                 SELECT DISTINCT espn_team_abbrv_name
                 FROM TEAM_INDEX_ESPN
            """
            # sql = """
            #     SELECT DISTINCT team_abbrv_name
            #     FROM TEAM_INDEX
            #     LIMIT 1
            # """
            cursor.execute(sql)
            for result in cursor:
                team_abbrv_name = result[0]

                for game_year in spider.game_year_range:
                    for game_type in spider.game_type_range:
                        start_url = spider.base_url.format(
                            team_abbrv_name, game_year, game_type
                        )
                        spider.start_urls.append(start_url)
        finally:
            if cursor is not None:
                cursor.close()

        return spider

    def start_requests(self):
        for start_url in self.start_urls:
            yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, "lxml")

        no_data_div_ele = soup.select_one("div.Schedule__no-data")
        if no_data_div_ele is not None:
            return

        page_title_h1_ele = soup.select_one("h1.headline.headline__h1.dib")
        if page_title_h1_ele is None:
            self.logger.warn(
                "Failed to retrieve the page title. Please check <%s>", response.url
            )
            return

        season = page_title_h1_ele.text if page_title_h1_ele.text else None
        if season is not None:
            m = re.search(r"\d{4}-\d{2}", season)
            if m:
                season = m.group()
            else:
                season = None
        if season is None:
            self.logger.warn(
                "Failed to retrieve the season information. Please check <%s>",
                response.url,
            )
            return

        current_url = response.url
        game_type = int(current_url[-1])
        if game_type == 2:
            game_type = "regular"
        elif game_type == 3:
            game_type = "playoffs"

        game_ls_tbody_ele = soup.select_one("section.pt0 table.Table tbody")
        if game_ls_tbody_ele is None:
            self.logger.warn(
                "No game information was found. Please check <%s>", response.url
            )
            return

        game_ls_table_header_tr_eles = game_ls_tbody_ele.select(
            "tr:has(td.Table_Headers)"
        )
        for game_ls_table_header_tr_ele in game_ls_table_header_tr_eles:
            game_ls_table_header_tr_ele.decompose()
        game_ls_table_title_tr_eles = game_ls_tbody_ele.select(
            "tr:has(td.Table__Title)"
        )
        for game_ls_table_title_tr_ele in game_ls_table_title_tr_eles:
            game_ls_table_title_tr_ele.decompose()

        game_ls_tr_eles = game_ls_tbody_ele.select("tr")
        for game_ls_tr_ele in game_ls_tr_eles:
            postponed_game_td_ele = game_ls_tr_ele.select_one(
                "td:contains('Postponed')"
            )
            if postponed_game_td_ele is not None:
                continue

            game_td_eles = game_ls_tr_ele.select("td")
            if game_type == "regular" and len(game_td_eles) != 7:
                self.logger.warn(
                    (
                        "The regular game-list table usually has 7 columns but current row has not. "
                        "Please check <%s>"
                    ),
                    response.url,
                )
                continue
            elif game_type == "playoffs" and len(game_td_eles) != 6:
                self.logger.warn(
                    (
                        "The playoffs game-list table usually has 6 columns but current row has not. "
                        "Please check <%s>"
                    ),
                    response.url,
                )
                continue

            key_column_index = -1
            if game_type == "regular" or game_type == "playoffs":
                key_column_index = 2
            if key_column_index == -1:
                self.logger.warning("Unknown key column index. Please check")
                continue

            game_result_td_ele = game_td_eles[2]
            game_result_a_ele = game_result_td_ele.select_one(
                "a[href*='/game?gameId=']"
            )
            if game_result_a_ele is not None:
                game_url = urljoin(response.url, game_result_a_ele["href"])

                game_id = None
                m = re.search(r"/game\?gameId=(.+)$", game_url, flags=re.I)
                if m:
                    game_id = m.group(1)
            else:
                self.logger.warn(
                    "No game id was found. Please check <%s>", response.url
                )
                continue

            if game_id and game_url and game_type:
                game_index_item = GameIndex()
                game_index_item["game_id"] = game_id
                game_index_item["game_url"] = game_url
                game_index_item["game_type"] = game_type
                game_index_item["season"] = season
                game_index_item["create_date"] = datetime.date.today()
                game_index_item["need_update"] = True
                yield game_index_item
