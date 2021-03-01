package edu.usc.viterbi.dsci.dsci558project.domain;

public class SimilarPlayer {

    private String playerId;
    private String playerName;
    private String dateOfBirth;
    private String placeOfBirth;
    private Double similarity;
    private Double maxSingleStatDistance;

    public SimilarPlayer() {
    }

    public SimilarPlayer(String playerId, String playerName, String dateOfBirth,
                         String placeOfBirth, Double similarity, Double maxSingleStatDistance) {
        this.playerId = playerId;
        this.playerName = playerName;
        this.dateOfBirth = dateOfBirth;
        this.placeOfBirth = placeOfBirth;
        this.similarity = similarity;
        this.maxSingleStatDistance = maxSingleStatDistance;
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

    public Double getSimilarity() {
        return similarity;
    }

    public void setSimilarity(Double similarity) {
        this.similarity = similarity;
    }

    public Double getMaxSingleStatDistance() {
        return maxSingleStatDistance;
    }

    public void setMaxSingleStatDistance(Double maxSingleStatDistance) {
        this.maxSingleStatDistance = maxSingleStatDistance;
    }

}
