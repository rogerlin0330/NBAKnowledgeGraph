#!/usr/bin/env python
# -*- coding: utf-8 -*-
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import argparse
import re
import uuid
import json
import math
import dateutil
from collections import defaultdict
import mysql.connector
import traceback
import datetime


def retrieve_from_wikidata_first_round():
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(
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
    
        WHERE 
        {
          ?player wdt:P106/(wdt:P279|wdt:P31)* wd:Q3665646 .  # occupation is basketball player
          ?player wdt:P118 wd:Q155223 .  # league is NBA
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
                                  ?player_placeBirth rdfs:label ?player_placeBirthLabel .
                                  
                                }
        }
        GROUP BY ?player ?playerLabel ?player_dateBirthLabel ?player_placeBirthLabel
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    result_df = pd.json_normalize(results["results"]["bindings"])
    # print(result_df[['player.value', 'playerLabel.value', 'player_dateBirthLabel.value',
    #                  'player_placeBirthLabel.value']].head())
    return result_df


def type_transfer(dataset):
    for position in range(len(dataset["player.value"])):
        # weight unit normalization (pound and gram)
        if (
            dataset["player_weightUnit_list.value"][position]
            and dataset["player_weightUnit_list.value"][position] == "pound"
        ):
            dataset["player_weight_list.value"][position] = str(
                float(dataset["player_weight_list.value"][position]) * 0.453592
            )
        if dataset["player_weightUnit_list.value"][position] == "gram":
            dataset["player_weight_list.value"][position] = str(
                float(dataset["player_weight_list.value"][position]) / 1000
            )

        # height unit normalization (metre, inch)
        if dataset["player_heightUnit_list.value"][position] == "metre":
            height_list = dataset["player_height_list.value"][position].split(";")
            transfer_height_list = list()
            for each_height in height_list:
                each_height = each_height.strip()
                each_height = float(each_height) * 100
                transfer_height_list.append(each_height)
            dataset["player_height_list.value"][position] = transfer_height_list[0]

        if dataset["player_heightUnit_list.value"][position] == "inch":
            height_list = dataset["player_height_list.value"][position].split(";")
            transfer_height_list = list()
            for each_height in height_list:
                each_height = each_height.strip()
                each_height = float(each_height) * 2.54
                transfer_height_list.append(each_height)
            dataset["player_height_list.value"][position] = transfer_height_list[0]

        if dataset["player_heightUnit_list.value"][position] == "centimetre":
            height_list = dataset["player_height_list.value"][position].split(";")
            dataset["player_height_list.value"][position] = height_list[0]

        # transfer NaN to None
        if (
            dataset["player_father.value"][position]
            and dataset["player_mother.value"][position]
        ):
            father = dataset["player_father.value"][position]
            mother = dataset["player_mother.value"][position]
            if not isinstance(father, str) and math.isnan(father):
                dataset["player_father.value"][position] = None
            if not isinstance(mother, str) and math.isnan(mother):
                dataset["player_mother.value"][position] = None

        birth_place = dataset["player_placeBirthLabel.value"][position]
        if not isinstance(birth_place, str) and math.isnan(birth_place):
            dataset["player_placeBirthLabel.value"][position] = None

    return dataset


def get_wikidata(player_uri):
    wikiID_list = re.findall(r"/Q\d*", player_uri)
    wikiID = str("wd:" + wikiID_list[0].replace("/", ""))
    return wikiID


def get_date_birth(player_birthday):
    player_birthday = str(player_birthday)
    m = re.match(r"^\d{4}-\d{2}-\d{2}T.+?$", player_birthday)
    if m:
        player_birthday_dt = dateutil.parser.parse(player_birthday)
        return player_birthday_dt.strftime("%Y-%m-%d")
    else:
        return None


def get_mysql_conn():
    conn = mysql.connector.connect(
        host="ec2-54-67-29-193.us-west-1.compute.amazonaws.com",
        database="inf558",
        user="inf558",
        password="inf558",
    )
    conn.set_charset_collation("utf8mb4", "utf8mb4_unicode_ci")
    return conn


def serialize_data(input_file, output_file):
    result_ls = list()
    seen_player_id_dict = dict()

    for position in range(len(input_file["player.value"])):
        if (
            input_file["player_father.value"][position]
            or input_file["player_mother.value"][position]
            or input_file["player_sibling_list.value"][position]
            or input_file["player_spouse_list.value"][position]
            or input_file["player_child_list.value"][position]
            or input_file["player_edu_list.value"][position]
            or input_file["player_weight_list.value"][position]
            or input_file["player_height_list.value"][position]
            or input_file["player_dateBirthLabel.value"][position]
            or input_file["player_placeBirthLabel.value"][position]
        ):

            player_dict = dict()
            player_dict["record_id"] = str(uuid.uuid1())
            player_dict["wikidata_id"] = get_wikidata(
                input_file["player.value"][position]
            )
            seen_player_id_dict[player_dict["wikidata_id"]] = 1

            player_dict["player_name"] = input_file["playerLabel.value"][position]

            # height
            if input_file["player_height_list.value"][position]:
                player_dict["height"] = float(
                    input_file["player_height_list.value"][position]
                )
                player_dict["height"] = round(player_dict["height"], 2)
            else:
                player_dict["height"] = 0

            # weight
            if input_file["player_weight_list.value"][position]:
                player_dict["weight"] = float(
                    input_file["player_weight_list.value"][position]
                )
                player_dict["weight"] = round(player_dict["weight"], 2)
            else:
                player_dict["weight"] = 0

            # date_of_birth
            if input_file["player_dateBirthLabel.value"][position]:
                player_dict["date_of_birth"] = get_date_birth(
                    input_file["player_dateBirthLabel.value"][position]
                )
            else:
                player_dict["date_of_birth"] = None

            # place_of_birth
            if input_file["player_placeBirthLabel.value"][position]:
                player_dict["place_of_birth"] = input_file[
                    "player_placeBirthLabel.value"
                ][position]
            else:
                player_dict["place_of_birth"] = None

            # education
            if input_file["player_edu_list.value"][position]:
                player_dict["education"] = input_file["player_edu_list.value"][position]
            else:
                player_dict["education"] = None

            # father
            if input_file["player_father.value"][position]:
                player_dict["father"] = input_file["player_father.value"][position]
            else:
                player_dict["father"] = None

            # mother
            if input_file["player_mother.value"][position]:
                player_dict["mother"] = input_file["player_mother.value"][position]
            else:
                player_dict["mother"] = None

            # sibling
            if input_file["player_sibling_list.value"][position]:
                player_dict["sibling"] = input_file["player_sibling_list.value"][
                    position
                ]
            else:
                player_dict["sibling"] = None

            # spouse
            if input_file["player_spouse_list.value"][position]:
                player_dict["spouse"] = input_file["player_spouse_list.value"][position]
            else:
                player_dict["spouse"] = None

            # child
            if input_file["player_child_list.value"][position]:
                player_dict["child"] = input_file["player_child_list.value"][position]
            else:
                player_dict["child"] = None

            result_ls.append(player_dict)

    # conn = None
    # cursor = None
    # try:
    #     sql = """
    #         INSERT INTO PLAYER_BASIC_WIKIDATA (
    #             record_id, wikidata_id, player_name, height, weight, date_of_birth,
    #             place_of_birth, education, father, mother, sibling,
    #             spouse, child
    #         )
    #         VALUES (
    #             %(record_id)s, %(wikidata_id)s, %(player_name)s, %(height)s, %(weight)s,
    #             %(date_of_birth)s, %(place_of_birth)s,
    #             %(education)s, %(father)s, %(mother)s, %(sibling)s,
    #             %(spouse)s, %(child)s
    #         )
    #     """
    #
    #     conn = get_mysql_conn()
    #     cursor = conn.cursor(buffered=True)
    #     cursor.executemany(sql, result_ls)
    #     conn.commit()
    #     print("committed first round result to database")
    #     return seen_player_id_dict
    # except Exception:
    #     traceback.print_exc()
    #     if conn:
    #         conn.rollback()
    # finally:
    #     if cursor:
    #         cursor.close()
    #     if conn:
    #         conn.close()

    return seen_player_id_dict


def retrieve_from_wikidata_second_round(seen_player_id_dict):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = """
        SELECT ?player ?playerLabel
        WHERE {
            ?player wdt:P106/(wdt:P279|wdt:P31)* wd:Q3665646 .
            ?player wdt:P21 wd:Q6581097 .
            ?player wdt:P27 wd:Q30 .
            OPTIONAL { ?player wdt:P1532 wd:Q30 } .
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } .
        }
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    wikidata_qualifier_rs = sparql.query().convert()
    qualife_result_df = pd.json_normalize(wikidata_qualifier_rs["results"]["bindings"])

    resultf_df_ls = []

    wikidata_qualifier_ls = qualife_result_df["player.value"]
    wikidate_label_ls = qualife_result_df["playerLabel.value"]

    new_wikidata_id_ls = []
    test = 0
    for i, wikidata_qualifier in enumerate(wikidata_qualifier_ls):
        wikidata_qualifier = get_wikidata(wikidata_qualifier)
        wikidate_label = wikidate_label_ls[i]
        wikidate_label = wikidate_label.strip()

        new_wikidata_id_ls.append(
            dict(wikidata_id=wikidata_qualifier, player_name=wikidate_label)
        )

        # 查询对应信息

        # sparql.setQuery(query_each_person)
        # sparql.setReturnFormat(JSON)
        # wikidata_rs = sparql.query().convert()
        # wiki_df = pd.json_normalize(wikidata_rs["results"]["bindings"])
        #
        # resultf_df_ls.append(wiki_df)
        # if len(resultf_df_ls) == 10000:
        #     break

    conn = None
    cursor = None
    try:
        sql = """
            INSERT IGNORE INTO WIKIDATA_INDEX (wikidata_id, player_name)
            VALUE (%(wikidata_id)s, %(player_name)s)
        """
        print(datetime.datetime.now())
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.executemany(sql, new_wikidata_id_ls)
        conn.commit()
        print("committed new wikidata id to database")
    except Exception:
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    ########
    # result_df = pd.concat(resultf_df_ls)
    # print(res)

    # return wiki_df


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("output_file", type=str, help="the output file name")

    args = parse.parse_args()
    args = vars(args)
    output_file = args["output_file"]

    # player_wikidata = retrieve_from_wikidata_first_round()
    # after_nor_wikidata = type_transfer(player_wikidata)
    # seen_player_id_dict = serialize_data(after_nor_wikidata, output_file)

    second_wikidata = retrieve_from_wikidata_second_round(None)

    # print(second_wikidata["player.value", "playerLabel.value", "player_weight_list.value", "player_weightUnit_list.value"])
    # for i in range(len(second_wikidata)):
    #     print(second_wikidata[['player.value', 'playerLabel.value']][i])

    # sec_nor_wikidata = type_transfer(second_wikidata)
    # serialize_data(sec_nor_wikidata, "test2.json")


if __name__ == "__main__":
    main()
