package edu.usc.viterbi.dsci.dsci558project.controller.resp;

import edu.usc.viterbi.dsci.dsci558project.domain.PlayerServedTeam;

import java.util.List;

public class PlayerServedTeamResp extends BaseResp {

    private List<PlayerServedTeam> rows;

    public PlayerServedTeamResp(long total, String msg, List<PlayerServedTeam> rows) {
        super(total, msg);
        this.rows = rows;
    }

    public List<PlayerServedTeam> getRows() {
        return rows;
    }

    public void setRows(List<PlayerServedTeam> rows) {
        this.rows = rows;
    }

}
