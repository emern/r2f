package com.cherniav.r2f;

import android.content.Context;
import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import org.osmdroid.api.IMapController;
import org.osmdroid.util.GeoPoint;
import org.osmdroid.views.MapView;
import org.osmdroid.views.overlay.mylocation.GpsMyLocationProvider;
import org.osmdroid.views.overlay.mylocation.MyLocationNewOverlay;

public class MapFragment extends Fragment {

    // Declarations Setup
    private MapView map;
    private MyLocationNewOverlay mLocationOverlay;

    public MapFragment() {
        // Required empty public constructor
    }

    public static MapFragment newInstance() {
        MapFragment fragment = new MapFragment();
        return fragment;
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

        mapController.setZoom(8);

        // Set start point
        GeoPoint startPoint = new GeoPoint(49.2827, -123.1207);

        // Set map initialization point
        mapController.setCenter(startPoint);

        // Create overlay for current location
        mLocationOverlay = new MyLocationNewOverlay(new GpsMyLocationProvider(context),map);
        mLocationOverlay.enableMyLocation();
        map.getOverlays().add(this.mLocationOverlay);

        // Inflate the layout for this fragment
        return mapView;
    }
}