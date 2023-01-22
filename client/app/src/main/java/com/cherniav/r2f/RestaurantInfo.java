package com.cherniav.r2f;

public class RestaurantInfo {

    // Init class vars
    private String restaurantName;
    private int numReviews;
    private int reviewRating;
    private double rLatitude;
    private double rLongitude;

    // Class constructor
    public RestaurantInfo(String restaurantName, int numReviews, int reviewRating, double rLatitude, double rLongitude){
        this.restaurantName = restaurantName;
        this.numReviews = numReviews;
        this.reviewRating = reviewRating;
        this.rLatitude = rLatitude;
        this.rLongitude = rLongitude;
    }

    // Functions to retrieve certain info
    public String getRestaurantName(){
        return this.restaurantName;
    }

    public int getNumReviews(){
        return this.numReviews;
    }

    public int getReviewRating(){
        return this.reviewRating;
    }

    public double getrLatitude(){
        return this.rLatitude;
    }

    public double getrLongitude(){
        return this.rLongitude;
    }

}
