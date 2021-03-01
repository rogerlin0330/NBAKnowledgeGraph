# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from GameCrawler.items import Game, GamePlayedByPlayer


class GameDBPipeline:
    def close_spider(self, spider):
        conn = spider.conn
        cursor = None
        try:
            sql = """
                UPDATE GAME_INDEX 
                SET need_update = FALSE
                WHERE game_id = %s
            """

            cursor = conn.cursor(buffered=True)
            for game_id in spider.crawling_game_id_ls:
                cursor.execute(sql, (game_id,))
                conn.commit()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def process_item(self, item, spider):
        item_dict = ItemAdapter(item).asdict()

        conn = spider.conn
        cursor = None
        try:
            if type(item) is Game:
                sql = """
                    INSERT INTO GAME (
                        record_id, game_id, game_url, season, game_date, game_type,
                        home_team, home_team_abbrv, away_team, away_team_abbrv,
                        home_score, away_score
                    ) VALUES (
                        %(record_id)s, %(game_id)s, %(game_url)s, %(season)s, %(game_date)s,
                        %(game_type)s, %(home_team)s, %(home_team_abbrv)s, %(away_team)s,
                        %(away_team_abbrv)s, %(home_score)s, %(away_score)s
                    )
                """
            elif type(item) is GamePlayedByPlayer:
                sql = """
                    INSERT INTO GAME_PLAYED_BY_PLAYER (
                        record_id, game_id, player_name, player_team, player_espn_id,
                        player_espn_url
                    ) VALUES (
                        %(record_id)s, %(game_id)s, %(player_name)s, %(player_team)s,
                        %(player_espn_id)s, %(player_espn_url)s
                    )
                """
            cursor = conn.cursor(buffered=True)
            cursor.execute(sql, item_dict)
            conn.commit()
        finally:
            if cursor:
                cursor.close()

        return item
