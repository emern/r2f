package com.cherniav.r2f.ui.map;

import android.annotation.SuppressLint;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.location.Criteria;
import android.location.Location;
import android.location.LocationManager;
import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.cherniav.r2f.R;
import com.cherniav.r2f.RestaurantInfo;
import com.cherniav.r2f.ui.R2fSocket;

import org.osmdroid.api.IMapController;
import org.osmdroid.util.GeoPoint;
import org.osmdroid.views.MapView;
import org.osmdroid.views.overlay.Marker;
import org.osmdroid.views.overlay.mylocation.GpsMyLocationProvider;
import org.osmdroid.views.overlay.mylocation.MyLocationNewOverlay;

import java.util.ArrayList;

public class MapFragment extends Fragment {

    // Declarations Setup
    private MapView map;
    private MyLocationNewOverlay mLocationOverlay;

    public MapFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        final Context context = this.getActivity();

        View mapView = inflater.inflate(R.layout.fragment_map, null);

        map = mapView.findViewById(R.id.map);

        // Set controls
        map.setBuiltInZoomControls(true);
        map.setMultiTouchControls(true);

        // Set default map zoom via Map Controller
        // ////////(NOTE: make variable later)
        IMapController mapController = map.getController();

        mapController.setZoom(16);

        // Get current location
        LocationManager locationManager = (LocationManager) getActivity().getSystemService(Context.LOCATION_SERVICE);
        Criteria criteria = new Criteria();
        @SuppressLint("MissingPermission")
        Location location = locationManager.getLastKnownLocation(locationManager.getBestProvider(criteria, false));

        double longitude = location.getLongitude();
        double latitude = location.getLatitude();

        // Set start point
        GeoPoint startPoint = new GeoPoint(convertLoc(latitude, longitude));

        // Set map initialization point
        mapController.setCenter(startPoint);

        ArrayList<RestaurantInfo> markingInfo = R2fSocket.searchNearbyRestaurants(latitude, longitude, 5, 500);

        for (int i=0; i < markingInfo.size();i++){

            genMarker(markingInfo.get(i).getRestaurantName(), null, markingInfo.get(i).getReviewRating(), markingInfo.get(i).getNumReviews(), convertLoc(markingInfo.get(i).getrLatitude(), markingInfo.get(i).getrLongitude()));

        }

        Bitmap lookingBitmap = BitmapFactory.decodeResource(context.getResources(),
                R.drawable.locsprite);

        // Create overlay for current location
        mLocationOverlay = new MyLocationNewOverlay(new GpsMyLocationProvider(context),map);
        mLocationOverlay.enableMyLocation();
        mLocationOverlay.setDirectionArrow(lookingBitmap, lookingBitmap);
        map.getOverlays().add(this.mLocationOverlay);

        // Inflate the layout for this fragment
        return mapView;
    }

    // Function to convert lat, long to GeoPoint for mapping purposes
    public static GeoPoint convertLoc(double latitude, double longitude){
        int lat = (int)(latitude*1E6);
        int lng = (int)(longitude*1E6);
        return new GeoPoint(lat, lng);
    }
    public void genMarker(String mMarkerName, String mDescription, int rating, int reviewNum, GeoPoint mMarkerLoc){
        Marker newMarker = new Marker(map);
        newMarker.setPosition(mMarkerLoc);
        newMarker.setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM);
        newMarker.setTitle(mMarkerName);
        newMarker.setSnippet("GMaps Rating: " + rating + "<br>GMaps Review Qty: " + reviewNum + "<br>" + mDescription);
        map.getOverlays().add(newMarker);
    }
}