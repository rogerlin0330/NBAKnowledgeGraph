#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Person:
    name = None
    source_id = None


class Player(Person):
    player_id = None
    player_url = None
    name = None
    full_name = None
    date_of_birth = None
    place_of_birth = None
    height = None
    weight = None
    dominant_hand = None
    college = None
    high_school = None


class PlayerHonor:
    honor_title = None


class PlayerRelative:
    player_id = None
    relative_name = None
    source_id = None
    relationship = None


class PlayerAchievedHonor:
    player_id = None
    honor_title = None
    season = None
    year = None


class Coach(Person):
    coach_id = None
    coach_url = None
    name = None


class Executive(Person):
    executive_id = None
    executive_url = None
    name = None


class Team:
    team_id = None
    team_url = None
    team_name = None
    team_abbrv_name = None
    from_season = None
    to_season = None
    espn_team_id = None
    espn_team_url = None
    espn_team_name = None
    espn_team_abbrv_name = None


class TeamServedPlayer:
    player_id = None
    team_id = None
    season = None


class TeamServedCoach:
    coach_id = None
    team_id = None
    season = None
    coach_job_title = None


class TeamManagedExecutive:
    executive_id = None
    team_id = None
    season = None


class TeamArena:
    team_id = None
    arena = None
    season = None
    attendance = None


class Stadium:
    stadium_name = None
