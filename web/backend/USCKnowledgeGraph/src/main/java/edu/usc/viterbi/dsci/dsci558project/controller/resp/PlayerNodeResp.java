package edu.usc.viterbi.dsci.dsci558project.controller.resp;

import edu.usc.viterbi.dsci.dsci558project.domain.PlayerNode;

import java.util.List;

public class PlayerNodeResp extends BaseResp {

    private List<PlayerNode> rows;

    public PlayerNodeResp(long total, String msg, List<PlayerNode> rows) {
        super(total, msg);
        this.rows = rows;
    }

    public List<PlayerNode> getRows() {
        return rows;
    }

    public void setRows(List<PlayerNode> rows) {
        this.rows = rows;
    }

}
