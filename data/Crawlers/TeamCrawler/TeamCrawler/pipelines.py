# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from TeamCrawler.items import (
    TeamInfoPerSeason,
    TeamServedCoachList,
    TeamServedPlayerList,
    TeamArena,
    TeamExecutive,
)


class TeamCrawlerDBPipeline:
    def close_spider(self, spider):
        conn = spider.conn
        cursor = None
        try:
            sql = """
                UPDATE TEAM_INDEX
                SET need_update = FALSE
                WHERE team_id = %s
            """

            cursor = conn.cursor(buffered=True)
            for team_id in spider.crawling_team_id_ls:
                cursor.execute(sql, (team_id,))
                conn.commit()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def process_item(self, item, spider):
        # # region TODO: removing this segment after hotfix TEAM_SERVED_COACH
        # if type(item) is not TeamServedCoachList:
        #     return item
        # # endregion

        item_dict = ItemAdapter(item).asdict()

        conn = spider.conn
        cursor = None
        try:
            if type(item) is TeamInfoPerSeason:
                sql = """
                    INSERT INTO TEAM_INFO_PER_SEASON (
                        record_id, team_id, season, registered_name,
                        registered_abbrv_name, info_url
                    ) VALUES (
                        %(record_id)s, %(team_id)s, %(season)s, %(registered_name)s,
                        %(registered_abbrv_name)s, %(info_url)s
                    )
                """
                cursor = conn.cursor(buffered=True)
                cursor.execute(sql, item_dict)
                conn.commit()
            elif type(item) is TeamServedCoachList:
                sql = """
                    INSERT INTO TEAM_SERVED_COACH (
                        record_id, team_id, season, coach_id, coach_name,
                        coach_job_title, coach_url
                    ) VALUES (
                        %(record_id)s, %(team_id)s, %(season)s, %(coach_id)s, %(coach_name)s,
                        %(coach_job_title)s, %(coach_url)s
                    )
                """
                cursor = conn.cursor(buffered=True)
                cursor.executemany(sql, item_dict["team_served_coach_ls"])
                conn.commit()
                pass
            elif type(item) is TeamServedPlayerList:
                sql = """
                    INSERT INTO TEAM_SERVED_PLAYER (
                        record_id, team_id, season, player_id, player_name, player_url
                    ) VALUES (
                        %(record_id)s, %(team_id)s, %(season)s, %(player_id)s, %(player_name)s,
                        %(player_url)s
                    )
                """
                cursor = conn.cursor(buffered=True)
                cursor.executemany(sql, item_dict["team_served_player_ls"])
                conn.commit()
            elif type(item) is TeamArena:
                sql = """
                    INSERT INTO TEAM_ARENA (
                        record_id, team_id, season, arena, attendance
                    ) VALUES (
                        %(record_id)s, %(team_id)s, %(season)s, %(arena)s,
                        %(attendance)s
                    )
                """
                cursor = conn.cursor(buffered=True)
                cursor.execute(sql, item_dict)
                conn.commit()
            elif type(item) is TeamExecutive:
                sql = """
                    INSERT INTO TEAM_EXECUTIVE (
                        record_id, team_id, season, executive_id, executive_name,
                        executive_url
                    ) VALUES (
                        %(record_id)s, %(team_id)s, %(season)s, %(executive_id)s,
                        %(executive_name)s, %(executive_url)s
                    )
                """
                cursor = conn.cursor(buffered=True)
                cursor.execute(sql, item_dict)
                conn.commit()
        finally:
            if cursor:
                cursor.close()

        return item
