package edu.usc.viterbi.dsci.dsci558project.domain;

public class PlayerAlumnus {

    private String playerId;
    private String playerName;
    private String dateOfBirth;
    private String placeOfBirth;

    public PlayerAlumnus() {
    }

    public PlayerAlumnus(String playerId, String playerName, String dateOfBirth, String placeOfBirth) {
        this.playerId = playerId;
        this.playerName = playerName;
        this.dateOfBirth = dateOfBirth;
        this.placeOfBirth = placeOfBirth;
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

}
