package com.weixiutong.technician;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.webkit.*;
public class MainActivity extends Activity {
    private WebView wv;
    @Override @SuppressLint("SetJavaScriptEnabled")
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        wv = new WebView(this);
        setContentView(wv);
        WebSettings s = wv.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        wv.setWebViewClient(new WebViewClient());
        wv.setWebChromeClient(new WebChromeClient());
        wv.loadUrl("https://www.zpqy.cn/technician/");
    }
    @Override public void onBackPressed() {
        if (wv.canGoBack()) wv.goBack(); else super.onBackPressed();
    }
}
