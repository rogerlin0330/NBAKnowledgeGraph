package edu.usc.viterbi.dsci.dsci558project.controller.resp;

import edu.usc.viterbi.dsci.dsci558project.domain.SimilarPlayer;

import java.util.List;

public class SimilarPlayersResp extends BaseResp {

    private List<SimilarPlayer> rows;

    public SimilarPlayersResp(long total, String msg, List<SimilarPlayer> rows) {
        super(total, msg);
        this.rows = rows;
    }

    public List<SimilarPlayer> getRows() {
        return rows;
    }

    public void setRows(List<SimilarPlayer> rows) {
        this.rows = rows;
    }

}
