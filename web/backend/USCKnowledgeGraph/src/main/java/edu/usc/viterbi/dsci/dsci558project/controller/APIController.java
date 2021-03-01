package edu.usc.viterbi.dsci.dsci558project.controller;

import edu.usc.viterbi.dsci.dsci558project.controller.req.PlayerAlumniReqParam;
import edu.usc.viterbi.dsci.dsci558project.controller.req.PlayerBasicReqParam;
import edu.usc.viterbi.dsci.dsci558project.controller.req.PlayerIdBasedReqParam;
import edu.usc.viterbi.dsci.dsci558project.controller.req.exception.IllegalReqParamException;
import edu.usc.viterbi.dsci.dsci558project.controller.resp.*;
import edu.usc.viterbi.dsci.dsci558project.service.IPlayerService;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import java.io.UnsupportedEncodingException;
import java.text.ParseException;

@RestController
public class APIController {

    @Resource
    private IPlayerService playerService;

    @RequestMapping(value = "/nba/api/fetchPlayerBasicCompact")
    public PlayerBasicCompactResp fetchPlayerBasicCompact(PlayerBasicReqParam reqParam)
            throws ParseException, UnsupportedEncodingException {
        PlayerBasicCompactResp resp = playerService.fetchPlayerBasicCompact(reqParam);
        return resp;
    }

    @RequestMapping(value = "/nba/api/fetchPlayerBasic")
    public PlayerNodeResp fetchPlayerBasic(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        PlayerNodeResp resp = playerService.fetchPlayerBasic(reqParam);
        return resp;
    }

    @RequestMapping(value = "/nba/api/fetchPlayerPerfStatPerGame")
    public PlayerPerfStatPerGameResp fetchPlayerPerfStatPerGame(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        PlayerPerfStatPerGameResp resp = playerService.fetchPlayerPerStatPerGame(reqParam);
        return resp;
    }

    @RequestMapping(value = "/nba/api/fetchPlayerServedTeam")
    public PlayerServedTeamResp fetchPlayerServedTeam(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        PlayerServedTeamResp resp = playerService.fetchPlayerServedTeam(reqParam);
        return resp;
    }

    @RequestMapping(value = "/nba/api/fetchSimilarPlayers")
    public SimilarPlayersResp fetchSimilarPlayers(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        SimilarPlayersResp resp = playerService.fetchSimilarPlayers(reqParam);
        return resp;
    }

    @RequestMapping(value = "/nba/api/fetchPlayerTeammates")
    public PlayerTeammatesResp fetchPlayerTeammates(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        PlayerTeammatesResp resp = playerService.fetchPlayerTeammates(reqParam);
        return resp;
    }

    @RequestMapping(value = "/nba/api/fetchCoWorkedCoaches")
    public CoWorkedCoachesResp fetchCoWorkedCoaches(PlayerIdBasedReqParam reqParam)
            throws UnsupportedEncodingException {
        CoWorkedCoachesResp resp = playerService.fetchCoWorkedCoaches(reqParam);
        return resp;
    }

    @RequestMapping(value = "/nba/api/fetchPlayerAlumni")
    public PlayerAlumniResp fetchPlayerAlumni(PlayerAlumniReqParam reqParam)
            throws UnsupportedEncodingException {
        PlayerAlumniResp resp = playerService.fetchPlayerAlumni(reqParam);
        return resp;
    }

}
