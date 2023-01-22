package com.cherniav.r2f.ui.review;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.ViewModel;

public class ReviewViewModel extends ViewModel {

    private final MutableLiveData<String> mText;

    public ReviewViewModel() {
        mText = new MutableLiveData<>();
        mText.setValue("Review Placeholder text");
    }

    public LiveData<String> getText() {
        return mText;
    }
}