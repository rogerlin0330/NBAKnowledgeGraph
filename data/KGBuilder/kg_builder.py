#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import sys

import mysql.connector
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from value_obj import Person, Player, PlayerHonor, Coach, Executive, Team, Stadium
from value_obj import (
    PlayerRelative,
    PlayerAchievedHonor,
    TeamServedPlayer,
    TeamServedCoach,
    TeamManagedExecutive,
    TeamArena,
)


logging.basicConfig(
    filename="kg_builder.log",
    format="%(asctime)s [%(levelname)s]: %(message)s",
    level=logging.INFO,
)


mysql_db_config = {
    "db": "inf558",
    "user": "inf558",
    "passwd": "inf558",
    "host": "ec2-54-67-29-193.us-west-1.compute.amazonaws.com",
}

neo4j_db_config = {
    "uri": "bolt://www.rogerlin.tech:17687",
    "user": "dsci558",
    "password": "dsci558",
}


class Neo4jEngine:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def create_normal_person_node(self, person: Person):
        created_node_person_id_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_normal_person_node, person
            )
            for record in result:
                created_node_person_id_ls.append(
                    dict(
                        person_name=record["p"]["name"],
                        source_id=record["p"]["source_id"],
                    )
                )
                logging.info(
                    "Created node for normal person: %s (source: %s)",
                    record["p"]["name"],
                    record["p"]["source_id"],
                )
        return created_node_person_id_ls

    @staticmethod
    def _create_and_return_normal_person_node(tx, person: Person):
        query = """
            CREATE (p:NormalPerson:Person { name: $person_name, source_id: $source_id })
            RETURN p
        """
        result = tx.run(query, person_name=person.name, source_id=person.source_id)
        try:
            return [{"p": record["p"]} for record in result]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_player_node(self, player: Player):
        created_node_player_id_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_player_node, player
            )
            for record in result:
                created_node_player_id_ls.append(dict(player_id=record["p"]))
                logging.info("Created node for player: %s", record["p"])
        return created_node_player_id_ls

    @staticmethod
    def _create_and_return_player_node(tx, player: Player):
        query = """
            CREATE (p:Player:Person { 
                player_id: $player_id,
                player_url: $player_url,
                name: $player_name,
                full_name: $player_full_name,
                date_of_birth: $date_of_birth, 
                place_of_birth: $place_of_birth,
                height: $height,
                weight: $weight,
                dominant_hand: $dominant_hand,
                college: $college,
                high_school: $high_school
            })
            RETURN p
        """
        result = tx.run(
            query,
            player_id=player.player_id,
            player_url=player.player_url,
            player_name=player.name,
            player_full_name=player.full_name,
            date_of_birth=player.date_of_birth,
            place_of_birth=player.place_of_birth,
            height=player.height,
            weight=player.weight,
            dominant_hand=player.dominant_hand,
            college=player.college,
            high_school=player.high_school,
        )
        try:
            return [{"p": record["p"]["player_id"]} for record in result]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_player_honor_node(self, player_honor: PlayerHonor):
        created_node_player_honor_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_player_honor_node, player_honor
            )
            for record in result:
                created_node_player_honor_ls.append(dict(award=record["ph"]))
                logging.info("Created node for player honor: %s", record["ph"])
        return created_node_player_honor_ls

    @staticmethod
    def _create_and_return_player_honor_node(tx, player_honor: PlayerHonor):
        query = """
            CREATE (ph:PlayerHonor:Honor { honor_title: $honor_title })
            RETURN ph
        """
        result = tx.run(query, honor_title=player_honor.honor_title)
        try:
            return [{"ph": record["ph"]["honor_title"]} for record in result]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_coach_node(self, coach: Coach):
        created_node_coach_id_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_coach_node, coach
            )
            for record in result:
                created_node_coach_id_ls.append(dict(coach_id=record["c"]))
                logging.info("Created node for coach: %s", record["c"])
        return created_node_coach_id_ls

    @staticmethod
    def _create_and_return_coach_node(tx, coach: Coach):
        query = """
            CREATE (c:Coach:Person { 
                coach_id: $coach_id,
                coach_url: $coach_url,
                name: $coach_name
            })
            RETURN c
        """
        result = tx.run(
            query,
            coach_id=coach.coach_id,
            coach_url=coach.coach_url,
            coach_name=coach.name,
        )
        try:
            return [{"c": record["c"]["coach_id"]} for record in result]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_executive_node(self, executive: Executive):
        created_node_executive_id_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_executive_node, executive
            )
            for record in result:
                created_node_executive_id_ls.append(dict(executive_id=record["e"]))
                logging.info("Created node for executive: %s", record["e"])
        return created_node_executive_id_ls

    @staticmethod
    def _create_and_return_executive_node(tx, executive: Executive):
        query = """
            CREATE (e:Executive:Person { 
                executive_id: $executive_id,
                executive_url: $executive_url,
                name: $executive_name
            })
            RETURN e
        """
        result = tx.run(
            query,
            executive_id=executive.executive_id,
            executive_url=executive.executive_url,
            executive_name=executive.name,
        )
        try:
            return [{"e": record["e"]["executive_id"]} for record in result]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_team_node(self, team: Team):
        created_node_team_id_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(self._create_and_return_team_node, team)
            for record in result:
                created_node_team_id_ls.append(dict(team_id=record["t"]))
                logging.info("Created node for team: %s", record["t"])
        return created_node_team_id_ls

    @staticmethod
    def _create_and_return_team_node(tx, team: Team):
        query = """
            CREATE (t:Team { 
                team_id: $team_id,
                team_url: $team_url,
                team_name: $team_name,
                team_abbrv_name: $team_abbrv_name,
                from_season: $from_season,
                to_season: $to_season,
                espn_team_id: $espn_team_id,
                espn_team_url: $espn_team_url,
                espn_team_name: $espn_team_name,
                espn_team_abbrv_name: $espn_team_abbrv_name
            })
            RETURN t
        """
        result = tx.run(
            query,
            team_id=team.team_id,
            team_url=team.team_url,
            team_name=team.team_name,
            team_abbrv_name=team.team_abbrv_name,
            from_season=team.from_season,
            to_season=team.to_season,
            espn_team_id=team.espn_team_id,
            espn_team_url=team.espn_team_url,
            espn_team_name=team.espn_team_name,
            espn_team_abbrv_name=team.espn_team_abbrv_name,
        )
        try:
            return [{"t": record["t"]["team_id"]} for record in result]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_stadium_node(self, stadium: Stadium):
        created_node_stadium_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_stadium_node, stadium
            )
            for record in result:
                created_node_stadium_ls.append(dict(stadium_name=record["s"]))
                logging.info("Created node for stadium: %s", record["s"])
        return created_node_stadium_ls

    @staticmethod
    def _create_and_return_stadium_node(tx, stadium: Stadium):
        query = """
            CREATE (s:Stadium { stadium_name: $stadium_name })
            RETURN s
        """
        result = tx.run(query, stadium_name=stadium.stadium_name)
        try:
            return [{"s": record["s"]["stadium_name"]} for record in result]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_player_achieved_honor_relationship(
        self, player_achieved_honor: PlayerAchievedHonor
    ):
        created_relationship_player_achieved_honor_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_player_achieved_honor_relationship,
                player_achieved_honor,
            )
            for record in result:
                created_relationship_player_achieved_honor_ls.append(
                    dict(
                        player_id=record["p"]["player_id"],
                        award=record["h"]["honor_title"],
                        season=record["r"]["season"],
                        year=record["r"]["year"],
                    )
                )
                logging.info(
                    "Created relationship: (%s)-[achieved (%s)]->(%s)",
                    record["p"]["player_id"],
                    record["r"]["season"]
                    if record["r"]["season"]
                    else record["r"]["year"],
                    record["h"]["honor_title"],
                )
        return created_relationship_player_achieved_honor_ls

    @staticmethod
    def _create_and_return_player_achieved_honor_relationship(
        tx, player_achieved_honor: PlayerAchievedHonor
    ):
        query = """
            MATCH (p:Player),(h:PlayerHonor)
            WHERE p.player_id = $player_id AND h.honor_title = $honor_title
            CREATE (p)-[r:achieved { season: $season, year: $year }]->(h)
            RETURN p, r, h
        """
        result = tx.run(
            query,
            player_id=player_achieved_honor.player_id,
            honor_title=player_achieved_honor.honor_title,
            season=player_achieved_honor.season,
            year=player_achieved_honor.year,
        )
        try:
            return [
                {"p": record["p"], "r": record["r"], "h": record["h"]}
                for record in result
            ]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_team_served_player_relationship(
        self, team_served_player: TeamServedPlayer
    ):
        created_relationship_team_served_player_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_team_served_player_relationship,
                team_served_player,
            )
            for record in result:
                created_relationship_team_served_player_ls.append(
                    dict(
                        player_id=record["p"]["player_id"],
                        team_id=record["t"]["team_id"],
                        season=record["r"]["season"],
                    )
                )
                logging.info(
                    "Created relationship: (%s)-[served (%s)]->(%s)",
                    record["p"]["player_id"],
                    record["r"]["season"],
                    record["t"]["team_id"],
                )
        return created_relationship_team_served_player_ls

    @staticmethod
    def _create_and_return_team_served_player_relationship(
        tx, team_served_player: TeamServedPlayer
    ):
        query = """
            MATCH (p:Player),(t:Team)
            WHERE p.player_id = $player_id AND t.team_id = $team_id
            CREATE (p)-[r:served { season: $season }]->(t)
            RETURN p, r, t
        """
        result = tx.run(
            query,
            player_id=team_served_player.player_id,
            team_id=team_served_player.team_id,
            season=team_served_player.season,
        )
        try:
            return [
                {"p": record["p"], "r": record["r"], "t": record["t"]}
                for record in result
            ]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_team_served_coach_relationship(self, team_served_coach: TeamServedCoach):
        created_relationship_team_served_coach_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_team_served_coach_relationship,
                team_served_coach,
            )
            for record in result:
                created_relationship_team_served_coach_ls.append(
                    dict(
                        coach_id=record["c"]["coach_id"],
                        team_id=record["t"]["team_id"],
                        season=record["r"]["season"],
                        coach_job_title=record["r"]["coach_job_title"],
                    )
                )
                logging.info(
                    "Created relationship: (%s)-[served (%s), coach_job_title (%s)]->(%s)",
                    record["c"]["coach_id"],
                    record["r"]["season"],
                    record["r"]["coach_job_title"],
                    record["t"]["team_id"],
                )
        return created_relationship_team_served_coach_ls

    @staticmethod
    def _create_and_return_team_served_coach_relationship(
        tx, team_served_coach: TeamServedCoach
    ):
        query = """
            MATCH (c:Coach),(t:Team)
            WHERE c.coach_id = $coach_id AND t.team_id = $team_id
            CREATE (c)-[r:served { season: $season, coach_job_title: $coach_job_title }]->(t)
            RETURN c, r, t
        """
        result = tx.run(
            query,
            coach_id=team_served_coach.coach_id,
            team_id=team_served_coach.team_id,
            season=team_served_coach.season,
            coach_job_title=team_served_coach.coach_job_title,
        )
        try:
            return [
                {"c": record["c"], "r": record["r"], "t": record["t"]}
                for record in result
            ]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_team_managed_executive_relationship(
        self, team_managed_executive: TeamManagedExecutive
    ):
        created_relationship_team_managed_executive_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_team_managed_executive_relationship,
                team_managed_executive,
            )
            for record in result:
                created_relationship_team_managed_executive_ls.append(
                    dict(
                        executive_id=record["e"]["executive_id"],
                        team_id=record["t"]["team_id"],
                        season=record["r"]["season"],
                    )
                )
                logging.info(
                    "Created relationship: (%s)-[managed (%s)]->(%s)",
                    record["e"]["executive_id"],
                    record["r"]["season"],
                    record["t"]["team_id"],
                )
        return created_relationship_team_managed_executive_ls

    @staticmethod
    def _create_and_return_team_managed_executive_relationship(
        tx, team_managed_executive: TeamManagedExecutive
    ):
        query = """
            MATCH (e:Executive),(t:Team)
            WHERE e.executive_id = $executive_id AND t.team_id = $team_id
            CREATE (e)-[r:managed { season: $season }]->(t)
            RETURN e, r, t
        """
        result = tx.run(
            query,
            executive_id=team_managed_executive.executive_id,
            team_id=team_managed_executive.team_id,
            season=team_managed_executive.season,
        )
        try:
            return [
                {"e": record["e"], "r": record["r"], "t": record["t"]}
                for record in result
            ]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_team_arena_relationship(self, team_arena: TeamArena):
        created_relationship_team_arena_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_team_arena_relationship, team_arena
            )
            for record in result:
                created_relationship_team_arena_ls.append(
                    dict(
                        team_id=record["t"]["team_id"],
                        season=record["r"]["season"],
                        arena=record["s"]["stadium_name"],
                        attendance=record["r"]["attendance"],
                    )
                )
                logging.info("Created relationship: %s", record["r"])
        return created_relationship_team_arena_ls

    @staticmethod
    def _create_and_return_team_arena_relationship(tx, team_arena: TeamArena):
        query = """
            MATCH (t:Team),(s:Stadium)
            WHERE t.team_id = $team_id AND s.stadium_name = $arena
            CREATE (t)-[r:arena { season: $season, attendance: $attendance }]->(s)
            RETURN t, r, s
        """
        result = tx.run(
            query,
            team_id=team_arena.team_id,
            arena=team_arena.arena,
            season=team_arena.season,
            attendance=team_arena.attendance,
        )
        try:
            return [
                {"t": record["t"], "r": record["r"], "s": record["s"]}
                for record in result
            ]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def create_player_has_relative_relationship(self, player_relative: PlayerRelative):
        created_relationship_has_relative_ls = []
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_player_has_relative_relationship,
                player_relative,
            )
            for record in result:
                created_relationship_has_relative_ls.append(
                    dict(
                        player_id=record["p"]["player_id"],
                        source_id=record["np"]["source_id"],
                        relationship=record["rt"],
                    )
                )
                logging.info(
                    "Created relationship: %s-[%s]->%s (source: %s)",
                    record["p"]["player_id"],
                    record["rt"],
                    record["np"]["name"],
                    record["np"]["source_id"],
                )
        return created_relationship_has_relative_ls

    @staticmethod
    def _create_and_return_player_has_relative_relationship(
        tx, player_relative: PlayerRelative
    ):
        query = (
            """
            MATCH (p:Player),(np:NormalPerson)
            WHERE p.player_id = $player_id AND np.source_id = $source_id AND np.name = $relative_name
            CREATE (p)-[r:has_"""
            + player_relative.relationship
            + """]->(np)
            RETURN p, TYPE(r) AS rt, np
        """
        )
        result = tx.run(
            query,
            player_id=player_relative.player_id,
            source_id=player_relative.source_id,
            relative_name=player_relative.relative_name,
        )
        try:
            return [
                {"p": record["p"], "rt": record["rt"], "np": record["np"]}
                for record in result
            ]
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise


def get_mysql_conn():
    conn = mysql.connector.connect(
        host=mysql_db_config["host"],
        database=mysql_db_config["db"],
        user=mysql_db_config["user"],
        password=mysql_db_config["passwd"],
    )
    conn.set_charset_collation("utf8mb4", "utf8mb4_unicode_ci")
    return conn


def create_player_nodes(max_increment_size):
    # region retrieve player basic info from MySQL
    new_player_ls = []
    sql = """
        SELECT PB.player_id,
           PB.player_url,
           PB.player_name,
           PB.player_full_name,
           PB.date_of_birth,
           PB.place_of_birth,
           PB.height,
           PB.weight,
           PB.dominant_hand,
           PB.college,
           PB.high_school
        FROM PLAYER_INDEX PI
             JOIN PLAYER_BASIC PB on PI.player_id = PB.player_id
        WHERE PI.need_create_player_node IS TRUE
        ORDER BY to_year DESC, from_year ASC
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            player = Player()
            player.player_id = result[0]
            player.player_url = result[1]
            player.name = result[2]
            player.full_name = result[3]
            player.date_of_birth = result[4]
            player.place_of_birth = result[5]
            player.height = result[6]
            player.weight = result[7]
            player.dominant_hand = result[8]
            player.college = result[9]
            player.high_school = result[10]
            new_player_ls.append(player)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_player_ls) == 0:
        logging.warning("No more player need to be imported to Neo4j")
        return

    # region create player nodes in Neo4j
    created_node_player_id_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for player in new_player_ls:
            new_created_node_player_id_ls = neo4j_engine.create_player_node(player)
            created_node_player_id_ls.extend(new_created_node_player_id_ls)
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_node_player_id_ls) == 0:
        return

    # region update the node creation status in MySQL
    sql = """
        UPDATE PLAYER_INDEX SET need_create_player_node = FALSE
        WHERE player_id = %(player_id)s
    """
    conn = None
    cursor = None
    try:
        logging.info("Updating process status to MySQL")
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.executemany(sql, created_node_player_id_ls)
        conn.commit()
        logging.info("Done")
    except:
        conn.rollback()
        logging.error("", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion


def create_player_honor_nodes(max_increment_size):
    # region retrieve player honor info from MySQL
    new_player_honor_ls = []
    sql = """
        SELECT award FROM PLAYER_HONOR_INDEX
        WHERE need_create_honor_node IS TRUE
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            player_honor = PlayerHonor()
            player_honor.honor_title = result[0]
            new_player_honor_ls.append(player_honor)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_player_honor_ls) == 0:
        logging.warning("No more player honor need to be imported to Neo4j")
        return

    # region create player nodes in Neo4j
    created_node_player_honor_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for player_honor in new_player_honor_ls:
            new_created_node_player_honor_ls = neo4j_engine.create_player_honor_node(
                player_honor
            )
            created_node_player_honor_ls.extend(new_created_node_player_honor_ls)
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_node_player_honor_ls) == 0:
        return

    # region update the node creation status in MySQL
    sql = """
        UPDATE PLAYER_HONOR_INDEX SET need_create_honor_node = FALSE
        WHERE award = %(award)s
    """
    conn = None
    cursor = None
    try:
        logging.info("Updating process status to MySQL")
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.executemany(sql, created_node_player_honor_ls)
        conn.commit()
        logging.info("Done")
    except:
        conn.rollback()
        logging.error("", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion


def create_coach_nodes(max_increment_size):
    # region retrieve coach basic info from MySQL
    new_coach_ls = []
    sql = """
        SELECT DISTINCT TSC.coach_id, TSC.coach_url, TSC.coach_name
        FROM COACH_INDEX CI
                 JOIN TEAM_SERVED_COACH TSC on CI.coach_id = TSC.coach_id
        WHERE need_create_coach_node IS TRUE
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            coach = Coach()
            coach.coach_id = result[0]
            coach.coach_url = result[1]
            coach.name = result[2]
            new_coach_ls.append(coach)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_coach_ls) == 0:
        logging.warning("No more coach need to be imported to Neo4j")
        return

    # region create coach nodes in Neo4j
    created_node_coach_id_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for coach in new_coach_ls:
            new_created_node_coach_id_ls = neo4j_engine.create_coach_node(coach)
            created_node_coach_id_ls.extend(new_created_node_coach_id_ls)
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_node_coach_id_ls) == 0:
        return

    # region update the node creation status in MySQL
    sql = """
        UPDATE COACH_INDEX SET need_create_coach_node = FALSE
        WHERE coach_id = %(coach_id)s
    """
    conn = None
    cursor = None
    try:
        logging.info("Updating process status to MySQL")
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.executemany(sql, created_node_coach_id_ls)
        conn.commit()
        logging.info("Done")
    except:
        conn.rollback()
        logging.error("", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion


def create_executive_nodes(max_increment_size):
    # region retrieve coach basic info from MySQL
    new_executive_ls = []
    sql = """
        SELECT DISTINCT TE.executive_id, TE.executive_url, TE.executive_name
        FROM EXECUTIVE_INDEX EI
                 JOIN TEAM_EXECUTIVE TE on EI.executive_id = TE.executive_id
        WHERE need_create_executive_node IS TRUE
        LIMIT %s
        """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            executive = Executive()
            executive.executive_id = result[0]
            executive.executive_url = result[1]
            executive.name = result[2]
            new_executive_ls.append(executive)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_executive_ls) == 0:
        logging.warning("No more coach need to be imported to Neo4j")
        return

    # region create executive nodes in Neo4j
    created_node_executive_id_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for executive in new_executive_ls:
            new_created_node_executive_id_ls = neo4j_engine.create_executive_node(
                executive
            )
            created_node_executive_id_ls.extend(new_created_node_executive_id_ls)
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_node_executive_id_ls) == 0:
        return

    # region update the node creation status in MySQL
    sql = """
        UPDATE EXECUTIVE_INDEX SET need_create_executive_node = FALSE
        WHERE executive_id = %(executive_id)s
    """
    conn = None
    cursor = None
    try:
        logging.info("Updating process status to MySQL")
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.executemany(sql, created_node_executive_id_ls)
        conn.commit()
        logging.info("Done")
    except:
        conn.rollback()
        logging.error("", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion


def create_team_nodes(max_increment_size):
    # region retrieve team basic info from MySQL
    new_team_ls = []
    sql = """
        SELECT TI.team_id,
               TI.team_url,
               TI.team_name,
               TI.team_abbrv_name,
               TI.from_season,
               TI.to_season,
               TIE.espn_team_id,
               TIE.espn_team_url,
               TIE.espn_team_name,
               TIE.espn_team_abbrv_name
        FROM TEAM_INDEX TI
                 JOIN TEAM_INDEX_ESPN TIE ON TI.team_name = TIE.espn_team_name
        WHERE TI.need_create_team_node IS TRUE
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            team = Team()
            team.team_id = result[0]
            team.team_url = result[1]
            team.team_name = result[2]
            team.team_abbrv_name = result[3]
            team.from_season = result[4]
            team.to_season = result[5]
            team.espn_team_id = result[6]
            team.espn_team_url = result[7]
            team.espn_team_name = result[8]
            team.espn_team_abbrv_name = result[9]
            new_team_ls.append(team)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_team_ls) == 0:
        logging.warning("No more coach need to be imported to Neo4j")
        return

    # region create team nodes in Neo4j
    created_node_team_id_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for team in new_team_ls:
            new_created_node_team_id_ls = neo4j_engine.create_team_node(team)
            created_node_team_id_ls.extend(new_created_node_team_id_ls)
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_node_team_id_ls) == 0:
        return

    # region update the node creation status in MySQL
    sql = """
        UPDATE TEAM_INDEX SET need_create_team_node = FALSE
        WHERE team_id = %(team_id)s
    """
    conn = None
    cursor = None
    try:
        logging.info("Updating process status to MySQL")
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.executemany(sql, created_node_team_id_ls)
        conn.commit()
        logging.info("Done")
    except:
        conn.rollback()
        logging.error("", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion


def create_stadium_nodes(max_increment_size):
    # region retrieve player honor info from MySQL
    new_stadium_ls = []
    sql = """
        SELECT name
        FROM STADIUM_INDEX
        WHERE need_create_stadium_node IS TRUE
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            stadium = Stadium()
            stadium.stadium_name = result[0]
            new_stadium_ls.append(stadium)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_stadium_ls) == 0:
        logging.warning("No more stadium need to be imported to Neo4j")
        return

    # region create player nodes in Neo4j
    created_node_stadium_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for stadium in new_stadium_ls:
            new_created_node_stadium_ls = neo4j_engine.create_stadium_node(stadium)
            created_node_stadium_ls.extend(new_created_node_stadium_ls)
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_node_stadium_ls) == 0:
        return

    # region update the node creation status in MySQL
    sql = """
        UPDATE STADIUM_INDEX SET need_create_stadium_node = FALSE
        WHERE name = %(stadium_name)s
    """
    conn = None
    cursor = None
    try:
        logging.info("Updating process status to MySQL")
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.executemany(sql, created_node_stadium_ls)
        conn.commit()
        logging.info("Done")
    except:
        conn.rollback()
        logging.error("", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion


def create_team_used_name_nodes(max_increment_size):
    # TODO: build team_used_name node and connect it the team node
    sql = """
        SELECT DISTINCT registered_name, registered_abbrv_name, GROUP_CONCAT(season SEPARATOR ", ")
        FROM TEAM_INFO_PER_SEASON
        GROUP BY registered_name, registered_abbrv_name
    """
    pass


def create_normal_person_nodes(max_increment_size):
    # region retrieve player honor info from MySQL
    new_person_ls = []
    # sql = """
    #     SELECT DISTINCT wikidata_id, father
    #     FROM PLAYER_BASIC_WIKIDATA
    #     WHERE father IS NOT NULL
    #     LIMIT %s
    # """
    sql = """
        SELECT DISTINCT wikidata_id, child 
        FROM PLAYER_BASIC_WIKIDATA
        WHERE child IS NOT NULL
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            source_id = result[0]
            person_name_ls = result[1].split("; ")
            for person_name in person_name_ls:
                person = Person()
                person.name = person_name
                person.source_id = source_id
                new_person_ls.append(person)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_person_ls) == 0:
        logging.warning("No more person need to be imported to Neo4j")
        return

    # region create person nodes in Neo4j
    created_node_person_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for person in new_person_ls:
            new_created_node_person_ls = neo4j_engine.create_normal_person_node(person)
            created_node_person_ls.extend(new_created_node_person_ls)
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    logging.info("Done.")

    if len(created_node_person_ls) == 0:
        return


def create_player_achieved_honor_relationship(max_increment_size):
    # region retrieve player achieved honor relationships from MySQL
    new_player_achieved_honor_ls = []
    sql = """
        SELECT player_id, award, season, year FROM PLAYER_HONOR
        WHERE need_create_player_achieved_honor_relationship IS TRUE
        ORDER BY season DESC, year DESC
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            player_achieved_honor = PlayerAchievedHonor()
            player_achieved_honor.player_id = result[0]
            player_achieved_honor.honor_title = result[1]
            player_achieved_honor.season = result[2]
            player_achieved_honor.year = result[3]
            new_player_achieved_honor_ls.append(player_achieved_honor)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_player_achieved_honor_ls) == 0:
        logging.warning("No more player-achieved-honor need to be imported to Neo4j")
        return

    # region create team-served-player nodes in Neo4j
    created_relationship_player_achieved_honor_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for player_achieved_honor in new_player_achieved_honor_ls:
            new_created_relationship_player_achieved_honor_ls = (
                neo4j_engine.create_player_achieved_honor_relationship(
                    player_achieved_honor
                )
            )
            created_relationship_player_achieved_honor_ls.extend(
                new_created_relationship_player_achieved_honor_ls
            )
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_relationship_player_achieved_honor_ls) == 0:
        return

    # region update the node creation status in MySQL
    conn = None
    cursor = None
    try:
        logging.info("Updating process status to MySQL")
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        for player_achieved_honor in created_relationship_player_achieved_honor_ls:
            if (
                player_achieved_honor["season"] is not None
                and player_achieved_honor["year"] is not None
            ):
                sql = """
                    UPDATE PLAYER_HONOR SET need_create_player_achieved_honor_relationship = FALSE
                    WHERE player_id = %(player_id)s AND award = %(award)s AND season = %(season)s
                        AND year = %(year)s
                """
            elif player_achieved_honor["year"] is None:
                sql = """
                    UPDATE PLAYER_HONOR SET need_create_player_achieved_honor_relationship = FALSE
                    WHERE player_id = %(player_id)s AND award = %(award)s AND season = %(season)s
                        AND year IS NULL
                """
            elif player_achieved_honor["season"] is None:
                sql = """
                    UPDATE PLAYER_HONOR SET need_create_player_achieved_honor_relationship = FALSE
                    WHERE player_id = %(player_id)s AND award = %(award)s AND season IS NULL
                        AND year = %(year)s
                """
            else:
                sql = """
                    UPDATE PLAYER_HONOR SET need_create_player_achieved_honor_relationship = FALSE
                    WHERE player_id = %(player_id)s AND award = %(award)s AND season IS NULL
                        AND year IS NULL
                """
            cursor.execute(sql, player_achieved_honor)
            conn.commit()
        logging.info("Done")
    except:
        conn.rollback()
        logging.error("", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion


def create_team_served_player_relationships(max_increment_size):
    # region retrieve team served player relationships from MySQL
    new_team_served_player_ls = []
    sql = """
        SELECT player_id, team_id, season FROM TEAM_SERVED_PLAYER
        WHERE need_create_team_served_player_relationship IS TRUE
        ORDER BY season DESC, team_id ASC, player_id ASC
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            team_served_player = TeamServedPlayer()
            team_served_player.player_id = result[0]
            team_served_player.team_id = result[1]
            team_served_player.season = result[2]
            new_team_served_player_ls.append(team_served_player)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_team_served_player_ls) == 0:
        logging.warning("No more team-served-player need to be imported to Neo4j")
        return

    # region create team-served-player nodes in Neo4j
    created_relationship_team_served_player_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for team_served_player in new_team_served_player_ls:
            new_created_relationship_team_served_player_ls = (
                neo4j_engine.create_team_served_player_relationship(team_served_player)
            )
            created_relationship_team_served_player_ls.extend(
                new_created_relationship_team_served_player_ls
            )
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_relationship_team_served_player_ls) == 0:
        return

    # region update the node creation status in MySQL
    sql = """
        UPDATE TEAM_SERVED_PLAYER SET need_create_team_served_player_relationship = FALSE
        WHERE player_id = %(player_id)s AND team_id = %(team_id)s AND season = %(season)s
    """
    conn = None
    cursor = None
    try:
        logging.info("Updating process status to MySQL")
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.executemany(sql, created_relationship_team_served_player_ls)
        conn.commit()
        logging.info("Done")
    except:
        conn.rollback()
        logging.error("", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion


def create_team_served_coach_relationship(max_increment_size):
    # region retrieve team served coach relationships from MySQL
    new_team_served_coach_ls = []
    sql = """
        SELECT coach_id, team_id, season, coach_job_title FROM TEAM_SERVED_COACH
        WHERE need_create_team_served_coach_relationship IS TRUE AND LOWER(coach_job_title) LIKE '%coach%'
        ORDER BY season DESC, team_id ASC, coach_id ASC
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            team_served_coach = TeamServedCoach()
            team_served_coach.coach_id = result[0]
            team_served_coach.team_id = result[1]
            team_served_coach.season = result[2]
            team_served_coach.coach_job_title = result[3]
            new_team_served_coach_ls.append(team_served_coach)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_team_served_coach_ls) == 0:
        logging.warning("No more team-served-coach need to be imported to Neo4j")
        return

    # region create team-served-coach nodes in Neo4j
    created_relationship_team_served_coach_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for team_served_coach in new_team_served_coach_ls:
            new_created_relationship_team_served_player_ls = (
                neo4j_engine.create_team_served_coach_relationship(team_served_coach)
            )
            created_relationship_team_served_coach_ls.extend(
                new_created_relationship_team_served_player_ls
            )
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_relationship_team_served_coach_ls) == 0:
        return

    # region update the node creation status in MySQL
    sql = """
        UPDATE TEAM_SERVED_COACH SET need_create_team_served_coach_relationship = FALSE
        WHERE coach_id = %(coach_id)s AND team_id = %(team_id)s AND season = %(season)s
            AND coach_job_title = %(coach_job_title)s
    """
    conn = None
    cursor = None
    try:
        logging.info("Updating process status to MySQL")
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.executemany(sql, created_relationship_team_served_coach_ls)
        conn.commit()
        logging.info("Done")
    except:
        conn.rollback()
        logging.error("", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion


def create_team_managed_executive_relationship(max_increment_size):
    # region retrieve team arena relationships from MySQL
    new_team_managed_executive_ls = []
    sql = """
        SELECT executive_id, team_id, season
        FROM TEAM_EXECUTIVE
        WHERE need_create_managed_relationship IS TRUE
        ORDER BY season DESC, team_id ASC
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            team_managed_executive = TeamManagedExecutive()
            team_managed_executive.executive_id = result[0]
            team_managed_executive.team_id = result[1]
            team_managed_executive.season = result[2]
            new_team_managed_executive_ls.append(team_managed_executive)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_team_managed_executive_ls) == 0:
        logging.warning("No more team-managed-executive need to be imported to Neo4j")
        return

    # region create team-managed-executive nodes in Neo4j
    created_relationship_team_managed_executive_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for team_managed_executive in new_team_managed_executive_ls:
            new_created_relationship_team_managed_executive_ls = (
                neo4j_engine.create_team_managed_executive_relationship(
                    team_managed_executive
                )
            )
            created_relationship_team_managed_executive_ls.extend(
                new_created_relationship_team_managed_executive_ls
            )
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_relationship_team_managed_executive_ls) == 0:
        return

    # region update the node creation status in MySQL
    sql = """
        UPDATE TEAM_EXECUTIVE SET need_create_managed_relationship = FALSE
        WHERE executive_id = %(executive_id)s AND team_id = %(team_id)s AND season = %(season)s
    """
    conn = None
    cursor = None
    try:
        logging.info("Updating process status to MySQL")
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.executemany(sql, created_relationship_team_managed_executive_ls)
        conn.commit()
        logging.info("Done")
    except:
        conn.rollback()
        logging.error("", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion


def create_team_arena_relationships(max_increment_size):
    # region retrieve team arena relationships from MySQL
    new_team_arena_ls = []
    sql = """
        SELECT team_id, arena, season, attendance
        FROM TEAM_ARENA
        WHERE need_create_team_arena_relationship IS TRUE
        ORDER BY season DESC, arena ASC, team_id ASC
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            team_arena = TeamArena()
            team_arena.team_id = result[0]
            team_arena.arena = result[1]
            team_arena.season = result[2]
            team_arena.attendance = result[3]
            new_team_arena_ls.append(team_arena)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_team_arena_ls) == 0:
        logging.warning("No more team-arena need to be imported to Neo4j")
        return

    # region create team-arena nodes in Neo4j
    created_relationship_team_arena_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for team_arena in new_team_arena_ls:
            new_created_relationship_team_arena_ls = (
                neo4j_engine.create_team_arena_relationship(team_arena)
            )
            created_relationship_team_arena_ls.extend(
                new_created_relationship_team_arena_ls
            )
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_relationship_team_arena_ls) == 0:
        return

    # region update the node creation status in MySQL
    sql_not_null = """
        UPDATE TEAM_ARENA SET need_create_team_arena_relationship = FALSE
        WHERE team_id = %(team_id)s AND season = %(season)s AND arena = %(arena)s AND attendance = %(attendance)s
    """
    sql_null = """
        UPDATE TEAM_ARENA SET need_create_team_arena_relationship = FALSE
        WHERE team_id = %(team_id)s AND season = %(season)s AND arena = %(arena)s AND attendance IS NULL
    """
    conn = None
    cursor = None
    try:
        logging.info("Updating process status to MySQL")
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        for created_relationship_team_arena in created_relationship_team_arena_ls:
            if created_relationship_team_arena["attendance"] is None:
                sql = sql_null
            else:
                sql = sql_not_null
            cursor.execute(sql, created_relationship_team_arena)
            conn.commit()
        logging.info("Done")
    except:
        conn.rollback()
        logging.error("", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion


def create_player_has_relative_relationships(max_increment_size):
    # region retrieve player relative relationships from MySQL
    new_player_relative_ls = []
    # relationship = "father"
    # sql = """
    #     SELECT DISTINCT BRWEL.player_id, PBW.father, BRWEL.wikidata_id
    #     FROM PLAYER_BASIC_WIKIDATA PBW
    #              JOIN BASKETBALL_REFERENCE_WIKIDATA_ENTITY_LINK BRWEL on PBW.wikidata_id = BRWEL.wikidata_id
    #     WHERE PBW.father IS NOT NULL
    #     LIMIT %s
    # """
    relationship = "sibling"
    sql = """
        SELECT DISTINCT BRWEL.player_id, PBW.sibling, BRWEL.wikidata_id
        FROM PLAYER_BASIC_WIKIDATA PBW
                 JOIN BASKETBALL_REFERENCE_WIKIDATA_ENTITY_LINK BRWEL on PBW.wikidata_id = BRWEL.wikidata_id
        WHERE PBW.sibling IS NOT NULL
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            relative_name_ls = result[1].split("; ")
            for relative_name in relative_name_ls:
                player_relative = PlayerRelative()
                player_relative.player_id = result[0]
                player_relative.relative_name = relative_name
                player_relative.source_id = result[2]
                player_relative.relationship = relationship
                new_player_relative_ls.append(player_relative)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # endregion

    if len(new_player_relative_ls) == 0:
        logging.warning("No more has-%s need to be imported to Neo4j", relationship)
        return

    # region create team-arena nodes in Neo4j
    created_relationship_has_relative_ls = []
    neo4j_engine = None
    try:
        neo4j_engine = Neo4jEngine(**neo4j_db_config)
        for player_relative in new_player_relative_ls:
            new_created_relationship_has_relative_ls = (
                neo4j_engine.create_player_has_relative_relationship(player_relative)
            )
            created_relationship_has_relative_ls.extend(
                new_created_relationship_has_relative_ls
            )
    finally:
        if neo4j_engine:
            neo4j_engine.close()
    # endregion

    if len(created_relationship_has_relative_ls) == 0:
        return

    logging.info("Done.")


def create_same_as_relationships():
    # MATCH (p1:Player)-[:has_sibling]->(p2:NormalPerson), (p3:Player)-[:has_sibling]->(p4:NormalPerson)
    # WHERE p1.name = p4.name AND p2.name = p3.name
    # CREATE (p4)-[r:same_as]->(p1)
    # RETURN ID(r)

    # MATCH (p1:Player)-[:has_father]->(p2:NormalPerson), (p3:Player)-[:has_child]->(p4:NormalPerson)
    # WHERE p1.name = p4.name AND p2.name = p3.name
    # CREATE (p4)-[r:same_as]->(p1)
    # RETURN ID(r)

    # MATCH (p1:Player)-[:has_child]->(p2:NormalPerson), (p3:Player)-[:has_father]->(p4:NormalPerson)
    # WHERE p1.name = p4.name AND p2.name = p3.name
    # CREATE (p4)-[r:same_as]->(p1)
    # RETURN ID(r)

    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "operation",
        choices=[
            "create_player_nodes",
            "create_player_honor_nodes",
            "create_coach_nodes",
            "create_executive_nodes",
            "create_team_nodes",
            "create_stadium_nodes",
            "create_normal_person_nodes",
            "create_player_achieved_honor_relationship",
            "create_team_served_player_relationships",
            "create_team_served_coach_relationship",
            "create_team_managed_executive_relationship",
            "create_team_arena_relationships",
            "create_player_has_relative_relationships",
        ],
        help="the operation to take",
    )
    parser.add_argument(
        "max_increment_size",
        type=int,
        metavar="max increment size",
        help="the maximum increment size of the data processed by the specified operation",
    )

    args = parser.parse_args()
    args = vars(args)
    operation = args["operation"]
    max_increment_size = args["max_increment_size"]

    f = getattr(sys.modules[__name__], operation)
    f(max_increment_size)


if __name__ == "__main__":
    main()
