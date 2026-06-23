package com.personal.foundermentor;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * Single-screen wrapper that hosts the bundled offline web app
 * (assets/index.html) inside a WebView. No network is required to run it.
 */
public class MainActivity extends Activity {

    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().setStatusBarColor(Color.parseColor("#0B1220"));
        getWindow().setNavigationBarColor(Color.parseColor("#0B1220"));

        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#0B1220"));
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);   // enables localStorage -> progress persists
        s.setDatabaseEnabled(true);
        s.setUseWideViewPort(true);     // honour the page's viewport meta
        s.setLoadWithOverviewMode(true);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setMediaPlaybackRequiresUserGesture(true);

        // Keep all navigation inside the WebView.
        web.setWebViewClient(new WebViewClient());

        setContentView(web);

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl("file:///android_asset/index.html");
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        web.saveState(outState);
    }

    @Override
    public void onBackPressed() {
        // Ask the web app to go back one screen. If it's already at the top
        // (overview), drop to the home screen instead of force-closing.
        web.evaluateJavascript(
                "(window.__appHandleBack && window.__appHandleBack()) ? '1' : '0'",
                value -> {
                    if (value == null || !value.contains("1")) {
                        moveTaskToBack(true);
                    }
                });
    }
}
