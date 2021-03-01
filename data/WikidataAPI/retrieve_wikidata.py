#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import math
import re
import time
import traceback
import urllib
import uuid

import dateutil
import mysql.connector
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

logging.basicConfig(
    filename="wikidata_api.log",
    format="%(asctime)s [%(levelname)s]: %(message)s",
    level=logging.INFO,
)


mysql_db_config = {
    "db": "inf558",
    "user": "inf558",
    "passwd": "inf558",
    "host": "ec2-54-67-29-193.us-west-1.compute.amazonaws.com",
}


def get_mysql_conn():
    conn = mysql.connector.connect(
        host=mysql_db_config["host"],
        database=mysql_db_config["db"],
        user=mysql_db_config["user"],
        password=mysql_db_config["passwd"],
    )
    conn.set_charset_collation("utf8mb4", "utf8mb4_unicode_ci")
    return conn


def load_unretrieved_wikidata_id(max_increment_size):
    unretrieved_wikidata_id_ls = []
    sql = """
        SELECT DISTINCT wikidata_id
        FROM (
            SELECT WI.wikidata_id AS wikidata_id
            FROM PLAYER_BASIC PB
                     JOIN WIKIDATA_INDEX WI ON PB.player_name = WI.player_name
                     JOIN PLAYER_INDEX PI on PB.player_id = PI.player_id
            WHERE need_retrieve_from_wikidata IS TRUE
            ORDER BY PI.to_year DESC, PI.from_year ASC) T
        LIMIT %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            unretrieved_wikidata_id_ls.append(result[0])
    except Exception:
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return unretrieved_wikidata_id_ls


def get_wikidata_id(player_uri):
    wikiID_list = re.findall(r"/Q\d*", player_uri)
    wikiID = str("wd:" + wikiID_list[0].replace("/", ""))
    return wikiID


def get_date_of_birth(player_birthday):
    player_birthday = str(player_birthday)
    m = re.match(r"^\d{4}-\d{2}-\d{2}T.+?$", player_birthday)
    if m:
        player_birthday_dt = dateutil.parser.parse(player_birthday)
        return player_birthday_dt.strftime("%Y-%m-%d")
    else:
        return None


def unify_attributes(result_df):
    for position in range(len(result_df["player.value"])):
        # weight unit normalization (pound and gram)
        if (
            result_df["player_weightUnit_list.value"][position]
            and result_df["player_weightUnit_list.value"][position] == "pound"
        ):
            result_df["player_weight_list.value"][position] = str(
                float(result_df["player_weight_list.value"][position]) * 0.453592
            )
        if result_df["player_weightUnit_list.value"][position] == "gram":
            result_df["player_weight_list.value"][position] = str(
                float(result_df["player_weight_list.value"][position]) / 1000
            )

        # height unit normalization (metre, inch)
        if result_df["player_heightUnit_list.value"][position] == "metre":
            height_list = result_df["player_height_list.value"][position].split(";")
            transfer_height_list = list()
            for each_height in height_list:
                each_height = each_height.strip()
                each_height = float(each_height) * 100
                transfer_height_list.append(each_height)
            result_df["player_height_list.value"][position] = transfer_height_list[0]

        if result_df["player_heightUnit_list.value"][position] == "inch":
            height_list = result_df["player_height_list.value"][position].split(";")
            transfer_height_list = list()
            for each_height in height_list:
                each_height = each_height.strip()
                each_height = float(each_height) * 2.54
                transfer_height_list.append(each_height)
            result_df["player_height_list.value"][position] = transfer_height_list[0]

        if result_df["player_heightUnit_list.value"][position] == "centimetre":
            height_list = result_df["player_height_list.value"][position].split(";")
            result_df["player_height_list.value"][position] = height_list[0]

        # transfer NaN to None
        if (
            result_df["player_father.value"][position]
            and result_df["player_mother.value"][position]
        ):
            father = result_df["player_father.value"][position]
            mother = result_df["player_mother.value"][position]
            if not isinstance(father, str) and math.isnan(father):
                result_df["player_father.value"][position] = None
            if not isinstance(mother, str) and math.isnan(mother):
                result_df["player_mother.value"][position] = None

        birth_place = result_df["player_placeBirthLabel.value"][position]
        if not isinstance(birth_place, str) and math.isnan(birth_place):
            result_df["player_placeBirthLabel.value"][position] = None

    return result_df


def df2dict_ls(result_df):
    result_ls = []

    for position in range(len(result_df["player.value"])):
        if (
            result_df["player_father.value"][position]
            or result_df["player_mother.value"][position]
            or result_df["player_sibling_list.value"][position]
            or result_df["player_spouse_list.value"][position]
            or result_df["player_child_list.value"][position]
            or result_df["player_edu_list.value"][position]
            or result_df["player_weight_list.value"][position]
            or result_df["player_height_list.value"][position]
            or result_df["player_dateBirthLabel.value"][position]
            or result_df["player_placeBirthLabel.value"][position]
        ):

            player_dict = dict()
            player_dict["record_id"] = str(uuid.uuid1())
            player_dict["wikidata_id"] = get_wikidata_id(
                result_df["player.value"][position]
            )

            player_dict["player_name"] = result_df["playerLabel.value"][position]

            # height
            if result_df["player_height_list.value"][position]:
                player_dict["height"] = float(
                    result_df["player_height_list.value"][position]
                )
                player_dict["height"] = round(player_dict["height"], 2)
            else:
                player_dict["height"] = 0

            # weight
            if result_df["player_weight_list.value"][position]:
                player_dict["weight"] = float(
                    result_df["player_weight_list.value"][position]
                )
                player_dict["weight"] = round(player_dict["weight"], 2)
            else:
                player_dict["weight"] = 0

            # date_of_birth
            if result_df["player_dateBirthLabel.value"][position]:
                player_dict["date_of_birth"] = get_date_of_birth(
                    result_df["player_dateBirthLabel.value"][position]
                )
            else:
                player_dict["date_of_birth"] = None

            # place_of_birth
            if result_df["player_placeBirthLabel.value"][position]:
                player_dict["place_of_birth"] = result_df[
                    "player_placeBirthLabel.value"
                ][position]
            else:
                player_dict["place_of_birth"] = None

            # education
            if result_df["player_edu_list.value"][position]:
                player_dict["education"] = result_df["player_edu_list.value"][position]
            else:
                player_dict["education"] = None

            # father
            if result_df["player_father.value"][position]:
                player_dict["father"] = result_df["player_father.value"][position]
            else:
                player_dict["father"] = None

            # mother
            if result_df["player_mother.value"][position]:
                player_dict["mother"] = result_df["player_mother.value"][position]
            else:
                player_dict["mother"] = None

            # sibling
            if result_df["player_sibling_list.value"][position]:
                player_dict["sibling"] = result_df["player_sibling_list.value"][
                    position
                ]
            else:
                player_dict["sibling"] = None

            # spouse
            if result_df["player_spouse_list.value"][position]:
                player_dict["spouse"] = result_df["player_spouse_list.value"][position]
            else:
                player_dict["spouse"] = None

            # child
            if result_df["player_child_list.value"][position]:
                player_dict["child"] = result_df["player_child_list.value"][position]
            else:
                player_dict["child"] = None

            result_ls.append(player_dict)

    return result_ls


def retrieve_from_wikidata(unretrieved_wikidata_id_ls):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)

    data_sql = """
        INSERT INTO PLAYER_BASIC_WIKIDATA (
            record_id, wikidata_id, player_name, height, weight, date_of_birth,
            place_of_birth, education, father, mother, sibling,
            spouse, child
        )
        VALUES (
            %(record_id)s, %(wikidata_id)s, %(player_name)s, %(height)s, %(weight)s,
            %(date_of_birth)s, %(place_of_birth)s,
            %(education)s, %(father)s, %(mother)s, %(sibling)s,
            %(spouse)s, %(child)s
        )
    """

    status_sql = """
        UPDATE WIKIDATA_INDEX SET need_retrieve_from_wikidata = FALSE
        WHERE wikidata_id = %s
    """

    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        for wikidata_id in unretrieved_wikidata_id_ls:
            try:
                query = (
                    """
                    SELECT
                        ?player ?playerLabel
                        (GROUP_CONCAT(DISTINCT ?player_fatherLabel; SEPARATOR="; ") AS ?player_father)
                        (GROUP_CONCAT(DISTINCT ?player_motherLabel; SEPARATOR="; ") AS ?player_mother)
                        (GROUP_CONCAT(DISTINCT ?player_siblingLabel; SEPARATOR="; ") AS ?player_sibling_list)
                        (GROUP_CONCAT(DISTINCT ?player_spouseLabel; SEPARATOR="; ") AS ?player_spouse_list)
                        (GROUP_CONCAT(DISTINCT ?player_childLabel; SEPARATOR="; ") AS ?player_child_list)
                        (GROUP_CONCAT(DISTINCT ?player_educateLabel; SEPARATOR="; ") AS ?player_edu_list)
                        (GROUP_CONCAT(DISTINCT ?player_weightLabel; SEPARATOR="; ") AS ?player_weight_list)
                        (GROUP_CONCAT(DISTINCT ?player_weight_unitLabel; SEPARATOR="; ") AS ?player_weightUnit_list)
                        (GROUP_CONCAT(DISTINCT ?player_heightLabel; SEPARATOR="; ") AS ?player_height_list)
                        (GROUP_CONCAT(DISTINCT ?player_height_unitLabel; SEPARATOR="; ") AS ?player_heightUnit_list)
                        ?player_dateBirthLabel
                        ?player_placeBirthLabel
                    WHERE {
                        ?player wdt:P31? """
                    + wikidata_id
                    + """ .
                        OPTIONAL { ?player wdt:P22 ?player_father }
                        OPTIONAL { ?player wdt:P25 ?player_mother }
                        OPTIONAL { ?player wdt:P3373 ?player_sibling }
                        OPTIONAL { ?player wdt:P26 ?player_spouse }
                        OPTIONAL { ?player wdt:P40 ?player_child }
                        OPTIONAL { ?player wdt:P69 ?player_educate }
                        OPTIONAL { ?player p:P2067 [ps:P2067 ?player_weight;
                                                    psv:P2067/wikibase:quantityUnit ?player_weight_unit] }
                        OPTIONAL { ?player p:P2048 [ps:P2048 ?player_height;
                                                    psv:P2048/wikibase:quantityUnit ?player_height_unit] }
                        OPTIONAL { ?player wdt:P569 ?player_dateBirth }
                        OPTIONAL { ?player wdt:P19 ?player_placeBirth }

                        SERVICE wikibase:label { bd:serviceParam wikibase:language "en".
                                                ?player rdfs:label ?playerLabel .
                                                ?player_father rdfs:label ?player_fatherLabel .
                                                ?player_mother rdfs:label ?player_motherLabel .
                                                ?player_sibling rdfs:label ?player_siblingLabel .
                                                ?player_spouse rdfs:label ?player_spouseLabel .
                                                ?player_child rdfs:label ?player_childLabel .
                                                ?player_educate rdfs:label ?player_educateLabel .
                                                ?player_weight rdfs:label ?player_weightLabel .
                                                ?player_weight_unit rdfs:label ?player_weight_unitLabel .
                                                ?player_height rdfs:label ?player_heightLabel .
                                                ?player_height_unit rdfs:label ?player_height_unitLabel .
                                                ?player_dateBirth rdfs:label ?player_dateBirthLabel .
                                                ?player_placeBirth rdfs:label ?player_placeBirthLabel . }
                    }
                    GROUP BY ?player ?playerLabel ?player_dateBirthLabel ?player_placeBirthLabel
                """
                )
                logging.info("Retrieving from Wikidata - %s", wikidata_id)
                sparql.setQuery(query)
                resp = sparql.query().convert()
                result_df = pd.json_normalize(resp["results"]["bindings"])

                norm_result_df = unify_attributes(result_df)
                result_ls = df2dict_ls(norm_result_df)

                cursor.executemany(data_sql, result_ls)
                cursor.execute(status_sql, (wikidata_id,))
                conn.commit()
                logging.info("Committed to MySQL - %s", wikidata_id)
                time.sleep(1)
            except Exception as e:
                if isinstance(e, urllib.error.HTTPError):
                    time.sleep(10)
                logging.warning("", exc_info=True)
                if conn:
                    conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument(
        "max_increment_size",
        type=int,
        help="the maximum number of record processed each run",
    )

    args = parse.parse_args()
    args = vars(args)
    max_increment_size = args["max_increment_size"]

    start = time.time()

    logging.info("Start retrieving ...")
    unretrieved_wikidata_id_ls = load_unretrieved_wikidata_id(max_increment_size)
    retrieve_from_wikidata(unretrieved_wikidata_id_ls)

    end = time.time()
    logging.info("Done (%s).", end - start)


if __name__ == "__main__":
    main()
