# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector


class PlayerIndexDBPipeline:
    def __init__(self, db, user, passwd, host):
        self.db = db
        self.user = user
        self.passwd = passwd
        self.host = host
        self.conn = None

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise RuntimeError(
                "The DB_SETTINGS need to be configured before activating the database pipeline."
            )

        db = db_settings["db"]
        user = db_settings["user"]
        passwd = db_settings["passwd"]
        host = db_settings["host"]
        return cls(db, user, passwd, host)

    def open_spider(self, spider):
        self.conn = mysql.connector.connect(
            host=self.host, database=self.db, user=self.user, password=self.passwd
        )
        self.conn.set_charset_collation("utf8mb4", "utf8mb4_unicode_ci")

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()

    def process_item(self, item, spider):
        item_dict = ItemAdapter(item).asdict()

        cursor = None
        try:
            sql = """
                INSERT INTO
                PLAYER_INDEX (
                    record_id, player_id, player_url, player_name, from_year, to_year, active, create_date,
                    need_update)
                VALUES (
                    %(record_id)s, %(player_id)s, %(player_url)s, %(player_name)s, %(from_year)s, %(to_year)s,
                    %(active)s, %(create_date)s, %(need_update)s
                )
            """

            cursor = self.conn.cursor(buffered=True)
            cursor.execute(sql, item_dict)
            self.conn.commit()
        finally:
            if cursor:
                cursor.close()

        return item
