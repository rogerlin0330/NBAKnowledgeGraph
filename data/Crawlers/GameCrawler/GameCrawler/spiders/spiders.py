#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid

from dateutil.parser import parse as dateparse
import mysql.connector
import scrapy
from GameCrawler.items import Game, GamePlayedByPlayer
from bs4 import BeautifulSoup
import urllib
import re


class GameSpider(scrapy.Spider):
    name = "GameSpider"
    start_reqs = []
    crawling_game_id_ls = []
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

        max_increment_size = crawler.settings.getint("MAX_INCREMENT_SIZE")
        cursor = None
        try:
            cursor = db_conn.cursor(buffered=True)

            sql = """
               SELECT game_id, game_url, game_type, season
               FROM GAME_INDEX
               WHERE need_update IS TRUE
               ORDER BY season DESC
               LIMIT %s
            """
            cursor.execute(sql, (max_increment_size,))
            for result in cursor:
                game_id = result[0]
                game_url = result[1]
                game_type = result[2]
                season = result[3]

                start_req = dict(
                    game_id=game_id,
                    game_url=game_url,
                    game_type=game_type,
                    season=season,
                )

                spider.crawling_game_id_ls.append(game_id)
                spider.start_reqs.append(start_req)
        finally:
            if cursor is not None:
                cursor.close()

        return spider

    def start_requests(self):
        for start_req in self.start_reqs:
            game_id = start_req["game_id"]
            game_url = start_req["game_url"]
            game_type = start_req["game_type"]
            season = start_req["season"]

            yield scrapy.Request(
                url=game_url,
                callback=self.parse_gamecast,
                cb_kwargs=dict(game_id=game_id, game_type=game_type, season=season),
            )

    def _parse_team_info(self, game_url, team_div_ele, team_type):
        is_successful = True
        team_info = dict(team_name=None, team_abbrv_name=None, team_score=None)

        # region parsing team name and team abbrev name
        team_name_ele = team_div_ele.select_one("a.team-name") if team_div_ele else None
        team_name_ele = (
            team_div_ele.select_one("div.team-name")
            if (team_div_ele and team_name_ele is None)
            else team_name_ele
        )
        team_long_name_span_ele = (
            team_name_ele.select_one("span.long-name") if team_name_ele else None
        )
        team_short_name_span_ele = (
            team_name_ele.select_one("span.short-name") if team_name_ele else None
        )
        team_abbrv_span = (
            team_name_ele.select_one("span.abbrev") if team_name_ele else None
        )

        team_name = (
            "{} {}".format(
                team_long_name_span_ele.text.strip(),
                team_short_name_span_ele.text.strip(),
            )
            if team_long_name_span_ele
            and team_long_name_span_ele.text
            and team_short_name_span_ele
            and team_short_name_span_ele.text
            else None
        )
        team_abbrv_name = (
            team_abbrv_span.text.strip()
            if team_abbrv_span and team_abbrv_span.text
            else None
        )
        if team_name is None or team_abbrv_name is None:
            msg = "{game_url} - {team_type} team's name or abbrev name is missing, please check.".format(
                game_url=game_url, team_type=team_type
            )
            self.logger.warning(msg)
            return False, None
        else:
            team_info["team_name"] = team_name
            team_info["team_abbrv_name"] = team_abbrv_name
        # endregion

        # region parsing team score
        team_score_div_ele = (
            team_div_ele.select_one("div.score") if team_div_ele else None
        )
        team_score = (
            team_score_div_ele.text.strip()
            if team_score_div_ele and team_score_div_ele.text
            else None
        )
        if team_score is None:
            msg = "{game_url} - {team_type} team's score info is missing, please check.".format(
                game_url=game_url, team_type=team_type
            )
            self.logger.warning(msg)
        else:
            team_info["team_score"] = team_score
        # endregion

        return is_successful, team_info

    def parse_gamecast(self, response, **kwargs):
        game_id = kwargs["game_id"]
        game_url = response.url
        game_type = kwargs["game_type"]
        season = kwargs["season"]

        try:
            soup = BeautifulSoup(response.text, "lxml")

            # region game_date
            game_date_span_ele = soup.select_one("span[data-date]")
            game_date = game_date_span_ele["data-date"] if game_date_span_ele else None
            if game_date is not None:
                game_date = dateparse(game_date)
                game_date = game_date.strftime("%Y-%m-%d")
            # endregion

            # region home team info
            home_team_div = soup.select_one("div.team.home")
            is_successful, home_team_info = self._parse_team_info(
                game_url, home_team_div, "home"
            )
            if not is_successful:
                return
            home_team, home_team_abbrv, home_score = (
                home_team_info["team_name"],
                home_team_info["team_abbrv_name"],
                home_team_info["team_score"],
            )
            # endregion

            # region away team info
            away_team_div = soup.select_one("div.team.away")
            is_successful, away_team_info = self._parse_team_info(
                game_url, away_team_div, "away"
            )
            if not is_successful:
                return
            away_team, away_team_abbrv, away_score = (
                away_team_info["team_name"],
                away_team_info["team_abbrv_name"],
                away_team_info["team_score"],
            )
            # endregion

            game = Game()
            game["record_id"] = str(uuid.uuid1())
            game["game_id"] = game_id
            game["game_url"] = game_url
            game["season"] = season
            game["game_date"] = game_date
            game["game_type"] = game_type
            game["home_team"] = home_team
            game["home_team_abbrv"] = home_team_abbrv
            game["away_team"] = away_team
            game["away_team_abbrv"] = away_team_abbrv
            game["home_score"] = home_score
            game["away_score"] = away_score

            yield game

            boxscore_a_ele = soup.select_one("li.boxscore a[href^='/nba/boxscore']")
            if boxscore_a_ele is not None:
                href = boxscore_a_ele["href"]
                link = urllib.parse.urljoin(response.url, href)
                yield scrapy.Request(
                    link,
                    self.parse_boxscore,
                    cb_kwargs=dict(
                        game_id=game_id, home_team=home_team, away_team=away_team
                    ),
                )
        except Exception:
            self.logger.error("An exception occurs on page %s", response.url)
            self.logger.error("", exc_info=True)

    def _parse_team_boxscore(
        self, team_boxscore_div_ele, team_dict, team_type, game_id, base_url
    ):
        if team_boxscore_div_ele is None:
            self.logger.warning(
                "%s - failed to detect %s team box score info, please check",
                base_url,
                team_type,
            )
            return

        game_played_by_player_ls = []
        player_a_eles = team_boxscore_div_ele.select("a[data-player-uid][href]")
        for player_a_ele in player_a_eles:
            href = player_a_ele["href"]
            player_espn_url = urllib.parse.urljoin(base_url, href)
            m = re.search(
                r"/id/(?P<player_id>\d+/(?P<player_name>.+))$", href, flags=re.I
            )
            if m:
                player_espn_id = m.group("player_id")

                player_name = m.group("player_name")
                player_name = " ".join(player_name.split("-")).title()

                game_played_by_player = GamePlayedByPlayer()
                game_played_by_player["record_id"] = str(uuid.uuid1())
                game_played_by_player["game_id"] = game_id
                game_played_by_player["player_name"] = player_name
                game_played_by_player["player_team"] = (
                    team_dict["home_team"]
                    if team_type == "home"
                    else team_dict["away_team"]
                )
                game_played_by_player["player_espn_id"] = player_espn_id
                game_played_by_player["player_espn_url"] = player_espn_url

                game_played_by_player_ls.append(game_played_by_player)

        return game_played_by_player_ls

    def parse_boxscore(self, response, **kwargs):
        game_id = kwargs["game_id"]
        home_team = kwargs["home_team"]
        away_team = kwargs["away_team"]
        team_dict = dict(home_team=home_team, away_team=away_team)

        soup = BeautifulSoup(response.text, "lxml")
        boxscore_div_ele = soup.select_one("#gamepackage-boxscore-module")
        if boxscore_div_ele is None:
            self.logger.warning(
                "%s - failed to detect global box score info, please check",
                response.url,
            )
            return

        game_played_by_player_ls = []

        # region home team box score
        home_team_boxscore_div_ele = boxscore_div_ele.select_one(
            "div.gamepackage-home-wrap"
        )
        game_played_by_home_team_player_ls = self._parse_team_boxscore(
            home_team_boxscore_div_ele, team_dict, "home", game_id, response.url
        )
        game_played_by_player_ls.extend(game_played_by_home_team_player_ls)
        # endregion

        # region away team box score
        away_team_boxscore_div_ele = boxscore_div_ele.select_one(
            "div.gamepackage-away-wrap"
        )
        game_played_by_away_team_player_ls = self._parse_team_boxscore(
            away_team_boxscore_div_ele, team_dict, "away", game_id, response.url
        )
        game_played_by_player_ls.extend(game_played_by_away_team_player_ls)
        # endregion

        for game_played_by_player in game_played_by_player_ls:
            yield game_played_by_player
