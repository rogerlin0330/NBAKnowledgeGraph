package edu.usc.viterbi.dsci.dsci558project.controller.resp;

import edu.usc.viterbi.dsci.dsci558project.domain.PlayerTeammate;

import java.util.List;

public class PlayerTeammatesResp extends  BaseResp {

    List<PlayerTeammate> rows;

    public PlayerTeammatesResp(long total, String msg, List<PlayerTeammate> rows) {
        super(total, msg);
        this.rows = rows;
    }

    public List<PlayerTeammate> getRows() {
        return rows;
    }

    public void setRows(List<PlayerTeammate> rows) {
        this.rows = rows;
    }

}
