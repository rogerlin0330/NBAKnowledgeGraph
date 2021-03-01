INSERT INTO BASKETBALL_REFERENCE_WIKIDATA_ENTITY_LINK
SELECT player_id, GROUP_CONCAT(wikidata_id) AS wikidata_id
FROM PLAYER_BASIC T1
         JOIN
     (SELECT PB.player_name, GROUP_CONCAT(DISTINCT PBW.wikidata_id) AS wikidata_id
      FROM PLAYER_BASIC PB
               JOIN PLAYER_BASIC_WIKIDATA PBW
                    on PB.player_name = PBW.player_name AND PB.date_of_birth = PBW.date_of_birth
      GROUP BY PB.player_name
      HAVING COUNT(DISTINCT PBW.wikidata_id) = 1) T2 ON T1.player_name = T2.player_name
GROUP BY player_id
HAVING COUNT(wikidata_id) = 1
ON DUPLICATE KEY UPDATE wikidata_id = VALUES(wikidata_id);
