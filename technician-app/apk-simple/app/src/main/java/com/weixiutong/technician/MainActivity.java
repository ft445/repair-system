package com.weixiutong.technician;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.webkit.*;
import android.graphics.Bitmap;

public class MainActivity extends Activity {
    private WebView wv;
    private static final String TAG = "RepairApp";

    @Override
    @SuppressLint("SetJavaScriptEnabled")
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        wv = new WebView(this);
        setContentView(wv);

        WebSettings s = wv.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setAllowFileAccessFromFileURLs(true);
        s.setAllowUniversalAccessFromFileURLs(true);
        s.setDatabaseEnabled(true);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        s.setCacheMode(WebSettings.LOAD_NO_CACHE);
        s.setMediaPlaybackRequiresUserGesture(false);

        wv.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView v, String url, Bitmap favicon) {
                Log.d(TAG, "Loading: " + url);
            }
            @Override
            public void onPageFinished(WebView v, String url) {
                Log.d(TAG, "Loaded: " + url);
                v.evaluateJavascript(
                    "console.log('=== App started ===');" +
                    "document.addEventListener('DOMContentLoaded', function(){" +
                    "  console.log('DOM ready, #app:', document.getElementById('app'));" +
                    "});" +
                    "window.onerror = function(msg,url,line){ console.error('ERR:',msg,url,line); };",
                    null
                );
            }
        });

        wv.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage m) {
                Log.d(TAG, "[JS] " + m.message() + " (" + m.sourceId() + ":" + m.lineNumber() + ")");
                return true;
            }
        });

        wv.loadUrl("file:///android_asset/public/index.html");
    }

    @Override
    public void onBackPressed() {
        if (wv.canGoBack()) wv.goBack();
        else super.onBackPressed();
    }
}
