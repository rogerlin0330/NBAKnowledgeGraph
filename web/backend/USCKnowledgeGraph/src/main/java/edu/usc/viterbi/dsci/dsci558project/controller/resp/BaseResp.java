package edu.usc.viterbi.dsci.dsci558project.controller.resp;

public class BaseResp {

    private long total;
    private String msg;

    public BaseResp(long total, String msg) {
        this.total = total;
        this.msg = msg;
    }

    public long getTotal() {
        return total;
    }

    public void setTotal(long total) {
        this.total = total;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }

}
