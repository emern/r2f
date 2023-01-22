package com.cherniav.r2f;

public class RestaurantInfo {

    // Init class vars
    private String name;
    private int total_ratings;
    private double score;
    private double ref_lat;
    private double ref_long;private String placeid;

    // Class constructor
    public RestaurantInfo(String restaurantName, int numReviews, int reviewRating, double rLatitude, double rLongitude, String placeid){
        this.name = restaurantName;
        this.total_ratings = numReviews;
        this.score = reviewRating;
        this.ref_lat = rLatitude;
        this.ref_long = rLongitude;
        this.placeid = placeid;
    }

    // Functions to retrieve certain info
    public String getRestaurantName(){
        return this.name;
    }

    public int getNumReviews(){
        return this.total_ratings;
    }

    public double getReviewRating(){
        return this.score;
    }

    public double getrLatitude(){
        return this.ref_lat;
    }

    public double getrLongitude(){
        return this.ref_long;
    }

}
