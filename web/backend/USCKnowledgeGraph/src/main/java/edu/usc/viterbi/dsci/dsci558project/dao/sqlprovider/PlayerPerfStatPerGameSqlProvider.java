package edu.usc.viterbi.dsci.dsci558project.dao.sqlprovider;

import edu.usc.viterbi.dsci.dsci558project.domain.PlayerPerfStatPerGame;
import edu.usc.viterbi.dsci.dsci558project.domain.PlayerPerfStatPerGameExample.Criteria;
import edu.usc.viterbi.dsci.dsci558project.domain.PlayerPerfStatPerGameExample.Criterion;
import edu.usc.viterbi.dsci.dsci558project.domain.PlayerPerfStatPerGameExample;
import java.util.List;
import java.util.Map;
import org.apache.ibatis.jdbc.SQL;

public class PlayerPerfStatPerGameSqlProvider {

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table PLAYER_PERFORMANCE_STAT_PER_GAME
     *
     * @mbg.generated Mon Nov 09 15:22:35 PST 2020
     */
    public String countByExample(PlayerPerfStatPerGameExample example) {
        SQL sql = new SQL();
        sql.SELECT("count(*)").FROM("PLAYER_PERFORMANCE_STAT_PER_GAME");
        applyWhere(sql, example, false);
        return sql.toString();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table PLAYER_PERFORMANCE_STAT_PER_GAME
     *
     * @mbg.generated Mon Nov 09 15:22:35 PST 2020
     */
    public String deleteByExample(PlayerPerfStatPerGameExample example) {
        SQL sql = new SQL();
        sql.DELETE_FROM("PLAYER_PERFORMANCE_STAT_PER_GAME");
        applyWhere(sql, example, false);
        return sql.toString();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table PLAYER_PERFORMANCE_STAT_PER_GAME
     *
     * @mbg.generated Mon Nov 09 15:22:35 PST 2020
     */
    public String insertSelective(PlayerPerfStatPerGame record) {
        SQL sql = new SQL();
        sql.INSERT_INTO("PLAYER_PERFORMANCE_STAT_PER_GAME");

        if (record.getRecordId() != null) {
            sql.VALUES("record_id", "#{recordId,jdbcType=VARCHAR}");
        }

        if (record.getPlayerId() != null) {
            sql.VALUES("player_id", "#{playerId,jdbcType=VARCHAR}");
        }

        if (record.getSeason() != null) {
            sql.VALUES("season", "#{season,jdbcType=VARCHAR}");
        }

        if (record.getAge() != null) {
            sql.VALUES("age", "#{age,jdbcType=TINYINT}");
        }

        if (record.getTeamAbbrvName() != null) {
            sql.VALUES("team_abbrv_name", "#{teamAbbrvName,jdbcType=VARCHAR}");
        }

        if (record.getLeague() != null) {
            sql.VALUES("league", "#{league,jdbcType=VARCHAR}");
        }

        if (record.getPosition() != null) {
            sql.VALUES("position", "#{position,jdbcType=VARCHAR}");
        }

        if (record.getG() != null) {
            sql.VALUES("G", "#{G,jdbcType=SMALLINT}");
        }

        if (record.getGS() != null) {
            sql.VALUES("GS", "#{GS,jdbcType=SMALLINT}");
        }

        if (record.getMP() != null) {
            sql.VALUES("MP", "#{MP,jdbcType=DOUBLE}");
        }

        if (record.getFG() != null) {
            sql.VALUES("FG", "#{FG,jdbcType=DOUBLE}");
        }

        if (record.getFGA() != null) {
            sql.VALUES("FGA", "#{FGA,jdbcType=DOUBLE}");
        }

        if (record.getFGP() != null) {
            sql.VALUES("FGP", "#{FGP,jdbcType=DOUBLE}");
        }

        if (record.get_3P() != null) {
            sql.VALUES("3P", "#{_3P,jdbcType=DOUBLE}");
        }

        if (record.get_3PA() != null) {
            sql.VALUES("3PA", "#{_3PA,jdbcType=DOUBLE}");
        }

        if (record.get_3PP() != null) {
            sql.VALUES("3PP", "#{_3PP,jdbcType=DOUBLE}");
        }

        if (record.get_2P() != null) {
            sql.VALUES("2P", "#{_2P,jdbcType=DOUBLE}");
        }

        if (record.get_2PA() != null) {
            sql.VALUES("2PA", "#{_2PA,jdbcType=DOUBLE}");
        }

        if (record.get_2PP() != null) {
            sql.VALUES("2PP", "#{_2PP,jdbcType=DOUBLE}");
        }

        if (record.geteFGP() != null) {
            sql.VALUES("eFGP", "#{eFGP,jdbcType=DOUBLE}");
        }

        if (record.getFT() != null) {
            sql.VALUES("FT", "#{FT,jdbcType=DOUBLE}");
        }

        if (record.getFTA() != null) {
            sql.VALUES("FTA", "#{FTA,jdbcType=DOUBLE}");
        }

        if (record.getFTP() != null) {
            sql.VALUES("FTP", "#{FTP,jdbcType=DOUBLE}");
        }

        if (record.getORB() != null) {
            sql.VALUES("ORB", "#{ORB,jdbcType=DOUBLE}");
        }

        if (record.getDRB() != null) {
            sql.VALUES("DRB", "#{DRB,jdbcType=DOUBLE}");
        }

        if (record.getTRB() != null) {
            sql.VALUES("TRB", "#{TRB,jdbcType=DOUBLE}");
        }

        if (record.getAST() != null) {
            sql.VALUES("AST", "#{AST,jdbcType=DOUBLE}");
        }

        if (record.getSTL() != null) {
            sql.VALUES("STL", "#{STL,jdbcType=DOUBLE}");
        }

        if (record.getBLK() != null) {
            sql.VALUES("BLK", "#{BLK,jdbcType=DOUBLE}");
        }

        if (record.getTOV() != null) {
            sql.VALUES("TOV", "#{TOV,jdbcType=DOUBLE}");
        }

        if (record.getPF() != null) {
            sql.VALUES("PF", "#{PF,jdbcType=DOUBLE}");
        }

        if (record.getPTS() != null) {
            sql.VALUES("PTS", "#{PTS,jdbcType=DOUBLE}");
        }

        return sql.toString();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table PLAYER_PERFORMANCE_STAT_PER_GAME
     *
     * @mbg.generated Mon Nov 09 15:22:35 PST 2020
     */
    public String selectByExample(PlayerPerfStatPerGameExample example) {
        SQL sql = new SQL();
        if (example != null && example.isDistinct()) {
            sql.SELECT_DISTINCT("record_id");
        } else {
            sql.SELECT("record_id");
        }
        sql.SELECT("player_id");
        sql.SELECT("season");
        sql.SELECT("age");
        sql.SELECT("team_abbrv_name");
        sql.SELECT("league");
        sql.SELECT("position");
        sql.SELECT("G");
        sql.SELECT("GS");
        sql.SELECT("MP");
        sql.SELECT("FG");
        sql.SELECT("FGA");
        sql.SELECT("FGP");
        sql.SELECT("3P");
        sql.SELECT("3PA");
        sql.SELECT("3PP");
        sql.SELECT("2P");
        sql.SELECT("2PA");
        sql.SELECT("2PP");
        sql.SELECT("eFGP");
        sql.SELECT("FT");
        sql.SELECT("FTA");
        sql.SELECT("FTP");
        sql.SELECT("ORB");
        sql.SELECT("DRB");
        sql.SELECT("TRB");
        sql.SELECT("AST");
        sql.SELECT("STL");
        sql.SELECT("BLK");
        sql.SELECT("TOV");
        sql.SELECT("PF");
        sql.SELECT("PTS");
        sql.FROM("PLAYER_PERFORMANCE_STAT_PER_GAME");
        applyWhere(sql, example, false);

        if (example != null && example.getOrderByClause() != null) {
            sql.ORDER_BY(example.getOrderByClause());
        }

        return sql.toString();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table PLAYER_PERFORMANCE_STAT_PER_GAME
     *
     * @mbg.generated Mon Nov 09 15:22:35 PST 2020
     */
    public String updateByExampleSelective(Map<String, Object> parameter) {
        PlayerPerfStatPerGame record = (PlayerPerfStatPerGame) parameter.get("record");
        PlayerPerfStatPerGameExample example = (PlayerPerfStatPerGameExample) parameter.get("example");

        SQL sql = new SQL();
        sql.UPDATE("PLAYER_PERFORMANCE_STAT_PER_GAME");

        if (record.getRecordId() != null) {
            sql.SET("record_id = #{record.recordId,jdbcType=VARCHAR}");
        }

        if (record.getPlayerId() != null) {
            sql.SET("player_id = #{record.playerId,jdbcType=VARCHAR}");
        }

        if (record.getSeason() != null) {
            sql.SET("season = #{record.season,jdbcType=VARCHAR}");
        }

        if (record.getAge() != null) {
            sql.SET("age = #{record.age,jdbcType=TINYINT}");
        }

        if (record.getTeamAbbrvName() != null) {
            sql.SET("team_abbrv_name = #{record.teamAbbrvName,jdbcType=VARCHAR}");
        }

        if (record.getLeague() != null) {
            sql.SET("league = #{record.league,jdbcType=VARCHAR}");
        }

        if (record.getPosition() != null) {
            sql.SET("position = #{record.position,jdbcType=VARCHAR}");
        }

        if (record.getG() != null) {
            sql.SET("G = #{record.G,jdbcType=SMALLINT}");
        }

        if (record.getGS() != null) {
            sql.SET("GS = #{record.GS,jdbcType=SMALLINT}");
        }

        if (record.getMP() != null) {
            sql.SET("MP = #{record.MP,jdbcType=DOUBLE}");
        }

        if (record.getFG() != null) {
            sql.SET("FG = #{record.FG,jdbcType=DOUBLE}");
        }

        if (record.getFGA() != null) {
            sql.SET("FGA = #{record.FGA,jdbcType=DOUBLE}");
        }

        if (record.getFGP() != null) {
            sql.SET("FGP = #{record.FGP,jdbcType=DOUBLE}");
        }

        if (record.get_3P() != null) {
            sql.SET("3P = #{record._3P,jdbcType=DOUBLE}");
        }

        if (record.get_3PA() != null) {
            sql.SET("3PA = #{record._3PA,jdbcType=DOUBLE}");
        }

        if (record.get_3PP() != null) {
            sql.SET("3PP = #{record._3PP,jdbcType=DOUBLE}");
        }

        if (record.get_2P() != null) {
            sql.SET("2P = #{record._2P,jdbcType=DOUBLE}");
        }

        if (record.get_2PA() != null) {
            sql.SET("2PA = #{record._2PA,jdbcType=DOUBLE}");
        }

        if (record.get_2PP() != null) {
            sql.SET("2PP = #{record._2PP,jdbcType=DOUBLE}");
        }

        if (record.geteFGP() != null) {
            sql.SET("eFGP = #{record.eFGP,jdbcType=DOUBLE}");
        }

        if (record.getFT() != null) {
            sql.SET("FT = #{record.FT,jdbcType=DOUBLE}");
        }

        if (record.getFTA() != null) {
            sql.SET("FTA = #{record.FTA,jdbcType=DOUBLE}");
        }

        if (record.getFTP() != null) {
            sql.SET("FTP = #{record.FTP,jdbcType=DOUBLE}");
        }

        if (record.getORB() != null) {
            sql.SET("ORB = #{record.ORB,jdbcType=DOUBLE}");
        }

        if (record.getDRB() != null) {
            sql.SET("DRB = #{record.DRB,jdbcType=DOUBLE}");
        }

        if (record.getTRB() != null) {
            sql.SET("TRB = #{record.TRB,jdbcType=DOUBLE}");
        }

        if (record.getAST() != null) {
            sql.SET("AST = #{record.AST,jdbcType=DOUBLE}");
        }

        if (record.getSTL() != null) {
            sql.SET("STL = #{record.STL,jdbcType=DOUBLE}");
        }

        if (record.getBLK() != null) {
            sql.SET("BLK = #{record.BLK,jdbcType=DOUBLE}");
        }

        if (record.getTOV() != null) {
            sql.SET("TOV = #{record.TOV,jdbcType=DOUBLE}");
        }

        if (record.getPF() != null) {
            sql.SET("PF = #{record.PF,jdbcType=DOUBLE}");
        }

        if (record.getPTS() != null) {
            sql.SET("PTS = #{record.PTS,jdbcType=DOUBLE}");
        }

        applyWhere(sql, example, true);
        return sql.toString();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table PLAYER_PERFORMANCE_STAT_PER_GAME
     *
     * @mbg.generated Mon Nov 09 15:22:35 PST 2020
     */
    public String updateByExample(Map<String, Object> parameter) {
        SQL sql = new SQL();
        sql.UPDATE("PLAYER_PERFORMANCE_STAT_PER_GAME");

        sql.SET("record_id = #{record.recordId,jdbcType=VARCHAR}");
        sql.SET("player_id = #{record.playerId,jdbcType=VARCHAR}");
        sql.SET("season = #{record.season,jdbcType=VARCHAR}");
        sql.SET("age = #{record.age,jdbcType=TINYINT}");
        sql.SET("team_abbrv_name = #{record.teamAbbrvName,jdbcType=VARCHAR}");
        sql.SET("league = #{record.league,jdbcType=VARCHAR}");
        sql.SET("position = #{record.position,jdbcType=VARCHAR}");
        sql.SET("G = #{record.G,jdbcType=SMALLINT}");
        sql.SET("GS = #{record.GS,jdbcType=SMALLINT}");
        sql.SET("MP = #{record.MP,jdbcType=DOUBLE}");
        sql.SET("FG = #{record.FG,jdbcType=DOUBLE}");
        sql.SET("FGA = #{record.FGA,jdbcType=DOUBLE}");
        sql.SET("FGP = #{record.FGP,jdbcType=DOUBLE}");
        sql.SET("3P = #{record._3P,jdbcType=DOUBLE}");
        sql.SET("3PA = #{record._3PA,jdbcType=DOUBLE}");
        sql.SET("3PP = #{record._3PP,jdbcType=DOUBLE}");
        sql.SET("2P = #{record._2P,jdbcType=DOUBLE}");
        sql.SET("2PA = #{record._2PA,jdbcType=DOUBLE}");
        sql.SET("2PP = #{record._2PP,jdbcType=DOUBLE}");
        sql.SET("eFGP = #{record.eFGP,jdbcType=DOUBLE}");
        sql.SET("FT = #{record.FT,jdbcType=DOUBLE}");
        sql.SET("FTA = #{record.FTA,jdbcType=DOUBLE}");
        sql.SET("FTP = #{record.FTP,jdbcType=DOUBLE}");
        sql.SET("ORB = #{record.ORB,jdbcType=DOUBLE}");
        sql.SET("DRB = #{record.DRB,jdbcType=DOUBLE}");
        sql.SET("TRB = #{record.TRB,jdbcType=DOUBLE}");
        sql.SET("AST = #{record.AST,jdbcType=DOUBLE}");
        sql.SET("STL = #{record.STL,jdbcType=DOUBLE}");
        sql.SET("BLK = #{record.BLK,jdbcType=DOUBLE}");
        sql.SET("TOV = #{record.TOV,jdbcType=DOUBLE}");
        sql.SET("PF = #{record.PF,jdbcType=DOUBLE}");
        sql.SET("PTS = #{record.PTS,jdbcType=DOUBLE}");

        PlayerPerfStatPerGameExample example = (PlayerPerfStatPerGameExample) parameter.get("example");
        applyWhere(sql, example, true);
        return sql.toString();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table PLAYER_PERFORMANCE_STAT_PER_GAME
     *
     * @mbg.generated Mon Nov 09 15:22:35 PST 2020
     */
    public String updateByPrimaryKeySelective(PlayerPerfStatPerGame record) {
        SQL sql = new SQL();
        sql.UPDATE("PLAYER_PERFORMANCE_STAT_PER_GAME");

        if (record.getPlayerId() != null) {
            sql.SET("player_id = #{playerId,jdbcType=VARCHAR}");
        }

        if (record.getSeason() != null) {
            sql.SET("season = #{season,jdbcType=VARCHAR}");
        }

        if (record.getAge() != null) {
            sql.SET("age = #{age,jdbcType=TINYINT}");
        }

        if (record.getTeamAbbrvName() != null) {
            sql.SET("team_abbrv_name = #{teamAbbrvName,jdbcType=VARCHAR}");
        }

        if (record.getLeague() != null) {
            sql.SET("league = #{league,jdbcType=VARCHAR}");
        }

        if (record.getPosition() != null) {
            sql.SET("position = #{position,jdbcType=VARCHAR}");
        }

        if (record.getG() != null) {
            sql.SET("G = #{G,jdbcType=SMALLINT}");
        }

        if (record.getGS() != null) {
            sql.SET("GS = #{GS,jdbcType=SMALLINT}");
        }

        if (record.getMP() != null) {
            sql.SET("MP = #{MP,jdbcType=DOUBLE}");
        }

        if (record.getFG() != null) {
            sql.SET("FG = #{FG,jdbcType=DOUBLE}");
        }

        if (record.getFGA() != null) {
            sql.SET("FGA = #{FGA,jdbcType=DOUBLE}");
        }

        if (record.getFGP() != null) {
            sql.SET("FGP = #{FGP,jdbcType=DOUBLE}");
        }

        if (record.get_3P() != null) {
            sql.SET("3P = #{_3P,jdbcType=DOUBLE}");
        }

        if (record.get_3PA() != null) {
            sql.SET("3PA = #{_3PA,jdbcType=DOUBLE}");
        }

        if (record.get_3PP() != null) {
            sql.SET("3PP = #{_3PP,jdbcType=DOUBLE}");
        }

        if (record.get_2P() != null) {
            sql.SET("2P = #{_2P,jdbcType=DOUBLE}");
        }

        if (record.get_2PA() != null) {
            sql.SET("2PA = #{_2PA,jdbcType=DOUBLE}");
        }

        if (record.get_2PP() != null) {
            sql.SET("2PP = #{_2PP,jdbcType=DOUBLE}");
        }

        if (record.geteFGP() != null) {
            sql.SET("eFGP = #{eFGP,jdbcType=DOUBLE}");
        }

        if (record.getFT() != null) {
            sql.SET("FT = #{FT,jdbcType=DOUBLE}");
        }

        if (record.getFTA() != null) {
            sql.SET("FTA = #{FTA,jdbcType=DOUBLE}");
        }

        if (record.getFTP() != null) {
            sql.SET("FTP = #{FTP,jdbcType=DOUBLE}");
        }

        if (record.getORB() != null) {
            sql.SET("ORB = #{ORB,jdbcType=DOUBLE}");
        }

        if (record.getDRB() != null) {
            sql.SET("DRB = #{DRB,jdbcType=DOUBLE}");
        }

        if (record.getTRB() != null) {
            sql.SET("TRB = #{TRB,jdbcType=DOUBLE}");
        }

        if (record.getAST() != null) {
            sql.SET("AST = #{AST,jdbcType=DOUBLE}");
        }

        if (record.getSTL() != null) {
            sql.SET("STL = #{STL,jdbcType=DOUBLE}");
        }

        if (record.getBLK() != null) {
            sql.SET("BLK = #{BLK,jdbcType=DOUBLE}");
        }

        if (record.getTOV() != null) {
            sql.SET("TOV = #{TOV,jdbcType=DOUBLE}");
        }

        if (record.getPF() != null) {
            sql.SET("PF = #{PF,jdbcType=DOUBLE}");
        }

        if (record.getPTS() != null) {
            sql.SET("PTS = #{PTS,jdbcType=DOUBLE}");
        }

        sql.WHERE("record_id = #{recordId,jdbcType=VARCHAR}");

        return sql.toString();
    }

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table PLAYER_PERFORMANCE_STAT_PER_GAME
     *
     * @mbg.generated Mon Nov 09 15:22:35 PST 2020
     */
    protected void applyWhere(SQL sql, PlayerPerfStatPerGameExample example, boolean includeExamplePhrase) {
        if (example == null) {
            return;
        }

        String parmPhrase1;
        String parmPhrase1_th;
        String parmPhrase2;
        String parmPhrase2_th;
        String parmPhrase3;
        String parmPhrase3_th;
        if (includeExamplePhrase) {
            parmPhrase1 = "%s #{example.oredCriteria[%d].allCriteria[%d].value}";
            parmPhrase1_th = "%s #{example.oredCriteria[%d].allCriteria[%d].value,typeHandler=%s}";
            parmPhrase2 = "%s #{example.oredCriteria[%d].allCriteria[%d].value} and #{example.oredCriteria[%d].criteria[%d].secondValue}";
            parmPhrase2_th = "%s #{example.oredCriteria[%d].allCriteria[%d].value,typeHandler=%s} and #{example.oredCriteria[%d].criteria[%d].secondValue,typeHandler=%s}";
            parmPhrase3 = "#{example.oredCriteria[%d].allCriteria[%d].value[%d]}";
            parmPhrase3_th = "#{example.oredCriteria[%d].allCriteria[%d].value[%d],typeHandler=%s}";
        } else {
            parmPhrase1 = "%s #{oredCriteria[%d].allCriteria[%d].value}";
            parmPhrase1_th = "%s #{oredCriteria[%d].allCriteria[%d].value,typeHandler=%s}";
            parmPhrase2 = "%s #{oredCriteria[%d].allCriteria[%d].value} and #{oredCriteria[%d].criteria[%d].secondValue}";
            parmPhrase2_th = "%s #{oredCriteria[%d].allCriteria[%d].value,typeHandler=%s} and #{oredCriteria[%d].criteria[%d].secondValue,typeHandler=%s}";
            parmPhrase3 = "#{oredCriteria[%d].allCriteria[%d].value[%d]}";
            parmPhrase3_th = "#{oredCriteria[%d].allCriteria[%d].value[%d],typeHandler=%s}";
        }

        StringBuilder sb = new StringBuilder();
        List<Criteria> oredCriteria = example.getOredCriteria();
        boolean firstCriteria = true;
        for (int i = 0; i < oredCriteria.size(); i++) {
            Criteria criteria = oredCriteria.get(i);
            if (criteria.isValid()) {
                if (firstCriteria) {
                    firstCriteria = false;
                } else {
                    sb.append(" or ");
                }

                sb.append('(');
                List<Criterion> criterions = criteria.getAllCriteria();
                boolean firstCriterion = true;
                for (int j = 0; j < criterions.size(); j++) {
                    Criterion criterion = criterions.get(j);
                    if (firstCriterion) {
                        firstCriterion = false;
                    } else {
                        sb.append(" and ");
                    }

                    if (criterion.isNoValue()) {
                        sb.append(criterion.getCondition());
                    } else if (criterion.isSingleValue()) {
                        if (criterion.getTypeHandler() == null) {
                            sb.append(String.format(parmPhrase1, criterion.getCondition(), i, j));
                        } else {
                            sb.append(String.format(parmPhrase1_th, criterion.getCondition(), i, j,criterion.getTypeHandler()));
                        }
                    } else if (criterion.isBetweenValue()) {
                        if (criterion.getTypeHandler() == null) {
                            sb.append(String.format(parmPhrase2, criterion.getCondition(), i, j, i, j));
                        } else {
                            sb.append(String.format(parmPhrase2_th, criterion.getCondition(), i, j, criterion.getTypeHandler(), i, j, criterion.getTypeHandler()));
                        }
                    } else if (criterion.isListValue()) {
                        sb.append(criterion.getCondition());
                        sb.append(" (");
                        List<?> listItems = (List<?>) criterion.getValue();
                        boolean comma = false;
                        for (int k = 0; k < listItems.size(); k++) {
                            if (comma) {
                                sb.append(", ");
                            } else {
                                comma = true;
                            }
                            if (criterion.getTypeHandler() == null) {
                                sb.append(String.format(parmPhrase3, i, j, k));
                            } else {
                                sb.append(String.format(parmPhrase3_th, i, j, k, criterion.getTypeHandler()));
                            }
                        }
                        sb.append(')');
                    }
                }
                sb.append(')');
            }
        }

        if (sb.length() > 0) {
            sql.WHERE(sb.toString());
        }
    }
}