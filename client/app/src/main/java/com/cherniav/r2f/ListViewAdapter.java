package com.cherniav.r2f;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class ListViewAdapter extends BaseAdapter {

    Context mContext;
    LayoutInflater inflater;
    private List<RestaurantInfo> restaurantNamesList;

    ViewHolder holder;

    public ListViewAdapter(Context context, ArrayList<RestaurantInfo> restaurantNamesList) {
        mContext = context;
        this.restaurantNamesList = restaurantNamesList;
        inflater = LayoutInflater.from(mContext);
    }

    public class ViewHolder {
        TextView name;
    }

    @Override
    public int getCount() {
        return restaurantNamesList.size();
    }

    @Override
    public RestaurantInfo getItem(int position) {
        return restaurantNamesList.get(position);
    }

    @Override
    public long getItemId(int position) {
        return position;
    }

    @Override
    public View getView(final int position, View view, ViewGroup parent) {
        final ViewHolder holder;
        if (view == null) {
            holder = new ViewHolder();
            view = inflater.inflate(R.layout.activity_list_view_items, null);
            // Locate the TextViews in listview_item.xml
            holder.name = (TextView) view.findViewById(R.id.restaurantName);
            view.setTag(holder);
        } else {
            holder = (ViewHolder) view.getTag();
        }
        // Set the results into TextViews
        holder.name.clearComposingText();
        String display_str = restaurantNamesList.get(position).getRestaurantName() + '\n' +
                            restaurantNamesList.get(position).getReviewRating();
        holder.name.setText(display_str);
        return view;
    }


    // Filter Class
    public void filter(ArrayList<RestaurantInfo> newdata) {
        this.restaurantNamesList.clear();
        this.restaurantNamesList.addAll(newdata);
        notifyDataSetChanged();
    }
}