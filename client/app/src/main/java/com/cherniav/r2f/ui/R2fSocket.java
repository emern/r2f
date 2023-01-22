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
    private static String hostname = "207.81.215.40";
    private static int port = 12000;

    private static String RESP_OK = "OK";

    public static ArrayList<RestaurantInfo> searchRestaurantsWithName(String name) {
        JsonObject jsonObject = new JsonObject();
        jsonObject.addProperty("cmd", 0);
        jsonObject.addProperty("name", name);
        String reponse_data = getResponse(jsonObject.toString());
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
        String reponse_data = getResponse(jsonObject.toString());
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
        String reponse_data = getResponse(jsonObject.toString());
        Gson gson = new Gson();
        GsonRestaurantDecoder decoder =  gson.fromJson(reponse_data, GsonRestaurantDecoder.class);
        return (decoder.response.equals(RESP_OK)) ? true : false;
    }


    private static String getResponse(String sendData) {
        try (Socket socket = new Socket(hostname, port)) {

            OutputStream output = socket.getOutputStream();
            PrintWriter writer = new PrintWriter(output, true);
            writer.print(sendData);
            writer.flush();

            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            String outLine = "";
            for (String line = reader.readLine(); (line != null); line = reader.readLine()) {
                outLine = line;
            }
            output.close();
            reader.close();
            return outLine;

        } catch (UnknownHostException ex) {
            System.out.println("Server not found: " + ex.getMessage());
        } catch (IOException ex) {
            System.out.println("I/O error: " + ex.getMessage());
        }

        return "";
    }

    private class GsonRestaurantDecoder {
        String response;
        ArrayList<RestaurantInfo> restaurants;
    }

}
