# Custom Web Engine Implementation Guide for TV Bro

## Overview

TV Bro is an Android TV browser that already has an elegant web engine abstraction system supporting multiple web engines. Currently, it supports:
- **GeckoView** (Mozilla Firefox engine)
- **Android WebView** (System WebView engine)

This guide provides comprehensive instructions for implementing custom web engines, including detecting and utilizing installed web engines like `com.google.android.webview`, Chromium-based engines, or any other custom web rendering engines available on the device.

## Current Architecture Analysis

### WebEngine Interface
The app uses a clean abstraction with the `WebEngine` interface located at:
```
app/src/main/java/com/phlox/tvwebbrowser/webengine/WebEngine.kt
```

### Supported Engines
Currently implemented engines:
1. **GeckoWebEngine** - Uses Mozilla GeckoView
2. **WebViewWebEngine** - Uses Android's built-in WebView

### Factory Pattern
The `WebEngineFactory` manages engine creation and initialization:
```
app/src/main/java/com/phlox/tvwebbrowser/webengine/WebEngineFactory.kt
```

## Custom Web Engine Implementation Strategy

### 1. Web Engine Detection System

First, we need to create a system to detect available web engines on the device.

#### Step 1.1: Create WebEngineDetector Utility

Create a new file: `app/src/main/java/com/phlox/tvwebbrowser/webengine/WebEngineDetector.kt`

```kotlin
package com.phlox.tvwebbrowser.webengine

import android.content.Context
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.webkit.WebView
import android.os.Build
import java.lang.reflect.Method

data class AvailableWebEngine(
    val engineId: String,
    val displayName: String,
    val packageName: String,
    val version: String?,
    val isSystemEngine: Boolean,
    val engineType: WebEngineType
)

enum class WebEngineType {
    SYSTEM_WEBVIEW,
    CHROME_WEBVIEW,
    CUSTOM_WEBVIEW,
    GECKO_VIEW,
    NATIVE_BROWSER,
    OTHER
}

object WebEngineDetector {
    
    /**
     * Detects all available web engines on the device
     */
    fun detectAvailableWebEngines(context: Context): List<AvailableWebEngine> {
        val engines = mutableListOf<AvailableWebEngine>()
        
        // Add system WebView
        engines.add(detectSystemWebView(context))
        
        // Add GeckoView if available
        detectGeckoView()?.let { engines.add(it) }
        
        // Detect Chrome-based WebViews
        engines.addAll(detectChromeBasedWebViews(context))
        
        // Detect other browser engines that could be used
        engines.addAll(detectOtherBrowserEngines(context))
        
        return engines
    }
    
    private fun detectSystemWebView(context: Context): AvailableWebEngine {
        val webViewPackage = getWebViewPackageInfo(context)
        return AvailableWebEngine(
            engineId = "system_webview",
            displayName = "System WebView",
            packageName = webViewPackage?.packageName ?: "com.android.webview",
            version = webViewPackage?.versionName,
            isSystemEngine = true,
            engineType = WebEngineType.SYSTEM_WEBVIEW
        )
    }
    
    private fun detectGeckoView(): AvailableWebEngine? {
        return try {
            Class.forName("org.mozilla.geckoview.GeckoRuntime")
            AvailableWebEngine(
                engineId = "gecko_view",
                displayName = "GeckoView (Firefox Engine)",
                packageName = "org.mozilla.geckoview",
                version = null, // Could extract from BuildConfig
                isSystemEngine = false,
                engineType = WebEngineType.GECKO_VIEW
            )
        } catch (e: ClassNotFoundException) {
            null
        }
    }
    
    private fun detectChromeBasedWebViews(context: Context): List<AvailableWebEngine> {
        val engines = mutableListOf<AvailableWebEngine>()
        val pm = context.packageManager
        
        val chromeBasedPackages = listOf(
            "com.google.android.webview",
            "com.android.chrome",
            "com.chrome.beta",
            "com.chrome.dev",
            "com.chrome.canary",
            "com.microsoft.emmx", // Edge
            "com.opera.browser",
            "com.opera.mini.native",
            "org.chromium.chrome",
            "com.vivaldi.browser"
        )
        
        chromeBasedPackages.forEach { packageName ->
            try {
                val packageInfo = pm.getPackageInfo(packageName, 0)
                val appInfo = pm.getApplicationInfo(packageName, 0)
                
                engines.add(AvailableWebEngine(
                    engineId = "chrome_based_$packageName",
                    displayName = pm.getApplicationLabel(appInfo).toString(),
                    packageName = packageName,
                    version = packageInfo.versionName,
                    isSystemEngine = (appInfo.flags and ApplicationInfo.FLAG_SYSTEM) != 0,
                    engineType = when {
                        packageName.contains("webview") -> WebEngineType.CHROME_WEBVIEW
                        packageName.contains("chrome") -> WebEngineType.NATIVE_BROWSER
                        else -> WebEngineType.OTHER
                    }
                ))
            } catch (e: PackageManager.NameNotFoundException) {
                // Package not installed
            }
        }
        
        return engines
    }
    
    private fun detectOtherBrowserEngines(context: Context): List<AvailableWebEngine> {
        val engines = mutableListOf<AvailableWebEngine>()
        val pm = context.packageManager
        
        val otherBrowserPackages = listOf(
            "org.mozilla.firefox",
            "org.mozilla.fenix",
            "org.mozilla.focus",
            "com.duckduckgo.mobile.android",
            "com.brave.browser",
            "org.torproject.torbrowser",
            "acr.browser.lightning",
            "com.kiwibrowser.browser"
        )
        
        otherBrowserPackages.forEach { packageName ->
            try {
                val packageInfo = pm.getPackageInfo(packageName, 0)
                val appInfo = pm.getApplicationInfo(packageName, 0)
                
                engines.add(AvailableWebEngine(
                    engineId = "browser_engine_$packageName",
                    displayName = pm.getApplicationLabel(appInfo).toString(),
                    packageName = packageName,
                    version = packageInfo.versionName,
                    isSystemEngine = false,
                    engineType = WebEngineType.NATIVE_BROWSER
                ))
            } catch (e: PackageManager.NameNotFoundException) {
                // Package not installed
            }
        }
        
        return engines
    }
    
    private fun getWebViewPackageInfo(context: Context): android.content.pm.PackageInfo? {
        return try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                // Use getCurrentWebViewPackage for Android 8.0+
                val webViewPackage = WebView.getCurrentWebViewPackage()
                context.packageManager.getPackageInfo(webViewPackage?.packageName ?: "", 0)
            } else {
                // Fallback for older versions
                context.packageManager.getPackageInfo("com.google.android.webview", 0)
            }
        } catch (e: Exception) {
            null
        }
    }
}
```

#### Step 1.2: Update Config.kt to Support Multiple Engines

Add to `Config.kt`:

```kotlin
// Add these constants to the companion object
const val ENGINE_CHROME_WEBVIEW = "ChromeWebView"
const val ENGINE_CUSTOM_WEBVIEW = "CustomWebView"

// Update SupportedWebEngines array
val SupportedWebEngines = arrayOf(ENGINE_GECKO_VIEW, ENGINE_WEB_VIEW, ENGINE_CHROME_WEBVIEW, ENGINE_CUSTOM_WEBVIEW)

// Add method to get available engines
fun getAvailableWebEngines(context: Context): List<AvailableWebEngine> {
    return WebEngineDetector.detectAvailableWebEngines(context)
}

// Add property to store selected custom engine
var customWebEnginePackage: String?
    get() = prefs.getString("custom_web_engine_package", null)
    set(value) {
        if (value == null) prefs.edit().remove("custom_web_engine_package").apply()
        else prefs.edit().putString("custom_web_engine_package", value).apply()
    }
```

### 2. Custom WebView Engine Implementation

#### Step 2.1: Create CustomWebViewEngine

Create `app/src/main/java/com/phlox/tvwebbrowser/webengine/custom/CustomWebViewEngine.kt`:

```kotlin
package com.phlox.tvwebbrowser.webengine.custom

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.view.View
import android.view.ViewGroup
import com.phlox.tvwebbrowser.model.WebTabState
import com.phlox.tvwebbrowser.webengine.WebEngine
import com.phlox.tvwebbrowser.webengine.WebEngineWindowProviderCallback
import com.phlox.tvwebbrowser.webengine.webview.WebViewWebEngine

/**
 * Custom WebView engine that can use different WebView implementations
 * such as Chrome WebView, system WebView variants, or other WebView-compatible engines
 */
class CustomWebViewEngine(
    tab: WebTabState,
    private val customPackageName: String? = null
) : WebEngine {
    
    private val baseWebViewEngine: WebViewWebEngine = WebViewWebEngine(tab)
    private var customWebView: CustomWebViewEx? = null
    
    override val url: String?
        get() = baseWebViewEngine.url
    
    override var userAgentString: String?
        get() = baseWebViewEngine.userAgentString
        set(value) {
            baseWebViewEngine.userAgentString = value
        }
    
    @Throws(Exception::class)
    override fun getOrCreateView(activityContext: Context): View {
        if (customPackageName != null) {
            // Try to create a WebView using the custom package
            return createCustomWebView(activityContext)
        }
        return baseWebViewEngine.getOrCreateView(activityContext)
    }
    
    private fun createCustomWebView(context: Context): View {
        if (customWebView == null) {
            customWebView = CustomWebViewEx(context, customPackageName)
        }
        return customWebView!!
    }
    
    // Delegate all other methods to base implementation
    override fun saveState(): Any? = baseWebViewEngine.saveState()
    override fun restoreState(savedInstanceState: Any) = baseWebViewEngine.restoreState(savedInstanceState)
    override fun stateFromBytes(bytes: ByteArray): Any? = baseWebViewEngine.stateFromBytes(bytes)
    override fun loadUrl(url: String) = baseWebViewEngine.loadUrl(url)
    override fun canGoForward(): Boolean = baseWebViewEngine.canGoForward()
    override fun goForward() = baseWebViewEngine.goForward()
    override fun canZoomIn(): Boolean = baseWebViewEngine.canZoomIn()
    override fun zoomIn() = baseWebViewEngine.zoomIn()
    override fun canZoomOut(): Boolean = baseWebViewEngine.canZoomOut()
    override fun zoomOut() = baseWebViewEngine.zoomOut()
    override fun zoomBy(zoomBy: Float) = baseWebViewEngine.zoomBy(zoomBy)
    override fun evaluateJavascript(script: String) = baseWebViewEngine.evaluateJavascript(script)
    override fun setNetworkAvailable(connected: Boolean) = baseWebViewEngine.setNetworkAvailable(connected)
    override fun getView(): View? = customWebView ?: baseWebViewEngine.getView()
    override fun canGoBack(): Boolean = baseWebViewEngine.canGoBack()
    override fun goBack() = baseWebViewEngine.goBack()
    override fun reload() = baseWebViewEngine.reload()
    override fun onFilePicked(resultCode: Int, data: Intent?) = baseWebViewEngine.onFilePicked(resultCode, data)
    override fun onResume() = baseWebViewEngine.onResume()
    override fun onPause() = baseWebViewEngine.onPause()
    override fun onUpdateAdblockSetting(newState: Boolean) = baseWebViewEngine.onUpdateAdblockSetting(newState)
    override fun hideFullscreenView() = baseWebViewEngine.hideFullscreenView()
    override fun togglePlayback() = baseWebViewEngine.togglePlayback()
    override suspend fun renderThumbnail(bitmap: Bitmap?): Bitmap? = baseWebViewEngine.renderThumbnail(bitmap)
    override fun onAttachToWindow(callback: WebEngineWindowProviderCallback, parent: ViewGroup, fullscreenViewParent: ViewGroup) = 
        baseWebViewEngine.onAttachToWindow(callback, parent, fullscreenViewParent)
    override fun onDetachFromWindow(completely: Boolean, destroyTab: Boolean) = 
        baseWebViewEngine.onDetachFromWindow(completely, destroyTab)
    override fun trimMemory() = baseWebViewEngine.trimMemory()
    override fun onPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray): Boolean = 
        baseWebViewEngine.onPermissionsResult(requestCode, permissions, grantResults)
    
    companion object {
        fun clearCache(ctx: Context) {
            WebViewWebEngine.clearCache(ctx)
        }
    }
}
```

#### Step 2.2: Create CustomWebViewEx

Create `app/src/main/java/com/phlox/tvwebbrowser/webengine/custom/CustomWebViewEx.kt`:

```kotlin
package com.phlox.tvwebbrowser.webengine.custom

import android.annotation.SuppressLint
import android.content.Context
import android.webkit.WebView
import android.webkit.WebSettings
import java.lang.reflect.Method

/**
 * Extended WebView that can load custom WebView implementations
 */
@SuppressLint("SetJavaScriptEnabled")
class CustomWebViewEx(
    context: Context,
    private val customPackageName: String?
) : WebView(createContextForPackage(context, customPackageName)) {
    
    init {
        setupWebView()
    }
    
    private fun setupWebView() {
        settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            setAppCacheEnabled(true)
            allowFileAccess = true
            allowContentAccess = true
            setSupportZoom(true)
            builtInZoomControls = true
            displayZoomControls = false
            useWideViewPort = true
            loadWithOverviewMode = true
            mixedContentMode = WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE
            
            // Try to set additional properties for custom WebView engines
            trySetCustomWebViewSettings()
        }
    }
    
    private fun trySetCustomWebViewSettings() {
        try {
            // Attempt to enable additional features that might be available in custom WebView implementations
            if (customPackageName?.contains("chrome") == true) {
                // Chrome-specific settings
                settings.setRenderPriority(WebSettings.RenderPriority.HIGH)
                settings.cacheMode = WebSettings.LOAD_DEFAULT
            }
        } catch (e: Exception) {
            // Ignore if custom settings are not supported
        }
    }
    
    companion object {
        private fun createContextForPackage(context: Context, packageName: String?): Context {
            return if (packageName != null) {
                try {
                    // Try to create a context for the custom package
                    context.createPackageContext(packageName, Context.CONTEXT_INCLUDE_CODE or Context.CONTEXT_IGNORE_SECURITY)
                } catch (e: Exception) {
                    // Fall back to regular context if package context creation fails
                    context
                }
            } else {
                context
            }
        }
    }
}
```

### 3. External Browser Engine Integration

#### Step 3.1: Create ExternalBrowserEngine

For browsers like Firefox, Chrome, etc., create an engine that can launch external browsers:

Create `app/src/main/java/com/phlox/tvwebbrowser/webengine/external/ExternalBrowserEngine.kt`:

```kotlin
package com.phlox.tvwebbrowser.webengine.external

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import android.widget.TextView
import com.phlox.tvwebbrowser.R
import com.phlox.tvwebbrowser.model.WebTabState
import com.phlox.tvwebbrowser.webengine.WebEngine
import com.phlox.tvwebbrowser.webengine.WebEngineWindowProviderCallback

/**
 * Web engine that delegates to external browsers
 * This is useful for integrating with browsers that don't provide embeddable engines
 */
class ExternalBrowserEngine(
    private val tab: WebTabState,
    private val browserPackageName: String
) : WebEngine {
    
    private var placeholderView: View? = null
    private var currentUrl: String? = null
    private var callback: WebEngineWindowProviderCallback? = null
    
    override val url: String?
        get() = currentUrl
    
    override var userAgentString: String? = null
    
    override fun saveState(): Any? {
        return mapOf("url" to currentUrl)
    }
    
    override fun restoreState(savedInstanceState: Any) {
        if (savedInstanceState is Map<*, *>) {
            currentUrl = savedInstanceState["url"] as? String
        }
    }
    
    override fun stateFromBytes(bytes: ByteArray): Any? = null
    
    override fun loadUrl(url: String) {
        currentUrl = url
        launchExternalBrowser(url)
    }
    
    private fun launchExternalBrowser(url: String) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            intent.setPackage(browserPackageName)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            callback?.getActivity()?.startActivity(intent)
        } catch (e: Exception) {
            // Fallback to system default browser
            try {
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                callback?.getActivity()?.startActivity(intent)
            } catch (e: Exception) {
                // Handle error
            }
        }
    }
    
    override fun canGoForward(): Boolean = false
    override fun goForward() {}
    override fun canZoomIn(): Boolean = false
    override fun zoomIn() {}
    override fun canZoomOut(): Boolean = false
    override fun zoomOut() {}
    override fun zoomBy(zoomBy: Float) {}
    override fun evaluateJavascript(script: String) {}
    override fun setNetworkAvailable(connected: Boolean) {}
    
    override fun getView(): View? = placeholderView
    
    @Throws(Exception::class)
    override fun getOrCreateView(activityContext: Context): View {
        if (placeholderView == null) {
            placeholderView = createPlaceholderView(activityContext)
        }
        return placeholderView!!
    }
    
    private fun createPlaceholderView(context: Context): View {
        val layout = FrameLayout(context)
        val textView = TextView(context)
        textView.text = "Content opened in external browser: $browserPackageName"
        textView.textAlignment = View.TEXT_ALIGNMENT_CENTER
        layout.addView(textView)
        return layout
    }
    
    override fun canGoBack(): Boolean = false
    override fun goBack() {}
    override fun reload() { currentUrl?.let { loadUrl(it) } }
    override fun onFilePicked(resultCode: Int, data: Intent?) {}
    override fun onResume() {}
    override fun onPause() {}
    override fun onUpdateAdblockSetting(newState: Boolean) {}
    override fun hideFullscreenView() {}
    override fun togglePlayback() {}
    override suspend fun renderThumbnail(bitmap: Bitmap?): Bitmap? = null
    
    override fun onAttachToWindow(callback: WebEngineWindowProviderCallback, parent: ViewGroup, fullscreenViewParent: ViewGroup) {
        this.callback = callback
        placeholderView?.let { parent.addView(it) }
    }
    
    override fun onDetachFromWindow(completely: Boolean, destroyTab: Boolean) {
        (placeholderView?.parent as? ViewGroup)?.removeView(placeholderView)
        callback = null
    }
    
    override fun trimMemory() {}
    override fun onPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray): Boolean = false
}
```

### 4. Update WebEngineFactory

Update `WebEngineFactory.kt` to support the new engines:

```kotlin
@Suppress("KotlinConstantConditions")
fun createWebEngine(tab: WebTabState): WebEngine {
    return when (TVBro.config.webEngine) {
        Config.ENGINE_GECKO_VIEW -> GeckoWebEngine(tab)
        Config.ENGINE_CHROME_WEBVIEW -> CustomWebViewEngine(tab, "com.google.android.webview")
        Config.ENGINE_CUSTOM_WEBVIEW -> CustomWebViewEngine(tab, TVBro.config.customWebEnginePackage)
        else -> {
            // Check if it's an external browser engine
            if (TVBro.config.webEngine.startsWith("browser_engine_")) {
                val packageName = TVBro.config.webEngine.removePrefix("browser_engine_")
                ExternalBrowserEngine(tab, packageName)
            } else {
                WebViewWebEngine(tab)
            }
        }
    }
}

suspend fun clearCache(ctx: Context) {
    when {
        TVBro.config.isWebEngineGecko() -> GeckoWebEngine.clearCache(ctx)
        TVBro.config.webEngine == Config.ENGINE_CHROME_WEBVIEW ||
        TVBro.config.webEngine == Config.ENGINE_CUSTOM_WEBVIEW -> CustomWebViewEngine.clearCache(ctx)
        else -> WebViewWebEngine.clearCache(ctx)
    }
}
```

### 5. Settings UI Integration

#### Step 5.1: Update Settings to Show Available Engines

In the settings views, update to show all detected engines:

```kotlin
// In MainSettingsView.kt or similar settings class

private fun updateWebEngineSettings() {
    val availableEngines = Config.getAvailableWebEngines(context)
    val engineTitles = mutableListOf<String>()
    val engineValues = mutableListOf<String>()
    
    // Add default engines
    engineTitles.add("System WebView")
    engineValues.add(Config.ENGINE_WEB_VIEW)
    
    if (availableEngines.any { it.engineType == WebEngineType.GECKO_VIEW }) {
        engineTitles.add("GeckoView (Firefox)")
        engineValues.add(Config.ENGINE_GECKO_VIEW)
    }
    
    // Add detected custom engines
    availableEngines.forEach { engine ->
        when (engine.engineType) {
            WebEngineType.CHROME_WEBVIEW -> {
                engineTitles.add("${engine.displayName} WebView")
                engineValues.add(Config.ENGINE_CHROME_WEBVIEW)
            }
            WebEngineType.NATIVE_BROWSER -> {
                engineTitles.add("${engine.displayName} (External)")
                engineValues.add(engine.engineId)
            }
            else -> {
                engineTitles.add(engine.displayName)
                engineValues.add(engine.engineId)
            }
        }
    }
    
    // Update UI with available engines
    updateWebEngineSpinner(engineTitles.toTypedArray(), engineValues.toTypedArray())
}
```

## Implementation Steps

### Phase 1: Basic Custom WebView Support
1. **Add WebEngineDetector utility** - Detect available WebView implementations
2. **Create CustomWebViewEngine** - Support Chrome WebView and other WebView variants
3. **Update Config and Factory** - Add configuration support for custom engines
4. **Test with Chrome WebView** - Verify functionality with `com.google.android.webview`

### Phase 2: External Browser Integration
1. **Implement ExternalBrowserEngine** - Support launching external browsers
2. **Add browser detection** - Detect installed browsers like Firefox, Chrome, etc.
3. **Create placeholder UI** - Show status when content is opened externally
4. **Test with multiple browsers** - Verify compatibility

### Phase 3: Advanced Features
1. **Custom engine preferences** - Allow users to select preferred engines per site
2. **Engine performance monitoring** - Track and compare engine performance
3. **Fallback mechanisms** - Automatic fallback when primary engine fails
4. **Deep integration** - Explore deeper integration possibilities with specific engines

### Phase 4: Testing and Optimization
1. **Comprehensive testing** - Test with all detected engines
2. **Performance optimization** - Optimize engine switching and memory usage
3. **Error handling** - Robust error handling for failed engine loads
4. **User documentation** - Create user guide for engine selection

## Technical Considerations

### Security
- **Package verification** - Verify integrity of custom WebView packages
- **Permission handling** - Ensure proper permission delegation to custom engines
- **Sandbox isolation** - Maintain security boundaries between engines

### Performance
- **Memory management** - Efficient switching between engines
- **Loading optimization** - Fast engine initialization
- **Resource sharing** - Share common resources between engines where possible

### Compatibility
- **API level support** - Ensure compatibility across Android versions
- **Device compatibility** - Handle devices with limited engine support
- **Feature parity** - Maintain consistent functionality across engines

## Testing Strategy

### Manual Testing
1. **Engine detection** - Verify all engines are properly detected
2. **Switching engines** - Test seamless switching between engines
3. **Feature compatibility** - Ensure all browser features work with each engine
4. **Performance comparison** - Compare loading times and memory usage

### Automated Testing
1. **Unit tests** - Test engine detection and factory creation
2. **Integration tests** - Test engine integration with app components
3. **Performance tests** - Automated performance comparison
4. **Compatibility tests** - Test across different Android versions and devices

## Future Enhancements

### Advanced Engine Support
- **WebView2** support for newer Microsoft Edge engine
- **Custom Chromium builds** - Support for specialized Chromium variants
- **Native engine integration** - Direct integration with browser native APIs

### Engine Management
- **Automatic updates** - Keep custom engines updated
- **Engine marketplace** - Download and install additional engines
- **Performance analytics** - Detailed performance monitoring and reporting

### User Experience
- **Engine recommendations** - Recommend best engine for device/content
- **Quick switching** - Fast engine switching via gestures or shortcuts
- **Engine profiles** - Different engine configurations for different use cases

## Conclusion

This implementation guide provides a comprehensive approach to adding custom web engine support to TV Bro. The modular architecture allows for:

1. **Flexibility** - Support for multiple engine types
2. **Extensibility** - Easy addition of new engines
3. **Compatibility** - Graceful fallback mechanisms
4. **Performance** - Optimized engine selection and management

By following this guide, TV Bro can become a truly universal browser capable of leveraging any web engine available on the device, providing users with the best possible browsing experience tailored to their specific needs and device capabilities.