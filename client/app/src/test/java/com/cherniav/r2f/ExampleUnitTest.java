package com.cherniav.r2f;

import org.junit.Test;

import com.cherniav.r2f.ui.R2fSocket;

/**
 * Example local unit test, which will execute on the development machine (host).
 *
 * @see <a href="http://d.android.com/tools/testing">Testing documentation</a>
 */
public class ExampleUnitTest {
    @Test
    public void addition_isCorrect() {
        R2fSocket.searchRestaurantsWithName("Lawrence");
        System.out.println(R2fSocket.updateRestaurantByPlaceId("ChIJi9Ix4HlxhlQRR9d6rVYjsFA"));
        R2fSocket.searchNearbyRestaurants(49.23232257745346, -123.07608804311171, 5, 500);
    }
}