package com.cherniav.r2f.ui;

import com.cherniav.r2f.RestaurantInfo;
import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;

public class R2fSocket {

    private static String RESP_OK = "OK";

    public static ArrayList<RestaurantInfo> searchRestaurantsWithName(String name) {
        JsonObject jsonObject = new JsonObject();
        jsonObject.addProperty("cmd", 0);
        jsonObject.addProperty("name", name);
        ResponseGetter getter = new ResponseGetter(jsonObject.toString());
        getter.start();
        try {
            getter.join();
        }
        catch(InterruptedException e) {
           return new ArrayList<>();
        }
        String reponse_data = getter.response;
        Gson gson = new Gson();
        GsonRestaurantDecoder decoder =  gson.fromJson(reponse_data, GsonRestaurantDecoder.class);
        if (decoder.response.equals(RESP_OK)) {
            return decoder.restaurants;
        } else {
            return new ArrayList<>();
        }
    }

    public static ArrayList<RestaurantInfo> searchNearbyRestaurants(double latitde, double longitude, int num_search, int radius) {
        JsonObject jsonObject = new JsonObject();
        jsonObject.addProperty("cmd", 2);
        jsonObject.addProperty("lat", latitde);
        jsonObject.addProperty("long", longitude);
        jsonObject.addProperty("num", num_search);
        jsonObject.addProperty("radius", radius);
        ResponseGetter getter = new ResponseGetter(jsonObject.toString());
        getter.start();
        try {
            getter.join();
        }
        catch(InterruptedException e) {
            return new ArrayList<>();
        }
        String reponse_data = getter.response;
        Gson gson = new Gson();
        GsonRestaurantDecoder decoder =  gson.fromJson(reponse_data, GsonRestaurantDecoder.class);
        if (decoder.response.equals(RESP_OK)) {
            return decoder.restaurants;
        } else {
            return new ArrayList<>();
        }
    }

    public static boolean updateRestaurantByPlaceId(String placeid) {
        JsonObject jsonObject = new JsonObject();
        jsonObject.addProperty("cmd", 1);
        jsonObject.addProperty("placeid", placeid);
        ResponseGetter getter = new ResponseGetter(jsonObject.toString());
        getter.start();
        try {
            getter.join();
        }
        catch(InterruptedException e) {
            return false;
        }
        String reponse_data = getter.response;
        Gson gson = new Gson();
        GsonRestaurantDecoder decoder =  gson.fromJson(reponse_data, GsonRestaurantDecoder.class);
        return (decoder.response.equals(RESP_OK)) ? true : false;
    }


}
