#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import uuid
from urllib.parse import urljoin

import mysql.connector
import scrapy
from TeamCrawler.items import (
    TeamInfoPerSeason,
    TeamServedCoachList,
    TeamServedPlayerList,
    TeamArena,
    TeamExecutive,
)
from bs4 import BeautifulSoup
from bs4.element import NavigableString


class TeamSpider(scrapy.Spider):
    name = "TeamSpider"
    start_urls = []
    crawling_team_id_ls = []
    conn = None
    custom_settings = {
        "LOG_LEVEL": "INFO",
    }

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
               SELECT team_id, team_url
               FROM TEAM_INDEX
               WHERE need_update IS TRUE
            """
            # sql = """
            #     SELECT team_id, team_url
            #     FROM TEAM_INDEX
            #     WHERE need_update IS TRUE
            #     LIMIT 1
            # """
            cursor.execute(sql)
            for result in cursor:
                team_id = result[0]
                team_url = result[1]

                spider.crawling_team_id_ls.append(team_id)
                spider.start_urls.append(team_url)
        finally:
            if cursor is not None:
                cursor.close()

        return spider

    def start_requests(self):
        for start_url in self.start_urls:
            yield scrapy.Request(
                url=start_url, callback=self.parse_basic_info_per_season
            )

    def parse_basic_info_per_season(self, response, **kwargs):
        team_url = response.url
        team_url = re.sub(r"/$", "", team_url)

        team_id = team_url[team_url.find("/teams") :]
        team_abbrv_name = team_id[team_id.rfind("/") + 1 :]

        soup = BeautifulSoup(response.text, "lxml")
        team_info_table_id = "#" + team_abbrv_name
        team_info_table_ele = soup.select_one(team_info_table_id)
        if team_info_table_ele is None:
            self.logger.warn(
                (
                    "Failed to detect the per-season information of current team (%s).\n"
                    "Please check the webpage structure"
                ),
                team_url,
            )

        team_info_tr_eles = team_info_table_ele.select(
            "tbody tr:not(tr[class='thread'])"
        )
        for team_info_tr_ele in team_info_tr_eles:
            team_league_td_ele = team_info_tr_ele.select_one("td[data-stat='lg_id']")
            if (
                team_league_td_ele is not None
                and team_league_td_ele.text is not None
                and team_league_td_ele.text.upper() != "NBA"
            ):
                continue

            season_th_ele = team_info_tr_ele.select_one("th[data-stat='season']")
            season = (
                season_th_ele.text.strip()
                if season_th_ele and season_th_ele.text
                else None
            )
            if season is None:
                self.logger.warn("Skipped a row that has no season information")
                continue

            team_td_ele = team_info_tr_ele.select_one("td[data-stat='team_name']")
            registered_name = (
                re.sub(r"\*$", "", team_td_ele.text.strip())
                if team_td_ele and team_td_ele.text
                else None
            )
            if registered_name is None:
                self.logger.warn(
                    "Skipped a row that has no registered name information"
                )
                continue

            registered_abbrv_name = None
            info_url = None
            team_season_a_ele = team_td_ele.select_one("a[href]")
            if team_season_a_ele is not None:
                team_season_href = team_season_a_ele["href"]
                info_url = urljoin(response.url, team_season_href)
                m = re.match(r"/teams/([^/]+?)/\d{4}\.html", team_season_href)
                if m:
                    registered_abbrv_name = m.group(1)

            team_info_per_season = TeamInfoPerSeason()
            team_info_per_season["record_id"] = str(uuid.uuid1())
            team_info_per_season["team_id"] = team_id
            team_info_per_season["season"] = season
            team_info_per_season["registered_name"] = registered_name
            team_info_per_season["registered_abbrv_name"] = registered_abbrv_name
            team_info_per_season["info_url"] = info_url
            yield team_info_per_season

            if info_url is not None:
                yield scrapy.Request(
                    url=info_url,
                    callback=self.parse_roster_info_per_season,
                    cb_kwargs=dict(team_id=team_id, season=season),
                )

    def parse_roster_info_per_season(self, response, **kwargs):
        if "team_id" not in kwargs:
            self.logger.error(
                "Failed to retrieve the team_id info from the processing request"
            )
        if "season" not in kwargs:
            self.logger.error(
                "Failed to retrieve the season info from the processing request"
            )

        team_id = kwargs["team_id"]
        season = kwargs["season"]

        html = response.text
        html = re.sub(r"<!--|-->", "", html)
        soup = BeautifulSoup(html, "lxml")

        # region extract served head coach and assistant coaches, executive, and arena
        served_coach_ls = []
        executive_item = None
        arena_item = None

        # region head coach, executive, and arena
        info_div_ele = soup.select_one("#info")
        if info_div_ele is not None:
            # region head coach
            coach_a_ele = info_div_ele.select_one("p:has(strong:contains('Coach:')) a")
            coach_name = (
                coach_a_ele.text.strip() if coach_a_ele and coach_a_ele.text else None
            )
            coach_id = coach_a_ele.get("href") if coach_a_ele else None
            coach_job_title = "Head Coach"
            coach_url = urljoin(response.url, coach_id) if coach_id else None

            if coach_id and coach_name:
                served_coach = dict(
                    record_id=str(uuid.uuid1()),
                    team_id=team_id,
                    season=season,
                    coach_id=coach_id,
                    coach_name=coach_name,
                    coach_job_title=coach_job_title,
                    coach_url=coach_url,
                )
                served_coach_ls.append(served_coach)
            # endregion

            # region executive
            executive_a_ele = info_div_ele.select_one(
                "p:has(strong:contains('Executive:')) a"
            )
            executive_name = (
                executive_a_ele.text.strip()
                if executive_a_ele and executive_a_ele.text
                else None
            )
            executive_id = executive_a_ele.get("href") if executive_a_ele else None
            executive_url = (
                urljoin(response.url, executive_id) if executive_id else None
            )

            if executive_id and executive_name:
                executive_item = TeamExecutive()
                executive_item["record_id"] = str(uuid.uuid1())
                executive_item["team_id"] = team_id
                executive_item["season"] = season
                executive_item["executive_id"] = executive_id
                executive_item["executive_name"] = executive_name
                executive_item["executive_url"] = executive_url
            # endregion

            # region arena
            arena_strong_ele = info_div_ele.select_one("p strong:contains('Arena:')")
            arena_name = (
                arena_strong_ele.next_sibling
                if arena_strong_ele and arena_strong_ele.next_sibling
                else None
            )
            if isinstance(arena_name, NavigableString):
                arena_name = re.sub(r"\n+", "", str(arena_name))
                arena_name = arena_name.strip()
            else:
                arena_name = None

            attendance_strong_ele = info_div_ele.select_one(
                "p strong:contains('Attendance:')"
            )
            attendance = (
                attendance_strong_ele.next_sibling
                if attendance_strong_ele and attendance_strong_ele.next_sibling
                else None
            )
            if isinstance(attendance, NavigableString):
                attendance = re.sub(r"\n+", "", str(attendance))
                m = re.match(r"\s*(\d{1,3}(,\d{3})*|\d+)[^0-9]*", attendance.strip())
                if m:
                    attendance = int(m.group(1).replace(",", ""))
                else:
                    attendance = None
            else:
                attendance = None

            if arena_name:
                arena_item = TeamArena()
                arena_item["record_id"] = str(uuid.uuid1())
                arena_item["team_id"] = team_id
                arena_item["season"] = season
                arena_item["arena"] = arena_name
                arena_item["attendance"] = attendance
            # endregion
        else:
            self.logger.warn(
                "<div id='info'> was not found in the page: %s. Please check",
                response.url,
            )
        # endregion

        # region assistant coaches
        assistant_coaches_table_ele = soup.select_one("#div_assistant_coaches table")
        if assistant_coaches_table_ele is not None:
            # self.logger.debug("Found assistant coach table")

            assistant_coaches_tr_eles = assistant_coaches_table_ele.select("tr")
            for assistant_coaches_tr_ele in assistant_coaches_tr_eles:
                assistant_coaches_td_eles = assistant_coaches_tr_ele.select("td")
                if len(assistant_coaches_td_eles) != 2:
                    continue

                # self.logger.debug("Extracting assistant coaches info")
                assistant_coaches_a_ele = assistant_coaches_td_eles[0].select_one(
                    "a[href]"
                )
                coach_name = (
                    assistant_coaches_a_ele.text.strip()
                    if assistant_coaches_a_ele and assistant_coaches_a_ele.text
                    else None
                )
                coach_id = (
                    assistant_coaches_a_ele["href"] if assistant_coaches_a_ele else None
                )
                if coach_name and coach_id:
                    coach_url = urljoin(response.url, coach_id) if coach_id else None
                    coach_job_title = (
                        assistant_coaches_td_eles[1].text.replace("\xa0", " ").strip()
                        if assistant_coaches_td_eles[1].text
                        else None
                    )

                    served_coach = dict(
                        record_id=str(uuid.uuid1()),
                        team_id=team_id,
                        season=season,
                        coach_id=coach_id,
                        coach_name=coach_name,
                        coach_job_title=coach_job_title,
                        coach_url=coach_url,
                    )
                    served_coach_ls.append(served_coach)
        # endregion

        if len(served_coach_ls) > 0:
            served_coach_ls_item = TeamServedCoachList()
            served_coach_ls_item["team_served_coach_ls"] = served_coach_ls
            yield served_coach_ls_item

        if executive_item is not None:
            yield executive_item

        if arena_item is not None:
            yield arena_item
        # endregion

        # region extract served players
        served_player_ls = []

        player_roster_tbody_ele = soup.select_one("#roster tbody")
        if player_roster_tbody_ele is not None:
            player_roster_tr_eles = player_roster_tbody_ele.select("tr")
            for player_roster_tr_ele in player_roster_tr_eles:
                player_a_ele = player_roster_tr_ele.select_one(
                    "td[data-stat='player'] a[href^='/players']"
                )
                if player_a_ele is not None:
                    player_id = player_a_ele["href"]
                    player_name = player_a_ele.text if player_a_ele.text else None
                    player_url = urljoin(response.url, player_id)

                    if player_id and player_name:
                        served_player = dict(
                            record_id=str(uuid.uuid1()),
                            team_id=team_id,
                            season=season,
                            player_id=player_id,
                            player_name=player_name,
                            player_url=player_url,
                        )
                        served_player_ls.append(served_player)
        else:
            self.logger.warn(
                (
                    "<table id='roster'>...<tbody>...</tbody>...</table> was "
                    "not found in page: %s. Please check"
                ),
                response.url,
            )

        if len(served_player_ls) > 0:
            served_player_ls_item = TeamServedPlayerList()
            served_player_ls_item["team_served_player_ls"] = served_player_ls
            yield served_player_ls_item
        # endregion
