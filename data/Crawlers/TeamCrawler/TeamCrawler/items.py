# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TeamInfoPerSeason(scrapy.Item):
    record_id = scrapy.Field()
    team_id = scrapy.Field()
    season = scrapy.Field()
    registered_name = scrapy.Field()
    registered_abbrv_name = scrapy.Field()
    info_url = scrapy.Field()


class TeamServedCoachList(scrapy.Item):
    team_served_coach_ls = scrapy.Field()


class TeamServedPlayerList(scrapy.Item):
    team_served_player_ls = scrapy.Field()


class TeamArena(scrapy.Item):
    record_id = scrapy.Field()
    team_id = scrapy.Field()
    season = scrapy.Field()
    arena = scrapy.Field()
    attendance = scrapy.Field()


class TeamExecutive(scrapy.Item):
    record_id = scrapy.Field()
    team_id = scrapy.Field()
    season = scrapy.Field()
    executive_id = scrapy.Field()
    executive_name = scrapy.Field()
    executive_url = scrapy.Field()
