package edu.usc.viterbi.dsci.dsci558project.controller.resp;

import edu.usc.viterbi.dsci.dsci558project.domain.PlayerAlumnus;

import java.util.List;

public class PlayerAlumniResp extends BaseResp {

    private List<PlayerAlumnus> rows;

    public PlayerAlumniResp(long total, String msg, List<PlayerAlumnus> rows) {
        super(total, msg);
        this.rows = rows;
    }

    public List<PlayerAlumnus> getRows() {
        return rows;
    }

    public void setRows(List<PlayerAlumnus> rows) {
        this.rows = rows;
    }

}
