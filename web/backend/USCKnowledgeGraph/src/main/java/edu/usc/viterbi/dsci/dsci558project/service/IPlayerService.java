package edu.usc.viterbi.dsci.dsci558project.service;

import edu.usc.viterbi.dsci.dsci558project.controller.req.PlayerAlumniReqParam;
import edu.usc.viterbi.dsci.dsci558project.controller.req.PlayerBasicReqParam;
import edu.usc.viterbi.dsci.dsci558project.controller.req.PlayerIdBasedReqParam;
import edu.usc.viterbi.dsci.dsci558project.controller.resp.*;

import java.io.UnsupportedEncodingException;
import java.text.ParseException;

public interface IPlayerService {

    PlayerBasicCompactResp fetchPlayerBasicCompact(PlayerBasicReqParam reqParam) throws ParseException, UnsupportedEncodingException;

    PlayerNodeResp fetchPlayerBasic(PlayerIdBasedReqParam reqParam) throws UnsupportedEncodingException;

    PlayerPerfStatPerGameResp fetchPlayerPerStatPerGame(PlayerIdBasedReqParam reqParam) throws UnsupportedEncodingException;

    PlayerServedTeamResp fetchPlayerServedTeam(PlayerIdBasedReqParam reqParam) throws UnsupportedEncodingException;

    SimilarPlayersResp fetchSimilarPlayers(PlayerIdBasedReqParam reqParam) throws UnsupportedEncodingException;

    PlayerTeammatesResp fetchPlayerTeammates(PlayerIdBasedReqParam reqParam) throws UnsupportedEncodingException;

    CoWorkedCoachesResp fetchCoWorkedCoaches(PlayerIdBasedReqParam reqParam) throws UnsupportedEncodingException;

    PlayerAlumniResp fetchPlayerAlumni(PlayerAlumniReqParam reqParam) throws UnsupportedEncodingException;

}
