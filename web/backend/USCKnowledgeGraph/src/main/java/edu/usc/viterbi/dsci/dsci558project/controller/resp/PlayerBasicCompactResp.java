package edu.usc.viterbi.dsci.dsci558project.controller.resp;

import edu.usc.viterbi.dsci.dsci558project.domain.PlayerBasicCompact;

import java.util.List;

public class PlayerBasicCompactResp extends BaseResp {

    private long totalNotFiltered;
    private List<PlayerBasicCompact> rows;

    public PlayerBasicCompactResp(long total, String msg, long totalNotFiltered, List<PlayerBasicCompact> rows) {
        super(total, msg);
        this.totalNotFiltered = totalNotFiltered;
        this.rows = rows;
    }

    public long getTotalNotFiltered() {
        return totalNotFiltered;
    }

    public void setTotalNotFiltered(long totalNotFiltered) {
        this.totalNotFiltered = totalNotFiltered;
    }

    public List<PlayerBasicCompact> getRows() {
        return rows;
    }

    public void setRows(List<PlayerBasicCompact> rows) {
        this.rows = rows;
    }

}
