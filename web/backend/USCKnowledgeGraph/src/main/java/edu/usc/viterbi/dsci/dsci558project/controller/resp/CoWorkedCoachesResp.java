package edu.usc.viterbi.dsci.dsci558project.controller.resp;

import edu.usc.viterbi.dsci.dsci558project.domain.CoWorkedCoach;

import java.util.List;

public class CoWorkedCoachesResp extends BaseResp {

    List<CoWorkedCoach> rows;

    public CoWorkedCoachesResp(long total, String msg, List<CoWorkedCoach> rows) {
        super(total, msg);
        this.rows = rows;
    }

    public List<CoWorkedCoach> getRows() {
        return rows;
    }

    public void setRows(List<CoWorkedCoach> rows) {
        this.rows = rows;
    }

}
