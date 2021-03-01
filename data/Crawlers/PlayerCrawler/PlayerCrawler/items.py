# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PlayerBasic(scrapy.Item):
    record_id = scrapy.Field()
    player_id = scrapy.Field()
    player_url = scrapy.Field()
    player_name = scrapy.Field()
    player_full_name = scrapy.Field()
    date_of_birth = scrapy.Field()
    place_of_birth = scrapy.Field()
    height = scrapy.Field()
    weight = scrapy.Field()
    dominant_hand = scrapy.Field()
    college = scrapy.Field()
    high_school = scrapy.Field()


class PlayerPerformancePerGameList(scrapy.Item):
    player_performance_per_game_ls = scrapy.Field()


class PlayerPerformanceTotalList(scrapy.Item):
    player_performance_total_ls = scrapy.Field()


class PlayerHonorList(scrapy.Item):
    player_honor_ls = scrapy.Field()
