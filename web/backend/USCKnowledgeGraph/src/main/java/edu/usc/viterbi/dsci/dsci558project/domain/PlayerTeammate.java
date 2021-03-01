package edu.usc.viterbi.dsci.dsci558project.domain;

public class PlayerTeammate {

    private String playerId;
    private String playerName;
    private String dateOfBirth;
    private String placeOfBirth;
    private String season;
    private String atTeam;

    public PlayerTeammate() {
    }

    public PlayerTeammate(String playerId, String playerName,
                          String dateOfBirth, String placeOfBirth, String season, String atTeam) {
        this.playerId = playerId;
        this.playerName = playerName;
        this.dateOfBirth = dateOfBirth;
        this.placeOfBirth = placeOfBirth;
        this.season = season;
        this.atTeam = atTeam;
    }

    public String getPlayerId() {
        return playerId;
    }

    public void setPlayerId(String playerId) {
        this.playerId = playerId;
    }

    public String getPlayerName() {
        return playerName;
    }

    public void setPlayerName(String playerName) {
        this.playerName = playerName;
    }

    public String getDateOfBirth() {
        return dateOfBirth;
    }

    public void setDateOfBirth(String dateOfBirth) {
        this.dateOfBirth = dateOfBirth;
    }

    public String getPlaceOfBirth() {
        return placeOfBirth;
    }

    public void setPlaceOfBirth(String placeOfBirth) {
        this.placeOfBirth = placeOfBirth;
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
