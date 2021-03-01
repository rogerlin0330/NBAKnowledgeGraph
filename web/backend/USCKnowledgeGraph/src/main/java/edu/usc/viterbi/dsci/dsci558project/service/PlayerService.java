package edu.usc.viterbi.dsci.dsci558project.service;

import com.github.pagehelper.PageHelper;
import com.google.common.base.Strings;
import edu.usc.viterbi.dsci.dsci558project.controller.req.PaginationSortParam;
import edu.usc.viterbi.dsci.dsci558project.controller.req.PlayerAlumniReqParam;
import edu.usc.viterbi.dsci.dsci558project.controller.req.PlayerBasicReqParam;
import edu.usc.viterbi.dsci.dsci558project.controller.req.PlayerIdBasedReqParam;
import edu.usc.viterbi.dsci.dsci558project.controller.req.exception.IllegalReqParamException;
import edu.usc.viterbi.dsci.dsci558project.controller.resp.*;
import edu.usc.viterbi.dsci.dsci558project.dao.PlayerBasicDao;
import edu.usc.viterbi.dsci.dsci558project.dao.PlayerPerfStatPerGameDao;
import edu.usc.viterbi.dsci.dsci558project.domain.*;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.neo4j.driver.Driver;
import org.neo4j.driver.Session;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

@Service
public class PlayerService implements IPlayerService {

    private static final int DEFAULT_OFFSET = 0;
    private static final int DEFAULT_LIMIT = 15;

    @Resource
    private PlayerBasicDao playerBasicDao;

    @Resource
    private PlayerPerfStatPerGameDao playerPerfStatPerGameDao;

    @Resource
    private Driver neo4jDao;

    private SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");

    private PlayerBasicExample buildPlayerBasicExample(PlayerBasicReqParam reqParam)
            throws UnsupportedEncodingException, ParseException {
        String playerId = StringUtils.trim(reqParam.getPlayerId());
        String playerName = StringUtils.trim(reqParam.getPlayerName());
        String playerFullName = StringUtils.trim(reqParam.getPlayerFullName());
        String dateOfBirth = StringUtils.trim(reqParam.getDateOfBirth());
        String placeOfBirth = StringUtils.trim(reqParam.getPlaceOfBirth());
        String playerUrl = StringUtils.trim(reqParam.getPlayerUrl());
        Double height = reqParam.getHeight();
        Double weight = reqParam.getWeight();
        String dominantHand = StringUtils.trim(reqParam.getDateOfBirth());
        String college = StringUtils.trim(reqParam.getCollege());
        String highSchool = StringUtils.trim(reqParam.getHighSchool());

        String sort = StringUtils.lowerCase(StringUtils.trim(reqParam.getSort()));
        String order = StringUtils.lowerCase(StringUtils.trim(reqParam.getOrder()));

        PlayerBasicExample example = new PlayerBasicExample();
        PlayerBasicExample.Criteria criteria = example.createCriteria();

        if (!StringUtils.isEmpty(playerId)) {
            playerId = URLDecoder.decode(playerId, "UTF-8");
            criteria.andPlayerIdEqualTo(playerId);
        }
        if (!StringUtils.isEmpty(playerName)) {
            criteria.andPlayerNameEqualTo(playerName);
        }
        if (!StringUtils.isEmpty(playerFullName)) {
            criteria.andPlayerFullNameEqualTo(playerFullName);
        }
        if (!StringUtils.isEmpty(dateOfBirth)) {
            Date dateOfBirthDate = sdf.parse(dateOfBirth);
            criteria.andDateOfBirthEqualTo(dateOfBirthDate);
        }
        if (!StringUtils.isEmpty(placeOfBirth)) {
            criteria.andPlaceOfBirthEqualTo(placeOfBirth);
        }
        if (!StringUtils.isEmpty(playerUrl)) {
            playerUrl = URLDecoder.decode(playerUrl, "UTF-8");
            criteria.andPlayerUrlEqualTo(playerUrl);
        }
        if (height != null) {
            criteria.andHeightEqualTo(height);
        }
        if (weight != null) {
            criteria.andWeightEqualTo(weight);
        }
        if (!StringUtils.isEmpty(dominantHand)) {
            criteria.andDominantHandEqualTo(dominantHand);
        }
        if (!StringUtils.isEmpty(college)) {
            criteria.andCollegeEqualTo(college);
        }
        if (!StringUtils.isEmpty(highSchool)) {
            criteria.andHighSchoolEqualTo(highSchool);
        }

        if (!StringUtils.isEmpty(sort)) {
            if (!order.equals("desc")) {
                order = "asc";
            }
            example.setOrderByClause(String.format("%s %s", sort, order));
        }

        return example;
    }

    private PlayerPerfStatPerGameExample buildPlayerPerfStatPerGameExample(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        String playerId = StringUtils.trim(reqParam.getPlayerId());
        String sort = StringUtils.lowerCase(StringUtils.trim(reqParam.getSort()));
        String order = StringUtils.lowerCase(StringUtils.trim(reqParam.getOrder()));

        PlayerPerfStatPerGameExample example = new PlayerPerfStatPerGameExample();
        PlayerPerfStatPerGameExample.Criteria criteria = example.createCriteria();

        playerId = URLDecoder.decode(playerId, "UTF-8");
        criteria.andPlayerIdEqualTo(playerId);

        if (!StringUtils.isEmpty(sort)) {
            if (!order.equals("desc")) {
                order = "asc";
            }
            example.setOrderByClause(String.format("%s %s", sort, order));
        }

        return example;
    }

    private ImmutablePair<String, Map<String, Object>> handlePaginationSortReqInCypher(
            String query, Map<String, Object> paramMap,
            PaginationSortParam reqParam) {
        String sort = StringUtils.trim(reqParam.getSort());
        String order = StringUtils.trim(reqParam.getOrder());
        Integer limit = reqParam.getLimit();
        Integer offset = reqParam.getOffset();

        if (!StringUtils.isEmpty(sort)) {
            query = String.join(" ",
                    query,
                    "ORDER BY",
                    sort);
            paramMap.put("sort", sort);

            if (!StringUtils.isEmpty(order)) {
                order = order.toLowerCase();
                if (!order.equals("desc")) {
                    order = "asc";
                }
                query = String.join(" ",
                        query,
                        order);
            }
        }

        if (offset != null) {
            query = String.join(" ",
                    query,
                    "SKIP $skip");
            paramMap.put("skip", offset);
        }
        if (limit != null) {
            query = String.join(" ",
                    query,
                    "LIMIT $limit");
            paramMap.put("limit", limit);
        }

        ImmutablePair<String, Map<String, Object>> result = new ImmutablePair<>(query, paramMap);

        return result;
    }

    /**
     * Fetch the compact version of the player basic info
     *
     * @param reqParam
     * @return
     * @throws ParseException
     * @throws UnsupportedEncodingException
     */
    @Override
    public PlayerBasicCompactResp fetchPlayerBasicCompact(PlayerBasicReqParam reqParam)
            throws ParseException, UnsupportedEncodingException {
        PlayerBasicExample example = buildPlayerBasicExample(reqParam);

//        long total = playerBasicDao.countByExample(example);
//        long totalNotFiltered = playerBasicDao.countByExample(new PlayerBasicExample());

        Integer offset = reqParam.getOffset();
        Integer limit = reqParam.getLimit();
        if (offset == null) {
            offset = DEFAULT_OFFSET;
        }
        if (limit == null) {
            limit = DEFAULT_LIMIT;
        }
        PageHelper.offsetPage(offset, limit, false);
        List<PlayerBasicCompact> queryResult = playerBasicDao.selectCompactByExample(example);
        long total = queryResult.size();
        long totalNotFiltered = -1;
        String msg = "success";

        PlayerBasicCompactResp resp = new PlayerBasicCompactResp(total, msg, totalNotFiltered, queryResult);

        return resp;
    }

    /**
     * Fetch the full version of the player basic info
     *
     * @param reqParam
     * @return
     * @throws ParseException
     * @throws UnsupportedEncodingException
     */
    @Override
    public PlayerNodeResp fetchPlayerBasic(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        String queryPlayerId = StringUtils.trim(reqParam.getPlayerId());
        queryPlayerId = Strings.nullToEmpty(queryPlayerId);
        queryPlayerId = URLDecoder.decode(queryPlayerId, "UTF-8");

        if (StringUtils.isEmpty(queryPlayerId)) {
            PlayerNodeResp resp = new PlayerNodeResp(
                    0, "The playerId parameter must be provided.", Collections.emptyList());

            return resp;
        }

        String query = String.join(" ",
                "MATCH (p:Player { player_id: $player_id })",
                "RETURN DISTINCT p.player_id AS playerId,",
                "p.wikidata_id AS wikidataId,",
                "p.player_url AS playerUrl,",
                "p.player_espn_url AS playerEspnUrl,",
                "p.name AS playerName,",
                "p.full_name AS playerFullName,",
                "p.date_of_birth AS dateOfBirth,",
                "p.place_of_birth AS placeOfBirth,",
                "p.height AS height,",
                "p.weight AS weight,",
                "p.college AS college,",
                "p.high_school AS highSchool,",
                "p.dominant_hand AS dominantHand"
        );
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("player_id", queryPlayerId);

        ImmutablePair<String, Map<String, Object>> result = handlePaginationSortReqInCypher(
                query, paramMap, reqParam);
        query = result.getLeft();
        paramMap = result.getRight();

        try (Session session = neo4jDao.session()) {
            List<PlayerNode> queryResult = session
                    .run(query, paramMap)
                    .list(record -> {
                        String playerId = record.get("playerId").asString(null);
                        String wikidataId = record.get("wikidataId").asString(null);
                        String playerUrl = record.get("playerUrl").asString(null);
                        String playerEspnUrl = record.get("playerEspnUrl").asString(null);
                        String playerName = record.get("playerName").asString(null);
                        String playerFullName = record.get("playerFullName").asString(null);
                        String dateOfBirth = record.get("dateOfBirth").asString(null);
                        Date dateOfBirthDate = null;
                        try {
                            if (!StringUtils.isEmpty(dateOfBirth)) {
                                dateOfBirthDate = sdf.parse(dateOfBirth);
                            }
                        } catch (ParseException e) {
                            e.printStackTrace();
                        }
                        String placeOfBirth = record.get("placeOfBirth").asString(null);
                        Double height = null;
                        if (!record.get("height").isNull()) {
                            height = record.get("height").asDouble();
                        }
                        Double weight = null;
                        if (!record.get("weight").isNull()) {
                            weight = record.get("weight").asDouble();
                        }
                        String college = record.get("college").asString(null);
                        String highSchool = record.get("highSchool").asString(null);
                        String dominantHand = record.get("dominantHand").asString(null);

                        PlayerNode playerNode = new PlayerNode();
                        playerNode.setPlayerId(playerId);
                        playerNode.setWikidataId(wikidataId);
                        playerNode.setPlayerUrl(playerUrl);
                        playerNode.setPlayerEspnUrl(playerEspnUrl);
                        playerNode.setPlayerName(playerName);
                        playerNode.setPlayerFullName(playerFullName);
                        playerNode.setDateOfBirth(dateOfBirthDate);
                        playerNode.setPlaceOfBirth(placeOfBirth);
                        playerNode.setHeight(height);
                        playerNode.setWeight(weight);
                        playerNode.setCollege(college);
                        playerNode.setHighSchool(highSchool);
                        playerNode.setDominantHand(dominantHand);

                        return playerNode;
                    });
            long total = queryResult.size();
            String msg = "success";

            PlayerNodeResp resp = new PlayerNodeResp(total, msg, queryResult);

            return resp;
        }
    }

    /**
     * Fetch the player's performance stat per game
     *
     * @param reqParam
     * @return
     * @throws UnsupportedEncodingException
     * @throws IllegalReqParamException
     */
    @Override
    public PlayerPerfStatPerGameResp fetchPlayerPerStatPerGame(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        String playerId = StringUtils.trim(reqParam.getPlayerId());
        if (StringUtils.isEmpty(playerId)) {
            PlayerPerfStatPerGameResp resp = new PlayerPerfStatPerGameResp(
                    0, "The playerId parameter must be provided.", Collections.emptyList());

            return resp;
        }

        PlayerPerfStatPerGameExample example = buildPlayerPerfStatPerGameExample(reqParam);

        Integer offset = reqParam.getOffset();
        Integer limit = reqParam.getLimit();
        if (offset == null) {
            offset = DEFAULT_OFFSET;
        }
        if (limit == null) {
            limit = DEFAULT_LIMIT;
        }
        PageHelper.offsetPage(offset, limit, false);
        List<PlayerPerfStatPerGame> queryResult = playerPerfStatPerGameDao.selectByExample(example);
        long total = queryResult.size();
        String msg = "success";

        PlayerPerfStatPerGameResp resp = new PlayerPerfStatPerGameResp(total, msg, queryResult);

        return resp;
    }

    /**
     * Fetch the team information that the player has served.
     *
     * @param reqParam
     * @return
     * @throws UnsupportedEncodingException
     */
    public PlayerServedTeamResp fetchPlayerServedTeam(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        String queryPlayerId = StringUtils.trim(reqParam.getPlayerId());
        queryPlayerId = Strings.nullToEmpty(queryPlayerId);
        queryPlayerId = URLDecoder.decode(queryPlayerId, "UTF-8");

        if (StringUtils.isEmpty(queryPlayerId)) {
            PlayerServedTeamResp resp = new PlayerServedTeamResp(
                    0, "The playerId parameter must be provided.", Collections.emptyList());

            return resp;
        }

        String query = String.join(" ",
            "MATCH (p:Player { player_id: $player_id })-[r:served]->(t:Team)",
            "RETURN DISTINCT p.player_id AS playerId,",
            "p.name AS playerName,",
            "t.team_name AS teamName,",
            "t.team_abbrv_name AS teamAbbrvName,",
            "r.season AS season"
        );
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("player_id", queryPlayerId);

        ImmutablePair<String, Map<String, Object>> result = handlePaginationSortReqInCypher(
                query, paramMap, reqParam);
        query = result.getLeft();
        paramMap = result.getRight();

        try (Session session = neo4jDao.session()) {
            List<PlayerServedTeam> queryResult = session
                    .run(query, paramMap)
                    .list(record -> {
                        String playerId = record.get("playerId").asString(null);
                        String playerName = record.get("playerName").asString(null);
                        String teamName = record.get("teamName").asString(null);
                        String teamAbbrvName = record.get("teamAbbrvName").asString(null);
                        String season = record.get("season").asString(null);

                        PlayerServedTeam playerServedTeam = new PlayerServedTeam(
                                playerId, playerName, teamName, teamAbbrvName, season
                        );
                        return playerServedTeam;
                    });
            long total = queryResult.size();
            String msg = "success";

            PlayerServedTeamResp resp = new PlayerServedTeamResp(total, msg, queryResult);

            return resp;
        }
    }

    /**
     * Fetch players that have similar playing pattern to the player
     *
     * @param reqParam
     * @return
     * @throws UnsupportedEncodingException
     */
    @Override
    public SimilarPlayersResp fetchSimilarPlayers(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        String queryPlayerId = StringUtils.trim(reqParam.getPlayerId());
        queryPlayerId = Strings.nullToEmpty(queryPlayerId);
        queryPlayerId = URLDecoder.decode(queryPlayerId, "UTF-8");

        if (StringUtils.isEmpty(queryPlayerId)) {
            SimilarPlayersResp resp = new SimilarPlayersResp(
                    0, "The playerId parameter must be provided.", Collections.emptyList());

            return resp;
        }

        String query = String.join(" ",
                "MATCH (p:Player { player_id: $player_id })-[r:has_similar_playing_pattern]-(sp:Player)",
                "RETURN sp.player_id AS playerId,",
                "sp.name AS playerName,",
                "sp.date_of_birth AS dateOfBirth,",
                "sp.place_of_birth AS placeOfBirth,",
                "r.cosine_similarity AS similarity,",
                "r.max_single_stat_distance AS maxSingleStatDistance"
        );
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("player_id", queryPlayerId);

        if (StringUtils.isEmpty(reqParam.getSort())) {
            reqParam.setSort("similarity");
            reqParam.setOrder("desc");
        }

        ImmutablePair<String, Map<String, Object>> result = handlePaginationSortReqInCypher(
                query, paramMap, reqParam);
        query = result.getLeft();
        paramMap = result.getRight();

        try (Session session = neo4jDao.session()) {
            List<SimilarPlayer> queryResult = session
                    .run(query, paramMap)
                    .list(record -> {
                        String playerId = record.get("playerId").asString(null);
                        String playerName = record.get("playerName").asString(null);
                        String dateOfBirth = record.get("dateOfBirth").asString(null);
                        String placeOfBirth = record.get("placeOfBirth").asString(null);
                        Double similarity = null;
                        if (!record.get("similarity").isNull()) {
                            similarity = record.get("similarity").asDouble();
                        }
                        Double maxSingleStatDistance = null;
                        if (!record.get("maxSingleStatDistance").isNull()) {
                            maxSingleStatDistance = record.get("maxSingleStatDistance").asDouble();
                        }

                        SimilarPlayer similarPlayer = new SimilarPlayer(playerId, playerName,
                                dateOfBirth, placeOfBirth, similarity, maxSingleStatDistance);

                        return similarPlayer;
                    });
            long total = queryResult.size();
            String msg = "success";

            SimilarPlayersResp resp = new SimilarPlayersResp(total, msg, queryResult);

            return resp;
        }
    }

    /**
     * Fetch players who have been the teammate of the player
     *
     * @param reqParam
     * @return
     * @throws UnsupportedEncodingException
     */
    @Override
    public PlayerTeammatesResp fetchPlayerTeammates(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        String queryPlayerId = StringUtils.trim(reqParam.getPlayerId());
        queryPlayerId = Strings.nullToEmpty(queryPlayerId);
        queryPlayerId = URLDecoder.decode(queryPlayerId, "UTF-8");

        if (StringUtils.isEmpty(queryPlayerId)) {
            PlayerTeammatesResp resp = new PlayerTeammatesResp(
                    0, "The playerId parameter must be provided.", Collections.emptyList());

            return resp;
        }

        String query = String.join(" ",
                "MATCH (p1:Player { player_id: $player_id })-[r1:served]->(t:Team)<-[r2:served]-(p2:Player)",
                "WHERE p1.player_id <> p2.player_id AND r1.season = r2.season",
                "RETURN DISTINCT p2.player_id as playerId, p2.name AS playerName,",
                "p2.date_of_birth AS dateOfBirth, p2.place_of_birth as placeOfBirth,",
                "r1.season AS season, t.team_name AS atTeam"
        );
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("player_id", queryPlayerId);

        if (StringUtils.isEmpty(reqParam.getSort())) {
            reqParam.setSort("season");
            reqParam.setOrder("desc");
        }

        ImmutablePair<String, Map<String, Object>> result = handlePaginationSortReqInCypher(
                query, paramMap, reqParam);
        query = result.getLeft();
        paramMap = result.getRight();

        try (Session session = neo4jDao.session()) {
            List<PlayerTeammate> queryResult = session
                    .run(query, paramMap)
                    .list(record -> {
                        String playerId = record.get("playerId").asString(null);
                        String playerName = record.get("playerName").asString(null);
                        String dateOfBirth = record.get("dateOfBirth").asString(null);
                        String placeOfBirth = record.get("placeOfBirth").asString(null);
                        String season = record.get("season").asString(null);
                        String atTeam = record.get("atTeam").asString(null);

                        PlayerTeammate teammate = new PlayerTeammate(playerId, playerName,
                                dateOfBirth, placeOfBirth, season, atTeam);

                        return teammate;
                    });
            long total = queryResult.size();
            String msg = "success";

            PlayerTeammatesResp resp = new PlayerTeammatesResp(total, msg, queryResult);

            return resp;
        }
    }

    /**
     * Fetch coaches who have been co-worked with the player in the same team
     *
     * @param reqParam
     * @return
     * @throws UnsupportedEncodingException
     */
    @Override
    public CoWorkedCoachesResp fetchCoWorkedCoaches(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        String queryPlayerId = StringUtils.trim(reqParam.getPlayerId());
        queryPlayerId = Strings.nullToEmpty(queryPlayerId);
        queryPlayerId = URLDecoder.decode(queryPlayerId, "UTF-8");

        if (StringUtils.isEmpty(queryPlayerId)) {
            CoWorkedCoachesResp resp = new CoWorkedCoachesResp(
                    0, "The playerId parameter must be provided.", Collections.emptyList());

            return resp;
        }

        String query = String.join(" ",
                "MATCH (p:Player { player_id: $player_id })-[r1:served]->(t:Team)<-[r2:served]-(c:Coach)",
                "WHERE r1.season = r2.season",
                "RETURN c.coach_id AS coachId, c.name AS coachName,",
                "r2.coach_job_title AS coachTitle, r2.season AS season, t.team_name AS atTeam"
        );
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("player_id", queryPlayerId);

        if (StringUtils.isEmpty(reqParam.getSort())) {
            reqParam.setSort("season");
            reqParam.setOrder("desc");
        }

        ImmutablePair<String, Map<String, Object>> result = handlePaginationSortReqInCypher(
                query, paramMap, reqParam);
        query = result.getLeft();
        paramMap = result.getRight();

        try (Session session = neo4jDao.session()) {
            List<CoWorkedCoach> queryResult = session
                    .run(query, paramMap)
                    .list(record -> {
                        String coachId = record.get("coachId").asString(null);
                        String coachName = record.get("coachName").asString(null);
                        String coachTitle = record.get("coachTitle").asString(null);
                        String season = record.get("season").asString(null);
                        String atTeam = record.get("atTeam").asString(null);

                        CoWorkedCoach coWorkedCoach = new CoWorkedCoach(coachId, coachName,
                                coachTitle, season, atTeam);

                        return coWorkedCoach;
                    });
            long total = queryResult.size();
            String msg = "success";

            CoWorkedCoachesResp resp = new CoWorkedCoachesResp(total, msg, queryResult);

            return resp;
        }
    }

    /**
     * Fetch alumni of the player
     *
     * @param reqParam
     * @return
     * @throws UnsupportedEncodingException
     */
    @Override
    public PlayerAlumniResp fetchPlayerAlumni(PlayerAlumniReqParam reqParam)
            throws UnsupportedEncodingException {
        String queryPlayerId = StringUtils.trim(reqParam.getPlayerId());
        queryPlayerId = Strings.nullToEmpty(queryPlayerId);
        queryPlayerId = URLDecoder.decode(queryPlayerId, "UTF-8");

        if (StringUtils.isEmpty(queryPlayerId)) {
            PlayerAlumniResp resp = new PlayerAlumniResp(
                    0, "The playerId parameter must be provided.", Collections.emptyList());

            return resp;
        }

        String alumniType = StringUtils.trim(reqParam.getAlumniType());
        if (StringUtils.isEmpty(alumniType)) {
            PlayerAlumniResp resp = new PlayerAlumniResp(
                    0, "The alumniType parameter must be provided.", Collections.emptyList());

            return resp;
        } else if (!alumniType.equals("HighSchool") && !alumniType.equals("College")) {
            PlayerAlumniResp resp = new PlayerAlumniResp(
                    0, "The alumniType parameter should either be \"HighSchool\" or \"College\".",
                    Collections.emptyList());

            return resp;
        }

        String query = String.join(" ",
            "MATCH (p1:Player { player_id: $player_id })-[:attended]->(:" + alumniType + ")<-[:attended]-(p2:Player)",
            "WHERE p1.player_id <> p2.player_id",
            "WITH p1, p2, duration.inDays(date(p1.date_of_birth), date(p2.date_of_birth)).days AS ageDiff",
            "RETURN p2.player_id AS playerId, p2.name AS playerName,",
            "p2.date_of_birth AS dateOfBirth, p2.place_of_birth AS placeOfBirth"
        );
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("player_id", queryPlayerId);

        if (StringUtils.isEmpty(reqParam.getSort())) {
            reqParam.setSort("ageDiff");
            reqParam.setOrder("asc");
        }

        ImmutablePair<String, Map<String, Object>> result = handlePaginationSortReqInCypher(
                query, paramMap, reqParam);
        query = result.getLeft();
        paramMap = result.getRight();

        try (Session session = neo4jDao.session()) {
            List<PlayerAlumnus> queryResult = session
                    .run(query, paramMap)
                    .list(record -> {
                        String playerId = record.get("playerId").asString(null);
                        String playerName = record.get("playerName").asString(null);
                        String dateOfBirth = record.get("dateOfBirth").asString(null);
                        String placeOfBirth = record.get("placeOfBirth").asString(null);

                        PlayerAlumnus playerAlumnus = new PlayerAlumnus(playerId, playerName,
                                dateOfBirth, placeOfBirth);

                        return playerAlumnus;
                    });
            long total = queryResult.size();
            String msg = "success";

            PlayerAlumniResp resp = new PlayerAlumniResp(total, msg, queryResult);

            return resp;
        }
    }

}
