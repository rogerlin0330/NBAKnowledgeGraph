#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import re
import traceback

import mysql.connector
import rltk

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


def load_samename_player_wikiid():
    samename_player_dict = dict()
    sql = """
        SELECT PB.player_name, GROUP_CONCAT(DISTINCT PBW.wikidata_id SEPARATOR ', ')
        FROM BASKETBALL_REFERENCE_WIKIDATA_ENTITY_LINK BRWEI
                 JOIN PLAYER_BASIC PB on BRWEI.player_id = PB.player_id
                 JOIN PLAYER_BASIC_WIKIDATA PBW on PB.player_name = PBW.player_name AND PB.date_of_birth = PBW.date_of_birth
        GROUP BY PB.player_name
        HAVING COUNT(DISTINCT PBW.wikidata_id) >= 2
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql)
        for result in cursor:
            samename_player_dict[result[0]] = result[1].split(", ")
    except Exception:
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return samename_player_dict


def load_player_basic(samename_player_dict):
    player_basic_list = list()
    sql = """
            SELECT * FROM PLAYER_BASIC 
            WHERE player_name = %s
        """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        for player_name in samename_player_dict.keys():
            cursor.execute(sql, (player_name,))
            for result in cursor:
                res = {
                    "player_id": result[1],
                    "player_name": result[3],
                    "height": result[7],
                    "weight": result[8],
                    "date_of_birth": result[5],
                    "place_of_birth": result[6],
                }
                player_basic_list.append(res)
    except Exception:
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return player_basic_list


def load_player_wikidata(samename_player_dict):
    wikidata_list = list()
    sql = """
        SELECT * FROM PLAYER_BASIC_WIKIDATA 
        WHERE wikidata_id = %s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        for wikidataid in samename_player_dict.values():
            for i in wikidataid:
                cursor.execute(sql, (i,))
                for result in cursor:
                    res = {
                        "wikidata_id": result[1],
                        "player_name": result[2],
                        "height": result[3],
                        "weight": result[4],
                        "date_of_birth": result[5],
                        "place_of_birth": result[6],
                    }
                    wikidata_list.append(res)
    except Exception:
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return wikidata_list


def calc_height_sim(h1, h2):
    sim = 1 - 0.1 * abs(float(h1) - float(h2))
    if sim < 0:
        sim = 0
    return sim


def calc_weight_sim(w1, w2):
    sim = 1 - 0.1 * abs(float(w1) - float(w2))
    if sim < 0:
        sim = 0
    return sim


def calc_birthday_sim(b1, b2):
    return rltk.levenshtein_similarity(b1, b2)


def calc_place_of_birth_sim(p1, p2):
    return rltk.levenshtein_similarity(p1.lower(), p2.lower())


def rule_based_method(bask_re, wikidata):
    MY_TRESH = 0.85

    compared_attr_num = 0
    score = 0

    if bask_re["player_name"] is None or wikidata["player_name"] is None:
        return False, 0
    elif (
        rltk.levenshtein_similarity(bask_re["player_name"], wikidata["player_name"])
        < 0.95
    ):
        return False, 0

    if bask_re["height"] is not None and wikidata["height"] is not None:
        score_height = calc_height_sim(bask_re["height"], wikidata["height"])
        score += 0.25 * score_height
        compared_attr_num += 1
    if bask_re["weight"] is not None and wikidata["weight"] is not None:
        score_weight = calc_weight_sim(bask_re["weight"], wikidata["weight"])
        score += 0.25 * score_weight
        compared_attr_num += 1
    if bask_re["date_of_birth"] is not None and wikidata["date_of_birth"] is not None:
        score_birthday = calc_birthday_sim(
            bask_re["date_of_birth"], wikidata["date_of_birth"]
        )
        score += 0.25 * score_birthday
        compared_attr_num += 1
    if bask_re["place_of_birth"] is not None and wikidata["place_of_birth"] is not None:
        bask_re_place_of_birth = re.split(r"[,，]\s+", bask_re["place_of_birth"])[0]
        score_place = calc_place_of_birth_sim(
            bask_re_place_of_birth, wikidata["place_of_birth"]
        )
        score += 0.25 * score_place
        compared_attr_num += 1

    # rescale
    if compared_attr_num < 2:
        return False, 0
    else:
        score = score / (compared_attr_num * 0.25)
        return score > MY_TRESH, score


def save_matched_records(prediction_list):
    sql = """
        UPDATE BASKETBALL_REFERENCE_WIKIDATA_ENTITY_LINK
            SET wikidata_id = %(wikidata_id)s,
                need_add_wikidata_id_to_player_node = FALSE
        WHERE player_id = %(player_id)s
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(buffered=True)
        cursor.executemany(sql, prediction_list)
        conn.commit()
        print("Committed to db.")
    except Exception:
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def main():
    samename_player = load_samename_player_wikiid()
    basketball_ref_record_ls = load_player_basic(samename_player)
    wikidata_record_ls = load_player_wikidata(samename_player)

    prediction_list = list()
    for wikidata_record in wikidata_record_ls:
        prediction_dict = dict()
        prediction_dict["wikidata_id"] = wikidata_record["wikidata_id"]
        prediction_dict["player_id"] = None

        cand_match_player_id_ls = []

        cache_basketball_ref_record_ls = copy.deepcopy(basketball_ref_record_ls)
        for i in range(len(cache_basketball_ref_record_ls) - 1, -1, -1):
            basketball_ref_record = cache_basketball_ref_record_ls[i]

            result, sim_score = rule_based_method(
                basketball_ref_record, wikidata_record
            )
            if result:
                cand_match_player_id_ls.append(
                    (basketball_ref_record["player_id"], i, sim_score)
                )

        if len(cand_match_player_id_ls) > 0:
            max_score_cand_match_player = max(
                cand_match_player_id_ls, key=lambda x: x[2]
            )
            max_score_cand_match_player_id = max_score_cand_match_player[0]
            prediction_dict["player_id"] = max_score_cand_match_player_id
            prediction_list.append(prediction_dict)

            max_score_cand_match_player_index = max_score_cand_match_player[1]
            basketball_ref_record_ls.pop(max_score_cand_match_player_index)

    save_matched_records(prediction_list)


if __name__ == "__main__":
    main()
