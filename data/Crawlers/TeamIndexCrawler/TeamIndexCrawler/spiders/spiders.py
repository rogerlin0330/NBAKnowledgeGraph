#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import uuid
from urllib.parse import urljoin

import scrapy
from TeamIndexCrawler.items import TeamIndex
from bs4 import BeautifulSoup
import re


class TeamIndexSpider(scrapy.Spider):
    name = "TeamIndexSpider"
    custom_settings = {
        "LOG_LEVEL": "INFO",
    }

    def __init__(self):
        super().__init__()

    def start_requests(self):
        start_url = "https://www.basketball-reference.com/teams/"
        yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, "lxml")
        active_team_table_ele = soup.select_one("#teams_active")
        if active_team_table_ele is None:
            self.logger.warn(
                "Failed to detect useful information. Please check the webpage's structure"
            )
            return

        active_team_tr_eles = active_team_table_ele.select("tr.full_table")
        for active_team_tr_ele in active_team_tr_eles:
            team_league_td_ele = active_team_tr_ele.select_one("td[data-stat='lg_id']")
            if (
                team_league_td_ele is not None
                and team_league_td_ele.text is not None
                and "NBA" not in team_league_td_ele.text.upper()
            ):
                continue

            team_name_a_ele = active_team_tr_ele.select_one(
                "th[data-stat='franch_name'] a[href]"
            )
            if team_name_a_ele is None or team_name_a_ele.text is None:
                self.logger.warn(
                    (
                        "Failed to get the team name from the current row of the table."
                        " This row will be skipped. Please check the webpage's structure"
                    )
                )
                continue
            team_name = team_name_a_ele.text
            team_id = team_name_a_ele["href"]
            team_id = re.sub(r"/$", "", team_id)
            team_url = urljoin(response.url, team_id) + "/"
            team_abbrv_name = team_id[team_id.rfind("/") + 1 :]

            from_season_td_ele = active_team_tr_ele.select_one(
                "td[data-stat='year_min']"
            )
            from_season = (
                from_season_td_ele.text
                if from_season_td_ele and from_season_td_ele.text
                else None
            )

            to_season_td_ele = active_team_tr_ele.select_one("td[data-stat='year_max']")
            to_season = (
                to_season_td_ele.text
                if to_season_td_ele and to_season_td_ele.text
                else None
            )

            years_td_ele = active_team_tr_ele.select_one("td[data-stat='years']")
            years = years_td_ele.text if years_td_ele and years_td_ele.text else None
            years = (
                int(years) if years is not None and re.match(r"\d+", years) else None
            )

            team_index_item = TeamIndex()
            team_index_item["record_id"] = str(uuid.uuid1())
            team_index_item["team_id"] = team_id
            team_index_item["team_url"] = team_url
            team_index_item["team_name"] = team_name
            team_index_item["team_abbrv_name"] = team_abbrv_name
            team_index_item["from_season"] = from_season
            team_index_item["to_season"] = to_season
            team_index_item["years"] = years
            team_index_item["create_date"] = datetime.date.today()
            team_index_item["need_update"] = True

            yield team_index_item
