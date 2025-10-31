// PWA redirect script
// Detects which restaurant the PWA was installed from and redirects accordingly

(function() {
    // Show debug info on screen for mobile testing
    function showDebug(message) {
        const debug = document.createElement('div');
        debug.style.cssText = 'position:fixed;top:0;left:0;right:0;background:red;color:white;padding:10px;z-index:9999;font-size:12px;';
        debug.textContent = message;
        document.body.appendChild(debug);
        setTimeout(() => debug.remove(), 3000);
    }
    
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;
    const urlParams = new URLSearchParams(window.location.search);
    const restaurantSubdomain = urlParams.get('pwa_restaurant');
    
    showDebug(`PWA: standalone=${isStandalone}, restaurant=${restaurantSubdomain}`);
    
    // Check if this is a PWA launch (standalone mode)
    if (isStandalone) {
        // Clear old localStorage to avoid conflicts
        localStorage.removeItem('pwa_restaurant');
        
        if (restaurantSubdomain && restaurantSubdomain !== 'null') {
            const redirectUrl = `/r/${restaurantSubdomain}/business/login`;
            showDebug(`Redirecting to: ${redirectUrl}`);
            setTimeout(() => window.location.href = redirectUrl, 1000);
        } else {
            showDebug('No restaurant param, using fallback');
            setTimeout(() => window.location.href = '/r/test-restaurant/business/login', 1000);
        }
    }
})();