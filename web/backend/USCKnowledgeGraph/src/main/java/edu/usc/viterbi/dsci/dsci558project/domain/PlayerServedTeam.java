package edu.usc.viterbi.dsci.dsci558project.domain;

public class PlayerServedTeam {

    private String playerId;
    private String playerName;
    private String teamName;
    private String teamAbbrvName;
    private String season;

    public PlayerServedTeam() {
    }

    public PlayerServedTeam(
            String playerId, String playerName, String teamName, String teamAbbrvName, String season
    ) {
        this.playerId = playerId;
        this.playerName = playerName;
        this.teamName = teamName;
        this.teamAbbrvName = teamAbbrvName;
        this.season = season;
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

    public String getTeamName() {
        return teamName;
    }

    public void setTeamName(String teamName) {
        this.teamName = teamName;
    }

    public String getTeamAbbrvName() {
        return teamAbbrvName;
    }

    public void setTeamAbbrvName(String teamAbbrvName) {
        this.teamAbbrvName = teamAbbrvName;
    }

    public String getSeason() {
        return season;
    }

    public void setSeason(String season) {
        this.season = season;
    }

}
