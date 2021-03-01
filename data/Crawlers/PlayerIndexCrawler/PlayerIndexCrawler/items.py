# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PlayerIndex(scrapy.Item):
    record_id = scrapy.Field()
    player_id = scrapy.Field()
    player_url = scrapy.Field()
    player_name = scrapy.Field()
    from_year = scrapy.Field()
    to_year = scrapy.Field()
    active = scrapy.Field()
    create_date = scrapy.Field()
    need_update = scrapy.Field()
