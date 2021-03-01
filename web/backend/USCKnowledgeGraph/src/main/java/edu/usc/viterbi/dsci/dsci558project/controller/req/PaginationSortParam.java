package edu.usc.viterbi.dsci.dsci558project.controller.req;

public class PaginationSortParam {

    // pagination params
    private Integer offset;
    private Integer limit;

    // sorting params
    private String sort;
    private String order;

    public Integer getOffset() {
        return offset;
    }

    public void setOffset(Integer offset) {
        this.offset = offset;
    }

    public Integer getLimit() {
        return limit;
    }

    public void setLimit(Integer limit) {
        this.limit = limit;
    }

    public String getSort() {
        return sort;
    }

    public void setSort(String sort) {
        this.sort = sort;
    }

    public String getOrder() {
        return order;
    }

    public void setOrder(String order) {
        this.order = order;
    }

}
