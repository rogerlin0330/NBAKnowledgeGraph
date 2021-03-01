# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from PlayerCrawler.items import (
    PlayerBasic,
    PlayerPerformancePerGameList,
    PlayerPerformanceTotalList,
    PlayerHonorList,
)

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class PlayerDBPipeline:
    def close_spider(self, spider):
        conn = spider.conn
        cursor = None
        try:
            sql = """
                UPDATE PLAYER_INDEX
                SET need_update = FALSE
                WHERE player_id = %s
            """

            cursor = conn.cursor(buffered=True)
            for player_id in spider.crawling_player_id_ls:
                cursor.execute(sql, (player_id,))
                conn.commit()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def process_item(self, item, spider):
        # for field in item.fields:
        #     item.setdefault(field, None)
        item_dict = ItemAdapter(item).asdict()

        conn = spider.conn
        cursor = None
        try:
            if type(item) is PlayerBasic:
                sql = """
                    INSERT INTO PLAYER_BASIC (
                        record_id, player_id, player_url, player_name,
                        player_full_name, date_of_birth, place_of_birth,
                        height, weight, dominant_hand, college, high_school)
                    VALUES (
                        %(record_id)s, %(player_id)s, %(player_url)s, %(player_name)s,
                        %(player_full_name)s, %(date_of_birth)s, %(place_of_birth)s,
                        %(height)s, %(weight)s, %(dominant_hand)s, %(college)s,
                        %(high_school)s
                    )
                """
                cursor = conn.cursor(buffered=True)
                cursor.execute(sql, item_dict)
                conn.commit()
            elif type(item) is PlayerPerformancePerGameList:
                sql = """
                    INSERT INTO PLAYER_PERFORMANCE_STAT_PER_GAME (
                        record_id, player_id, season, age, team_abbrv_name, league,
                        position, G, GS, MP, FG, FGA, FGP, `3P`, `3PA`, `3PP`, `2P`,
                        `2PA`, `2PP`, eFGP, FT, FTA, FTP, ORB, DRB, TRB, AST, STL,
                        BLK, TOV, PF, PTS
                    ) VALUES (
                        %(record_id)s, %(player_id)s, %(season)s, %(age)s, %(team_abbrv_name)s,
                        %(league)s, %(position)s, %(G)s, %(GS)s, %(MP)s, %(FG)s, %(FGA)s, %(FGP)s,
                        %(_3P)s, %(_3PA)s, %(_3PP)s, %(_2P)s, %(_2PA)s, %(_2PP)s, %(eFGP)s, %(FT)s,
                        %(FTA)s, %(FTP)s, %(ORB)s, %(DRB)s, %(TRB)s, %(AST)s, %(STL)s,
                        %(BLK)s, %(TOV)s, %(PF)s, %(PTS)s
                    )
                """
                cursor = conn.cursor(buffered=True)
                cursor.executemany(sql, item_dict["player_performance_per_game_ls"])
                conn.commit()
            elif type(item) is PlayerPerformanceTotalList:
                sql = """
                    INSERT INTO PLAYER_PERFORMANCE_STAT_TOTAL (
                        record_id, player_id, season, age, team_abbrv_name, league,
                        position, G, GS, MP, FG, FGA, FGP, `3P`, `3PA`, `3PP`, `2P`,
                        `2PA`, `2PP`, eFGP, FT, FTA, FTP, ORB, DRB, TRB, AST, STL,
                        BLK, TOV, PF, PTS
                    ) VALUES (
                        %(record_id)s, %(player_id)s, %(season)s, %(age)s, %(team_abbrv_name)s,
                        %(league)s, %(position)s, %(G)s, %(GS)s, %(MP)s, %(FG)s, %(FGA)s, %(FGP)s,
                        %(_3P)s, %(_3PA)s, %(_3PP)s, %(_2P)s, %(_2PA)s, %(_2PP)s, %(eFGP)s, %(FT)s,
                        %(FTA)s, %(FTP)s, %(ORB)s, %(DRB)s, %(TRB)s, %(AST)s, %(STL)s,
                        %(BLK)s, %(TOV)s, %(PF)s, %(PTS)s
                    )
                """
                cursor = conn.cursor(buffered=True)
                cursor.executemany(sql, item_dict["player_performance_total_ls"])
                conn.commit()
            elif type(item) is PlayerHonorList:
                sql = """
                    INSERT INTO PLAYER_HONOR (
                        record_id, player_id, season, year, award
                    ) VALUES (
                        %(record_id)s, %(player_id)s, %(season)s, %(year)s, %(award)s
                    )
                """
                cursor = conn.cursor(buffered=True)
                cursor.executemany(sql, item_dict["player_honor_ls"])
                conn.commit()
        finally:
            if cursor:
                cursor.close()

        return item
