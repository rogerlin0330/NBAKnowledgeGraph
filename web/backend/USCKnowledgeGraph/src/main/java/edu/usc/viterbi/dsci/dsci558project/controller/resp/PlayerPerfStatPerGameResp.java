package edu.usc.viterbi.dsci.dsci558project.controller.resp;

import edu.usc.viterbi.dsci.dsci558project.domain.PlayerPerfStatPerGame;

import java.util.List;

public class PlayerPerfStatPerGameResp extends BaseResp {

    private List<PlayerPerfStatPerGame> rows;

    public PlayerPerfStatPerGameResp(long total, String msg, List<PlayerPerfStatPerGame> rows) {
        super(total, msg);
        this.rows = rows;
    }

    public List<PlayerPerfStatPerGame> getRows() {
        return rows;
    }

    public void setRows(List<PlayerPerfStatPerGame> rows) {
        this.rows = rows;
    }

}
