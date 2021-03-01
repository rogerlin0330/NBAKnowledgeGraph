package edu.usc.viterbi.dsci.dsci558project.controller.req;

public class PlayerIdBasedReqParam extends PaginationSortParam {

    private String playerId;

    public String getPlayerId() {
        return playerId;
    }

    public void setPlayerId(String playerId) {
        this.playerId = playerId;
    }

}
