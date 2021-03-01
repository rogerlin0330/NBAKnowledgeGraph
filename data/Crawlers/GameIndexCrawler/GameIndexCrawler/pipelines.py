# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class GameIndexCrawlerDBPipeline:
    def close_spider(self, spider):
        conn = spider.conn
        if conn:
            conn.close()

    def process_item(self, item, spider):
        item_dict = ItemAdapter(item).asdict()

        conn = spider.conn
        cursor = None
        try:
            sql = """
                INSERT IGNORE INTO GAME_INDEX (
                    game_id, game_url, game_type, season, create_date, need_update
                )
                VALUES (
                    %(game_id)s, %(game_url)s, %(game_type)s, %(season)s,
                    %(create_date)s, %(need_update)s
                )
            """
            cursor = conn.cursor(buffered=True)
            cursor.execute(sql, item_dict)
            conn.commit()
        finally:
            if cursor:
                cursor.close()

        return item
