#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import mysql.connector
import numpy as np
import copy
import pandas as pd
from collections import defaultdict


logging.basicConfig(
    filename="similar_player_processor.log",
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


def load_unprocessed_player_id_ls(db_conn, max_increment_size):
    sql = """
        SELECT player_id
        FROM PLAYER_INDEX PI
        WHERE need_find_cand_sim_player IS TRUE
        ORDER BY to_year DESC, from_year ASC
        LIMIT %s
    """
    unprocessed_player_id_ls = []
    cursor = None
    try:
        cursor = db_conn.cursor(buffered=True)
        cursor.execute(sql, (max_increment_size,))
        for result in cursor:
            unprocessed_player_id_ls.append(result[0])
    finally:
        if cursor:
            cursor.close()

    return unprocessed_player_id_ls


def retrieve_candidate_sim_player_id_ls(db_conn, player_id):
    sql = """
        SELECT T1.player_id AS candidate_sim_player_id, T1.career_common_position
        FROM (SELECT PB2.*, VPCCP2.career_common_position
              FROM PLAYER_BASIC PB2
                       JOIN V_PLAYER_CAREER_COMMON_POSITION VPCCP2 ON PB2.player_id = VPCCP2.player_id) T1,
             (SELECT PB.player_id,
                     PB.date_of_birth AS date_of_birth,
                     PB.height        AS height,
                     PB.weight        AS weight,
                     VPCCP.career_common_position
              FROM PLAYER_BASIC PB
                       JOIN V_PLAYER_CAREER_COMMON_POSITION VPCCP on PB.player_id = VPCCP.player_id
              WHERE PB.player_id = %(player_id)s) KEY_PLAYER
        WHERE ABS(T1.weight - KEY_PLAYER.weight) <= 5
          AND ABS(T1.height - KEY_PLAYER.height) <= 5
          AND T1.career_common_position = KEY_PLAYER.career_common_position
          AND T1.player_id <> KEY_PLAYER.player_id
          AND ABS(YEAR(T1.date_of_birth) - YEAR(KEY_PLAYER.date_of_birth)) <= 5
    """
    candidate_sim_player_id_ls = []
    cursor = None
    try:
        cursor = db_conn.cursor(buffered=True)
        cursor.execute(sql, dict(player_id=player_id))
        common_position = None
        for result in cursor:
            candidate_sim_player_id = result[0]
            common_position = result[1] if common_position is None else common_position
            candidate_sim_player_id_ls.append(candidate_sim_player_id)
    finally:
        if cursor:
            cursor.close()

    return common_position, candidate_sim_player_id_ls


def retrieve_play_style_vectors_of_players_in_common_position(
    db_conn, common_position, player_id_ls
):
    template = ", ".join(["%s"] * len(player_id_ls))
    # sql = """
    #     SELECT player_id,
    #        AVG(PTS),
    #        AVG(FGA),
    #        AVG(3PA),
    #        AVG(2PA),
    #        AVG(FTA),
    #        AVG(ORB),
    #        AVG(DRB),
    #        AVG(AST),
    #        AVG(STL),
    #        AVG(BLK),
    #        AVG(TOV)
    #     FROM PLAYER_PERFORMANCE_STAT_PER_GAME
    #     WHERE player_id IN (%s)
    #       AND position = '%s'
    #     GROUP BY player_id
    # """
    sql = """
        SELECT player_id,
           AVG(FG),
           AVG(FGA),
           AVG(FGP),
           AVG(3P),
           AVG(3PA),
           AVG(3PP),
           AVG(2P),
           AVG(2PA),
           AVG(2PP),
           AVG(eFGP),
           AVG(FT),
           AVG(FTA),
           AVG(FTP),
           AVG(ORB),
           AVG(DRB),
           AVG(TRB),
           AVG(AST),
           AVG(STL),
           AVG(BLK),
           AVG(TOV),
           AVG(PTS)
        FROM PLAYER_PERFORMANCE_STAT_PER_GAME
        WHERE player_id IN (%s)
          AND position = '%s'
        GROUP BY player_id
    """
    # df_indices = []
    # df_dict = defaultdict(list)
    player_id_style_vector_dict = dict()
    sql = sql % (template, common_position)
    cursor = None
    try:
        cursor = db_conn.cursor(buffered=True)
        cursor.execute(sql, tuple(player_id_ls))
        for result in cursor:
            player_id = result[0]
            # df_indices.append(player_id)
            # for i, value in enumerate(result[1:]):
            #     df_dict[str(i)].append(value)
            play_style_vector = np.array(result[1:])
            player_id_style_vector_dict[player_id] = play_style_vector
    finally:
        if cursor:
            cursor.close()

    # data imputation
    df = pd.DataFrame.from_dict(player_id_style_vector_dict, orient="index")
    df.fillna(df.mean(), inplace=True)
    df.fillna(0, inplace=True)
    player_id_style_vector_dict = df.to_dict(orient="index")
    for key in player_id_style_vector_dict:
        player_id_style_vector_dict[key] = np.array(
            list(player_id_style_vector_dict[key].values())
        )

    return player_id_style_vector_dict


def save_processed_result(db_conn, key_player_id, new_similar_score_dict_ls):
    data_sql = """
        INSERT INTO PLAYER_CANDIDATE_SIM_PLAYER_SIM_SCORE(
            player_id, candidate_sim_player_id, common_position, cosine_similarity, max_single_stat_distance
        )
        VALUES (
            %(player_id)s, %(candidate_sim_player_id)s, %(common_position)s, %(cosine_similarity)s,
            %(max_single_stat_distance)s
        )
        ON DUPLICATE KEY UPDATE
            cosine_similarity = VALUES(cosine_similarity),
            max_single_stat_distance = VALUES(max_single_stat_distance)
    """
    status_sql = """
        UPDATE PLAYER_INDEX SET need_find_cand_sim_player = FALSE
        WHERE player_id = %s
    """
    cursor = None
    try:
        cursor = db_conn.cursor(buffered=True)
        if len(new_similar_score_dict_ls) > 0:
            cursor.executemany(data_sql, new_similar_score_dict_ls)
        cursor.execute(status_sql, (key_player_id,))
        db_conn.commit()

        logging.info("Committed to db with similar player info of: %s", key_player_id)
    finally:
        if cursor:
            cursor.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "max_increment_size",
        type=int,
        metavar="max increment size",
        help="the maximum increment size of the data processed by the specified operation",
    )

    args = parser.parse_args()
    args = vars(args)
    max_increment_size = args["max_increment_size"]

    conn = None
    try:
        logging.info("Processing ...")

        conn = get_mysql_conn()
        unprocessed_player_id_ls = load_unprocessed_player_id_ls(
            db_conn=conn, max_increment_size=max_increment_size
        )
        for key_player_id in unprocessed_player_id_ls:
            logging.info("Processing: %s", key_player_id)

            try:
                (
                    common_position,
                    candidate_sim_player_id_ls,
                ) = retrieve_candidate_sim_player_id_ls(
                    db_conn=conn, player_id=key_player_id
                )
                common_position_player_id_ls = [key_player_id]
                common_position_player_id_ls.extend(candidate_sim_player_id_ls)
                player_id_style_vector_dict = (
                    retrieve_play_style_vectors_of_players_in_common_position(
                        db_conn=conn,
                        common_position=common_position,
                        player_id_ls=common_position_player_id_ls,
                    )
                )

                new_similar_score_dict_ls = []
                if len(player_id_style_vector_dict) > 0:
                    key_player_vector = copy.deepcopy(
                        player_id_style_vector_dict[key_player_id]
                    )
                    del player_id_style_vector_dict[key_player_id]
                    for (
                        candidate_sim_player_id,
                        candidate_player_vector,
                    ) in player_id_style_vector_dict.items():
                        # region calculate cosine distance
                        numerator = key_player_vector.dot(candidate_player_vector)
                        denominator = np.linalg.norm(
                            key_player_vector
                        ) * np.linalg.norm(candidate_player_vector)
                        if denominator == 0:
                            cosine_sim = 0
                        else:
                            cosine_sim = numerator / denominator
                        if cosine_sim == np.nan:
                            cosine_sim = np.nan_to_num(cosine_sim)
                        # endregion

                        # region calculate max single stat distance
                        max_single_stat_distance = np.max(
                            np.abs(key_player_vector - candidate_player_vector)
                        )
                        # endregion

                        similar_score_dict = dict(
                            player_id=key_player_id,
                            candidate_sim_player_id=candidate_sim_player_id,
                            common_position=common_position,
                            cosine_similarity=cosine_sim,
                            max_single_stat_distance=max_single_stat_distance,
                        )
                        new_similar_score_dict_ls.append(similar_score_dict)
                        # print(
                        #     "{} - {} (sim: {})".format(
                        #         key_player_id, candidate_sim_player_id, cosine_sim
                        #     )
                        # )
                save_processed_result(
                    db_conn=conn,
                    key_player_id=key_player_id,
                    new_similar_score_dict_ls=new_similar_score_dict_ls,
                )
            except Exception as e:
                msg = "Error occurred when handling: %s" % key_player_id
                logging.error(msg, exc_info=True)
                if conn:
                    conn.rollback()

        logging.info("Done.")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
