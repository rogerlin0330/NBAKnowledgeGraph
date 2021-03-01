#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import uuid

import mysql.connector
import scrapy
from PlayerCrawler.items import (
    PlayerBasic,
    PlayerPerformancePerGameList,
    PlayerPerformanceTotalList,
    PlayerHonorList,
)
from bs4 import BeautifulSoup
from collections import defaultdict


class PlayerSpider(scrapy.Spider):
    name = "PlayerSpider"
    start_urls = []
    crawling_player_id_ls = []
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
                SELECT player_id, player_url
                FROM PLAYER_INDEX
                WHERE need_update IS TRUE
                  AND CHAR_LENGTH(player_url) > 0
                ORDER BY to_year DESC, from_year ASC
                LIMIT %s
            """
            # sql = """
            #     SELECT player_id, player_url
            #     FROM PLAYER_INDEX
            #     WHERE player_id  = '/players/w/wilcoch01.html'
            #     LIMIT %s
            # """
            cursor.execute(sql, (max_increment_size,))
            for result in cursor:
                player_id = result[0]
                url = result[1]

                spider.crawling_player_id_ls.append(player_id)
                spider.start_urls.append(url)
        finally:
            if cursor is not None:
                cursor.close()

        return spider

    def start_requests(self):
        for start_url in self.start_urls:
            yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response, **kwargs):
        html = response.text
        html = re.sub(r"<!--|-->", "", html)
        soup = BeautifulSoup(html, "lxml")
        player_basic_item = PlayerBasic()
        player_basic_item["record_id"] = str(uuid.uuid1())

        try:
            # region extract PLAYER_BASIC info
            player_url = response.url
            player_basic_item["player_url"] = player_url

            key_index = player_url.rfind("/player")
            player_id = player_url[key_index:]
            player_basic_item["player_id"] = player_id

            player_info_div_ele = soup.select_one("div[id=info]")

            player_name_span_ele = player_info_div_ele.select_one(
                "h1[itemprop='name'] span"
            )
            player_name = player_name_span_ele.text.strip()
            player_basic_item["player_name"] = player_name

            player_names = player_name.split()
            if len(player_names) == 1:
                esc_player_name = player_name.replace("'", r"\'")
                player_full_name_strong_ele = player_info_div_ele.select_one(
                    "h1[itemprop='name'] ~ p strong:contains('{}')".format(
                        esc_player_name
                    )
                )
            else:
                player_names[0] = player_names[0].replace("'", r"\'")
                player_names[1] = player_names[1].replace("'", r"\'")
                player_full_name_strong_ele = player_info_div_ele.select_one(
                    "h1[itemprop='name'] ~ p strong:contains('{}', '{}')".format(
                        player_names[0], player_names[1]
                    )
                )

            if player_full_name_strong_ele is not None:
                player_full_name = player_full_name_strong_ele.text.strip()
                player_basic_item["player_full_name"] = player_full_name
            else:
                player_basic_item["player_full_name"] = None

            date_of_birth_span_ele = player_info_div_ele.select_one(
                "span[itemprop='birthDate'][data-birth]"
            )
            if date_of_birth_span_ele is not None:
                date_of_birth = date_of_birth_span_ele["data-birth"].strip()
                player_basic_item["date_of_birth"] = date_of_birth
            else:
                player_basic_item["date_of_birth"] = None

            place_of_birth_span_ele = player_info_div_ele.select_one(
                "span[itemprop='birthPlace']"
            )
            if place_of_birth_span_ele is not None:
                place_of_birth = place_of_birth_span_ele.text.strip()
                place_of_birth = re.sub(r"^in\s+", "", place_of_birth)
                place_of_birth = place_of_birth.replace("\xa0", " ")
                player_basic_item["place_of_birth"] = (
                    place_of_birth if len(place_of_birth) > 0 else None
                )
            else:
                player_basic_item["place_of_birth"] = None

            height_weight_p_ele = player_info_div_ele.select_one(
                "p:has(span[itemprop='height']):has(span[itemprop='weight'])"
            )
            if height_weight_p_ele is not None:
                height_weight_info = height_weight_p_ele.text.strip()
                m = re.search(r"(\d+(.\d+)?)cm", height_weight_info)
                if m:
                    height = m.group(1)
                    player_basic_item["height"] = float(height)
                else:
                    player_basic_item["height"] = None

                m = re.search(r"(\d+(.\d+)?)kg", height_weight_info)
                if m:
                    weight = m.group(1)
                    player_basic_item["weight"] = float(weight)
                else:
                    player_basic_item["weight"] = None
            else:
                player_basic_item["height"] = None
                player_basic_item["weight"] = None

            shoot_hand_p_ele = player_info_div_ele.select_one(
                "p:has(strong:contains('Shoots'))"
            )
            if shoot_hand_p_ele is not None:
                shoot_hand_info = shoot_hand_p_ele.text.strip()
                shoot_hand_info = shoot_hand_info.replace("\n", " ")
                m = re.search(r"Shoots.+?(left|right)", shoot_hand_info, flags=re.I)
                if m:
                    dominant_hand = m.group(1).lower()
                    player_basic_item["dominant_hand"] = dominant_hand
                else:
                    player_basic_item["dominant_hand"] = None
            else:
                player_basic_item["dominant_hand"] = None

            college_a_ele = player_info_div_ele.select_one(
                "p:has(strong:contains('College:')) a"
            )
            if college_a_ele is not None:
                college = college_a_ele.text.strip()
                player_basic_item["college"] = college
            else:
                player_basic_item["college"] = None

            high_school_p_ele = player_info_div_ele.select_one(
                "p:has(strong:contains('High School:'))"
            )
            if high_school_p_ele is not None:
                high_school = high_school_p_ele.text.strip().replace("\n", "")
                high_school = re.sub(r"high school:\s+", "", high_school, flags=re.I)
                m = re.search(r"(.+?)\s+in\s+(.+)", high_school)
                if m:
                    high_school = "{} ({})".format(
                        m.group(1).strip(), m.group(2).strip()
                    )
                player_basic_item["high_school"] = high_school
            else:
                player_basic_item["high_school"] = None

            yield player_basic_item
            # endregion

            # region extract PLAYER_PERFORMANCE_PER_GAME info
            player_performance_per_game_ls = []
            per_game_table_ele = soup.select_one("#per_game tbody")
            if per_game_table_ele is not None:
                per_game_tr_eles = per_game_table_ele.select("tr")
                for per_game_tr_ele in per_game_tr_eles:
                    player_performance_per_game = defaultdict(None)
                    try:
                        # eliminate situations like: https://www.basketball-reference.com/players/c/cartevi01.html
                        temp_ele = per_game_tr_ele.select_one("td[data-stat='team_id']")
                        if (
                            temp_ele is not None
                            and "TOT" in temp_ele.text
                            and temp_ele.select_one("a") is None
                        ):
                            continue

                        temp_ele = per_game_tr_ele.select_one(
                            "td:contains('Did Not Play')"
                        )
                        if temp_ele is not None:
                            continue

                        # season
                        season_th_ele = per_game_tr_ele.select_one(
                            "th[data-stat='season']"
                        )
                        season = (
                            season_th_ele.text.strip()
                            if season_th_ele and season_th_ele.text
                            else None
                        )

                        # age
                        age_td_ele = per_game_tr_ele.select_one("td[data-stat='age']")
                        age = age_td_ele.text.strip() if age_td_ele else None
                        if age is not None and re.match(r"\d+", age):
                            age = int(age)
                        else:
                            age = None

                        # team_abbrv_name
                        team_abbrv_name_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='team_id']"
                        )
                        team_abbrv_name = (
                            team_abbrv_name_td_ele.text.strip()
                            if team_abbrv_name_td_ele and team_abbrv_name_td_ele.text
                            else None
                        )

                        # league
                        league_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='lg_id']"
                        )
                        league = (
                            league_td_ele.text.strip()
                            if league_td_ele and league_td_ele.text
                            else None
                        )

                        # position
                        position_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='pos']"
                        )
                        position = (
                            position_td_ele.text.strip()
                            if position_td_ele and position_td_ele.text
                            else None
                        )

                        # G
                        G_td_ele = per_game_tr_ele.select_one("td[data-stat='g']")
                        G = (
                            G_td_ele.text.strip()
                            if G_td_ele and G_td_ele.text
                            else None
                        )
                        if G is not None and re.match(r"\d+", G):
                            G = int(G)
                        else:
                            G = None

                        # GS
                        GS_td_ele = per_game_tr_ele.select_one("td[data-stat='gs']")
                        GS = (
                            GS_td_ele.text.strip()
                            if GS_td_ele and GS_td_ele.text
                            else None
                        )
                        if GS is not None and re.match(r"\d+", GS):
                            GS = int(GS)
                        else:
                            GS = None

                        # NP
                        MP_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='mp_per_g']"
                        )
                        MP = (
                            MP_td_ele.text.strip()
                            if MP_td_ele and MP_td_ele.text
                            else None
                        )
                        if MP is not None and re.match(r"\d+(.\d+)?|.\d+", MP):
                            MP = float(MP)
                        else:
                            MP = None

                        # FG
                        FG_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='fg_per_g']"
                        )
                        FG = (
                            FG_td_ele.text.strip()
                            if FG_td_ele and FG_td_ele.text
                            else None
                        )
                        if FG is not None and re.match(r"\d+(.\d+)?|.\d+", FG):
                            FG = float(FG)
                        else:
                            FG = None

                        # FGA
                        FGA_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='fga_per_g']"
                        )
                        FGA = (
                            FGA_td_ele.text.strip()
                            if FGA_td_ele and FGA_td_ele.text
                            else None
                        )
                        if FGA is not None and re.match(r"\d+(.\d+)?|.\d+", FGA):
                            FGA = float(FGA)
                        else:
                            FGA = None

                        # FGP
                        FGP_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='fg_pct']"
                        )
                        FGP = (
                            FGP_td_ele.text.strip()
                            if FGP_td_ele and FGP_td_ele.text
                            else None
                        )
                        if FGP is not None and re.match(r"\d+(.\d+)?|.\d+", FGP):
                            FGP = float(FGP)
                        else:
                            FGP = None

                        # _3P
                        _3P_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='fg3_per_g']"
                        )
                        _3P = (
                            _3P_td_ele.text.strip()
                            if _3P_td_ele and _3P_td_ele.text
                            else None
                        )
                        if _3P is not None and re.match(r"\d+(.\d+)?|.\d+", _3P):
                            _3P = float(_3P)
                        else:
                            _3P = None

                        # _3PA
                        _3PA_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='fg3a_per_g']"
                        )
                        _3PA = (
                            _3PA_td_ele.text.strip()
                            if _3PA_td_ele and _3PA_td_ele.text
                            else None
                        )
                        if _3PA is not None and re.match(r"\d+(.\d+)?|.\d+", _3PA):
                            _3PA = float(_3PA)
                        else:
                            _3PA = None

                        # _3PP
                        _3PP_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='fg3_pct']"
                        )
                        _3PP = (
                            _3PP_td_ele.text.strip()
                            if _3PP_td_ele and _3PP_td_ele.text
                            else None
                        )
                        if _3PP is not None and re.match(r"\d+(.\d+)?|.\d+", _3PP):
                            _3PP = float(_3PP)
                        else:
                            _3PP = None

                        # _2P
                        _2P_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='fg2_per_g']"
                        )
                        _2P = (
                            _2P_td_ele.text.strip()
                            if _2P_td_ele and _2P_td_ele.text
                            else None
                        )
                        if _2P is not None and re.match(r"\d+(.\d+)?|.\d+", _2P):
                            _2P = float(_2P)
                        else:
                            _2P = None

                        # _2PA
                        _2PA_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='fg2a_per_g']"
                        )
                        _2PA = (
                            _2PA_td_ele.text.strip()
                            if _2PA_td_ele and _2PA_td_ele.text
                            else None
                        )
                        if _2PA is not None and re.match(r"\d+(.\d+)?|.\d+", _2PA):
                            _2PA = float(_2PA)
                        else:
                            _2PA = None

                        # _2PP
                        _2PP_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='fg2_pct']"
                        )
                        _2PP = (
                            _2PP_td_ele.text.strip()
                            if _2PP_td_ele and _2PP_td_ele.text
                            else None
                        )
                        if _2PP is not None and re.match(r"\d+(.\d+)?|.\d+", _2PP):
                            _2PP = float(_2PP)
                        else:
                            _2PP = None

                        # eFGP
                        eFGP_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='efg_pct']"
                        )
                        eFGP = (
                            eFGP_td_ele.text.strip()
                            if eFGP_td_ele and eFGP_td_ele.text
                            else None
                        )
                        if eFGP is not None and re.match(r"\d+(.\d+)?|.\d+", eFGP):
                            eFGP = float(eFGP)
                        else:
                            eFGP = None

                        # FT
                        FT_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='ft_per_g']"
                        )
                        FT = (
                            FT_td_ele.text.strip()
                            if FT_td_ele and FT_td_ele.text
                            else None
                        )
                        if FT is not None and re.match(r"\d+(.\d+)?|.\d+", FT):
                            FT = float(FT)
                        else:
                            FT = None

                        # FTA
                        FTA_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='fta_per_g']"
                        )
                        FTA = (
                            FTA_td_ele.text.strip()
                            if FTA_td_ele and FTA_td_ele.text
                            else None
                        )
                        if FTA is not None and re.match(r"\d+(.\d+)?|.\d+", FTA):
                            FTA = float(FTA)
                        else:
                            FTA = None

                        # FTP
                        FTP_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='ft_pct']"
                        )
                        FTP = (
                            FTP_td_ele.text.strip()
                            if FTP_td_ele and FTP_td_ele.text
                            else None
                        )
                        if FTP is not None and re.match(r"\d+(.\d+)?|.\d+", FTP):
                            FTP = float(FTP)
                        else:
                            FTP = None

                        # ORB
                        ORB_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='orb_per_g']"
                        )
                        ORB = (
                            ORB_td_ele.text.strip()
                            if ORB_td_ele and ORB_td_ele.text
                            else None
                        )
                        if ORB is not None and re.match(r"\d+(.\d+)?|.\d+", ORB):
                            ORB = float(ORB)
                        else:
                            ORB = None

                        # DRB
                        DRB_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='drb_per_g']"
                        )
                        DRB = (
                            DRB_td_ele.text.strip()
                            if DRB_td_ele and DRB_td_ele.text
                            else None
                        )
                        if DRB is not None and re.match(r"\d+(.\d+)?|.\d+", DRB):
                            DRB = float(DRB)
                        else:
                            DRB = None

                        # TRB
                        TRB_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='trb_per_g']"
                        )
                        TRB = (
                            TRB_td_ele.text.strip()
                            if TRB_td_ele and TRB_td_ele.text
                            else None
                        )
                        if TRB is not None and re.match(r"\d+(.\d+)?|.\d+", TRB):
                            TRB = float(TRB)
                        else:
                            TRB = None

                        # AST
                        AST_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='ast_per_g']"
                        )
                        AST = (
                            AST_td_ele.text.strip()
                            if AST_td_ele and AST_td_ele.text
                            else None
                        )
                        if AST is not None and re.match(r"\d+(.\d+)?|.\d+", AST):
                            AST = float(AST)
                        else:
                            AST = None

                        # STL
                        STL_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='stl_per_g']"
                        )
                        STL = (
                            STL_td_ele.text.strip()
                            if STL_td_ele and STL_td_ele.text
                            else None
                        )
                        if STL is not None and re.match(r"\d+(.\d+)?|.\d+", STL):
                            STL = float(STL)
                        else:
                            STL = None

                        # BLK
                        BLK_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='blk_per_g']"
                        )
                        BLK = (
                            BLK_td_ele.text.strip()
                            if BLK_td_ele and BLK_td_ele.text
                            else None
                        )
                        if BLK is not None and re.match(r"\d+(.\d+)?|.\d+", BLK):
                            BLK = float(BLK)
                        else:
                            BLK = None

                        # TOV
                        TOV_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='tov_per_g']"
                        )
                        TOV = (
                            TOV_td_ele.text.strip()
                            if TOV_td_ele and TOV_td_ele.text
                            else None
                        )
                        if TOV is not None and re.match(r"\d+(.\d+)?|.\d+", TOV):
                            TOV = float(TOV)
                        else:
                            TOV = None

                        # PF
                        PF_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='pf_per_g']"
                        )
                        PF = (
                            PF_td_ele.text.strip()
                            if PF_td_ele and PF_td_ele.text
                            else None
                        )
                        if PF is not None and re.match(r"\d+(.\d+)?|.\d+", PF):
                            PF = float(PF)
                        else:
                            PF = None

                        # PTS
                        PTS_td_ele = per_game_tr_ele.select_one(
                            "td[data-stat='pts_per_g']"
                        )
                        PTS = (
                            PTS_td_ele.text.strip()
                            if PTS_td_ele and PTS_td_ele.text
                            else None
                        )
                        if PTS is not None and re.match(r"\d+(.\d+)?|.\d+", PTS):
                            PTS = float(PTS)
                        else:
                            PTS = None

                        player_performance_per_game["record_id"] = str(uuid.uuid1())
                        player_performance_per_game["player_id"] = player_basic_item[
                            "player_id"
                        ]
                        player_performance_per_game["season"] = season
                        player_performance_per_game["age"] = age
                        player_performance_per_game["team_abbrv_name"] = team_abbrv_name
                        player_performance_per_game["league"] = league
                        player_performance_per_game["position"] = position
                        player_performance_per_game["G"] = G
                        player_performance_per_game["GS"] = GS
                        player_performance_per_game["MP"] = MP
                        player_performance_per_game["FG"] = FG
                        player_performance_per_game["FGA"] = FGA
                        player_performance_per_game["FGP"] = FGP
                        player_performance_per_game["_3P"] = _3P
                        player_performance_per_game["_3PA"] = _3PA
                        player_performance_per_game["_3PP"] = _3PP
                        player_performance_per_game["_2P"] = _2P
                        player_performance_per_game["_2PA"] = _2PA
                        player_performance_per_game["_2PP"] = _2PP
                        player_performance_per_game["eFGP"] = eFGP
                        player_performance_per_game["FT"] = FT
                        player_performance_per_game["FTA"] = FTA
                        player_performance_per_game["FTP"] = FTP
                        player_performance_per_game["ORB"] = ORB
                        player_performance_per_game["DRB"] = DRB
                        player_performance_per_game["TRB"] = TRB
                        player_performance_per_game["AST"] = AST
                        player_performance_per_game["STL"] = STL
                        player_performance_per_game["BLK"] = BLK
                        player_performance_per_game["TOV"] = TOV
                        player_performance_per_game["PF"] = PF
                        player_performance_per_game["PTS"] = PTS

                        player_performance_per_game_ls.append(
                            player_performance_per_game
                        )
                    except Exception:
                        self.logger.error(
                            "An exception occurs on page %s", response.url
                        )
                        self.logger.error("", exc_info=True)

            player_performance_per_game_ls_item = PlayerPerformancePerGameList()
            player_performance_per_game_ls_item[
                "player_performance_per_game_ls"
            ] = player_performance_per_game_ls
            yield player_performance_per_game_ls_item
            # endregion

            # region extract PLAYER_PERFORMANCE_TOTAL info
            player_performance_total_ls = []
            total_table_ele = soup.select_one("#totals tbody")
            if total_table_ele is not None:
                total_tr_eles = total_table_ele.select("tr")
                for total_tr_ele in total_tr_eles:
                    player_performance_total = defaultdict(None)
                    try:
                        # eliminate situations like: https://www.basketball-reference.com/players/c/cartevi01.html
                        temp_ele = total_tr_ele.select_one("td[data-stat='team_id']")
                        if (
                            temp_ele is not None
                            and "TOT" in temp_ele.text
                            and temp_ele.select_one("a") is None
                        ):
                            continue

                        temp_ele = total_tr_ele.select_one(
                            "td:contains('Did Not Play')"
                        )
                        if temp_ele is not None:
                            continue

                        # season
                        season_th_ele = total_tr_ele.select_one(
                            "th[data-stat='season']"
                        )
                        season = (
                            season_th_ele.text.strip()
                            if season_th_ele and season_th_ele.text
                            else None
                        )

                        # age
                        age_td_ele = total_tr_ele.select_one("td[data-stat='age']")
                        age = age_td_ele.text.strip() if age_td_ele else None
                        if age is not None and re.match(r"\d+", age):
                            age = int(age)
                        else:
                            age = None

                        # team_abbrv_name
                        team_abbrv_name_td_ele = total_tr_ele.select_one(
                            "td[data-stat='team_id']"
                        )
                        team_abbrv_name = (
                            team_abbrv_name_td_ele.text.strip()
                            if team_abbrv_name_td_ele and team_abbrv_name_td_ele.text
                            else None
                        )

                        # league
                        league_td_ele = total_tr_ele.select_one("td[data-stat='lg_id']")
                        league = (
                            league_td_ele.text.strip()
                            if league_td_ele and league_td_ele.text
                            else None
                        )

                        # position
                        position_td_ele = total_tr_ele.select_one("td[data-stat='pos']")
                        position = (
                            position_td_ele.text.strip()
                            if position_td_ele and position_td_ele.text
                            else None
                        )

                        # G
                        G_td_ele = total_tr_ele.select_one("td[data-stat='g']")
                        G = (
                            G_td_ele.text.strip()
                            if G_td_ele and G_td_ele.text
                            else None
                        )
                        if G is not None and re.match(r"\d+", G):
                            G = int(G)
                        else:
                            G = None

                        # GS
                        GS_td_ele = total_tr_ele.select_one("td[data-stat='gs']")
                        GS = (
                            GS_td_ele.text.strip()
                            if GS_td_ele and GS_td_ele.text
                            else None
                        )
                        if GS is not None and re.match(r"\d+", GS):
                            GS = int(GS)
                        else:
                            GS = None

                        # NP
                        MP_td_ele = total_tr_ele.select_one("td[data-stat='mp']")
                        MP = (
                            MP_td_ele.text.strip()
                            if MP_td_ele and MP_td_ele.text
                            else None
                        )
                        if MP is not None and re.match(r"\d+(.\d+)?|.\d+", MP):
                            MP = float(MP)
                        else:
                            MP = None

                        # FG
                        FG_td_ele = total_tr_ele.select_one("td[data-stat='fg']")
                        FG = (
                            FG_td_ele.text.strip()
                            if FG_td_ele and FG_td_ele.text
                            else None
                        )
                        if FG is not None and re.match(r"\d+(.\d+)?|.\d+", FG):
                            FG = float(FG)
                        else:
                            FG = None

                        # FGA
                        FGA_td_ele = total_tr_ele.select_one("td[data-stat='fga']")
                        FGA = (
                            FGA_td_ele.text.strip()
                            if FGA_td_ele and FGA_td_ele.text
                            else None
                        )
                        if FGA is not None and re.match(r"\d+(.\d+)?|.\d+", FGA):
                            FGA = float(FGA)
                        else:
                            FGA = None

                        # FGP
                        FGP_td_ele = total_tr_ele.select_one("td[data-stat='fg_pct']")
                        FGP = (
                            FGP_td_ele.text.strip()
                            if FGP_td_ele and FGP_td_ele.text
                            else None
                        )
                        if FGP is not None and re.match(r"\d+(.\d+)?|.\d+", FGP):
                            FGP = float(FGP)
                        else:
                            FGP = None

                        # _3P
                        _3P_td_ele = total_tr_ele.select_one("td[data-stat='fg3']")
                        _3P = (
                            _3P_td_ele.text.strip()
                            if _3P_td_ele and _3P_td_ele.text
                            else None
                        )
                        if _3P is not None and re.match(r"\d+(.\d+)?|.\d+", _3P):
                            _3P = float(_3P)
                        else:
                            _3P = None

                        # _3PA
                        _3PA_td_ele = total_tr_ele.select_one("td[data-stat='fg3a']")
                        _3PA = (
                            _3PA_td_ele.text.strip()
                            if _3PA_td_ele and _3PA_td_ele.text
                            else None
                        )
                        if _3PA is not None and re.match(r"\d+(.\d+)?|.\d+", _3PA):
                            _3PA = float(_3PA)
                        else:
                            _3PA = None

                        # _3PP
                        _3PP_td_ele = total_tr_ele.select_one("td[data-stat='fg3_pct']")
                        _3PP = (
                            _3PP_td_ele.text.strip()
                            if _3PP_td_ele and _3PP_td_ele.text
                            else None
                        )
                        if _3PP is not None and re.match(r"\d+(.\d+)?|.\d+", _3PP):
                            _3PP = float(_3PP)
                        else:
                            _3PP = None

                        # _2P
                        _2P_td_ele = total_tr_ele.select_one("td[data-stat='fg2']")
                        _2P = (
                            _2P_td_ele.text.strip()
                            if _2P_td_ele and _2P_td_ele.text
                            else None
                        )
                        if _2P is not None and re.match(r"\d+(.\d+)?|.\d+", _2P):
                            _2P = float(_2P)
                        else:
                            _2P = None

                        # _2PA
                        _2PA_td_ele = total_tr_ele.select_one("td[data-stat='fg2a']")
                        _2PA = (
                            _2PA_td_ele.text.strip()
                            if _2PA_td_ele and _2PA_td_ele.text
                            else None
                        )
                        if _2PA is not None and re.match(r"\d+(.\d+)?|.\d+", _2PA):
                            _2PA = float(_2PA)
                        else:
                            _2PA = None

                        # _2PP
                        _2PP_td_ele = total_tr_ele.select_one("td[data-stat='fg2_pct']")
                        _2PP = (
                            _2PP_td_ele.text.strip()
                            if _2PP_td_ele and _2PP_td_ele.text
                            else None
                        )
                        if _2PP is not None and re.match(r"\d+(.\d+)?|.\d+", _2PP):
                            _2PP = float(_2PP)
                        else:
                            _2PP = None

                        # eFGP
                        eFGP_td_ele = total_tr_ele.select_one("td[data-stat='efg_pct']")
                        eFGP = (
                            eFGP_td_ele.text.strip()
                            if eFGP_td_ele and eFGP_td_ele.text
                            else None
                        )
                        if eFGP is not None and re.match(r"\d+(.\d+)?|.\d+", eFGP):
                            eFGP = float(eFGP)
                        else:
                            eFGP = None

                        # FT
                        FT_td_ele = total_tr_ele.select_one("td[data-stat='ft']")
                        FT = (
                            FT_td_ele.text.strip()
                            if FT_td_ele and FT_td_ele.text
                            else None
                        )
                        if FT is not None and re.match(r"\d+(.\d+)?|.\d+", FT):
                            FT = float(FT)
                        else:
                            FT = None

                        # FTA
                        FTA_td_ele = total_tr_ele.select_one("td[data-stat='fta']")
                        FTA = (
                            FTA_td_ele.text.strip()
                            if FTA_td_ele and FTA_td_ele.text
                            else None
                        )
                        if FTA is not None and re.match(r"\d+(.\d+)?|.\d+", FTA):
                            FTA = float(FTA)
                        else:
                            FTA = None

                        # FTP
                        FTP_td_ele = total_tr_ele.select_one("td[data-stat='ft_pct']")
                        FTP = (
                            FTP_td_ele.text.strip()
                            if FTP_td_ele and FTP_td_ele.text
                            else None
                        )
                        if FTP is not None and re.match(r"\d+(.\d+)?|.\d+", FTP):
                            FTP = float(FTP)
                        else:
                            FTP = None

                        # ORB
                        ORB_td_ele = total_tr_ele.select_one("td[data-stat='orb']")
                        ORB = (
                            ORB_td_ele.text.strip()
                            if ORB_td_ele and ORB_td_ele.text
                            else None
                        )
                        if ORB is not None and re.match(r"\d+(.\d+)?|.\d+", ORB):
                            ORB = float(ORB)
                        else:
                            ORB = None

                        # DRB
                        DRB_td_ele = total_tr_ele.select_one("td[data-stat='drb']")
                        DRB = (
                            DRB_td_ele.text.strip()
                            if DRB_td_ele and DRB_td_ele.text
                            else None
                        )
                        if DRB is not None and re.match(r"\d+(.\d+)?|.\d+", DRB):
                            DRB = float(DRB)
                        else:
                            DRB = None

                        # TRB
                        TRB_td_ele = total_tr_ele.select_one("td[data-stat='trb']")
                        TRB = (
                            TRB_td_ele.text.strip()
                            if TRB_td_ele and TRB_td_ele.text
                            else None
                        )
                        if TRB is not None and re.match(r"\d+(.\d+)?|.\d+", TRB):
                            TRB = float(TRB)
                        else:
                            TRB = None

                        # AST
                        AST_td_ele = total_tr_ele.select_one("td[data-stat='ast']")
                        AST = (
                            AST_td_ele.text.strip()
                            if AST_td_ele and AST_td_ele.text
                            else None
                        )
                        if AST is not None and re.match(r"\d+(.\d+)?|.\d+", AST):
                            AST = float(AST)
                        else:
                            AST = None

                        # STL
                        STL_td_ele = total_tr_ele.select_one("td[data-stat='stl']")
                        STL = (
                            STL_td_ele.text.strip()
                            if STL_td_ele and STL_td_ele.text
                            else None
                        )
                        if STL is not None and re.match(r"\d+(.\d+)?|.\d+", STL):
                            STL = float(STL)
                        else:
                            STL = None

                        # BLK
                        BLK_td_ele = total_tr_ele.select_one("td[data-stat='blk']")
                        BLK = (
                            BLK_td_ele.text.strip()
                            if BLK_td_ele and BLK_td_ele.text
                            else None
                        )
                        if BLK is not None and re.match(r"\d+(.\d+)?|.\d+", BLK):
                            BLK = float(BLK)
                        else:
                            BLK = None

                        # TOV
                        TOV_td_ele = total_tr_ele.select_one("td[data-stat='tov']")
                        TOV = (
                            TOV_td_ele.text.strip()
                            if TOV_td_ele and TOV_td_ele.text
                            else None
                        )
                        if TOV is not None and re.match(r"\d+(.\d+)?|.\d+", TOV):
                            TOV = float(TOV)
                        else:
                            TOV = None

                        # PF
                        PF_td_ele = total_tr_ele.select_one("td[data-stat='pf']")
                        PF = (
                            PF_td_ele.text.strip()
                            if PF_td_ele and PF_td_ele.text
                            else None
                        )
                        if PF is not None and re.match(r"\d+(.\d+)?|.\d+", PF):
                            PF = float(PF)
                        else:
                            PF = None

                        # PTS
                        PTS_td_ele = total_tr_ele.select_one("td[data-stat='pts']")
                        PTS = (
                            PTS_td_ele.text.strip()
                            if PTS_td_ele and PTS_td_ele.text
                            else None
                        )
                        if PTS is not None and re.match(r"\d+(.\d+)?|.\d+", PTS):
                            PTS = float(PTS)
                        else:
                            PTS = None

                        player_performance_total["record_id"] = str(uuid.uuid1())
                        player_performance_total["player_id"] = player_basic_item[
                            "player_id"
                        ]
                        player_performance_total["season"] = season
                        player_performance_total["age"] = age
                        player_performance_total["team_abbrv_name"] = team_abbrv_name
                        player_performance_total["league"] = league
                        player_performance_total["position"] = position
                        player_performance_total["G"] = G
                        player_performance_total["GS"] = GS
                        player_performance_total["MP"] = MP
                        player_performance_total["FG"] = FG
                        player_performance_total["FGA"] = FGA
                        player_performance_total["FGP"] = FGP
                        player_performance_total["_3P"] = _3P
                        player_performance_total["_3PA"] = _3PA
                        player_performance_total["_3PP"] = _3PP
                        player_performance_total["_2P"] = _2P
                        player_performance_total["_2PA"] = _2PA
                        player_performance_total["_2PP"] = _2PP
                        player_performance_total["eFGP"] = eFGP
                        player_performance_total["FT"] = FT
                        player_performance_total["FTA"] = FTA
                        player_performance_total["FTP"] = FTP
                        player_performance_total["ORB"] = ORB
                        player_performance_total["DRB"] = DRB
                        player_performance_total["TRB"] = TRB
                        player_performance_total["AST"] = AST
                        player_performance_total["STL"] = STL
                        player_performance_total["BLK"] = BLK
                        player_performance_total["TOV"] = TOV
                        player_performance_total["PF"] = PF
                        player_performance_total["PTS"] = PTS

                        player_performance_total_ls.append(player_performance_total)
                    except Exception:
                        self.logger.error(
                            "An exception occurs on page %s", response.url
                        )
                        self.logger.error("", exc_info=True)
            player_performance_total_ls_item = PlayerPerformanceTotalList()
            player_performance_total_ls_item[
                "player_performance_total_ls"
            ] = player_performance_total_ls
            yield player_performance_total_ls_item
            # endregion

            # region extract PLAYER_HONOR info
            award_table_ele = soup.select_one("#leaderboard_notable-awards table")
            if award_table_ele is not None:
                player_honor_ls = []
                award_td_eles = award_table_ele.select("td.single")
                for award_td_ele in award_td_eles:
                    if award_td_ele and award_td_ele.text:
                        raw_text = award_td_ele.text.strip()
                        award_info = re.split(
                            r"(?:(?<=\d{4}-\d{2})|(?<=\d{2}))\s+", raw_text, maxsplit=1
                        )
                        if len(award_info) != 2:
                            continue

                        player_honor = defaultdict(None)
                        player_honor["record_id"] = str(uuid.uuid1())
                        player_honor["player_id"] = player_basic_item["player_id"]

                        award = award_info[1]
                        player_honor["award"] = award

                        if re.match(r"\d{4}-\d{2}", award_info[0]):
                            season = award_info[0]

                            player_honor["season"] = season
                            player_honor["year"] = None
                            player_honor_ls.append(player_honor)
                        elif re.match(r"\d{4}", award_info[0]):
                            year = int(award_info[0])

                            player_honor["year"] = year
                            player_honor["season"] = None
                            player_honor_ls.append(player_honor)
                if len(player_honor_ls) > 0:
                    player_honor_ls_item = PlayerHonorList()
                    player_honor_ls_item["player_honor_ls"] = player_honor_ls
                    yield player_honor_ls_item
            # endregion
        except Exception:
            self.logger.error("An exception occurs on page %s", response.url)
            self.logger.error("", exc_info=True)
