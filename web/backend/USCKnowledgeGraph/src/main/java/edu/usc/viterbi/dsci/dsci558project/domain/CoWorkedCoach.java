package edu.usc.viterbi.dsci.dsci558project.domain;

public class CoWorkedCoach {

    private String coachId;
    private String coachName;
    private String coachTitle;
    private String season;
    private String atTeam;

    public CoWorkedCoach() {
    }

    public CoWorkedCoach(String coachId, String coachName, String coachTitle, String season, String atTeam) {
        this.coachId = coachId;
        this.coachName = coachName;
        this.coachTitle = coachTitle;
        this.season = season;
        this.atTeam = atTeam;
    }

    public String getCoachId() {
        return coachId;
    }

    public void setCoachId(String coachId) {
        this.coachId = coachId;
    }

    public String getCoachName() {
        return coachName;
    }

    public void setCoachName(String coachName) {
        this.coachName = coachName;
    }

    public String getCoachTitle() {
        return coachTitle;
    }

    public void setCoachTitle(String coachTitle) {
        this.coachTitle = coachTitle;
    }

    public String getSeason() {
        return season;
    }

    public void setSeason(String season) {
        this.season = season;
    }

    public String getAtTeam() {
        return atTeam;
    }

    public void setAtTeam(String atTeam) {
        this.atTeam = atTeam;
    }

}
