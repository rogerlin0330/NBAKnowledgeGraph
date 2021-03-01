# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TeamIndex(scrapy.Item):
    record_id = scrapy.Field()
    team_id = scrapy.Field()
    team_url = scrapy.Field()
    team_name = scrapy.Field()
    team_abbrv_name = scrapy.Field()
    from_season = scrapy.Field()
    to_season = scrapy.Field()
    years = scrapy.Field()
    create_date = scrapy.Field()
    need_update = scrapy.Field()
