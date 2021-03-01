# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GameIndex(scrapy.Item):
    game_id = scrapy.Field()
    game_url = scrapy.Field()
    game_type = scrapy.Field()
    season = scrapy.Field()
    create_date = scrapy.Field()
    need_update = scrapy.Field()
