# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Game(scrapy.Item):
    record_id = scrapy.Field()
    game_id = scrapy.Field()
    game_url = scrapy.Field()
    season = scrapy.Field()
    game_date = scrapy.Field()
    game_type = scrapy.Field()
    home_team = scrapy.Field()
    home_team_abbrv = scrapy.Field()
    away_team = scrapy.Field()
    away_team_abbrv = scrapy.Field()
    home_score = scrapy.Field()
    away_score = scrapy.Field()
    play_by_play_shooting_record = scrapy.Field()


class GamePlayedByPlayer(scrapy.Item):
    record_id = scrapy.Field()
    game_id = scrapy.Field()
    player_name = scrapy.Field()
    player_team = scrapy.Field()
    player_espn_id = scrapy.Field()
    player_espn_url = scrapy.Field()
