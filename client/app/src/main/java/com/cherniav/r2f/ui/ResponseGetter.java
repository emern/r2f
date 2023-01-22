package com.cherniav.r2f.ui;

import com.cherniav.r2f.RestaurantInfo;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;

class ResponseGetter extends Thread {

    private static String hostname = "207.81.215.40";
    private static int port = 12000;
    String response;
    String sendData;

    public void run() {
        response = getResponse(sendData);
    }

    public ResponseGetter(String sendData) {
        this.sendData = sendData;
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
}