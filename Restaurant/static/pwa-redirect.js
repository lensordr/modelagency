// PWA redirect script
// Detects which restaurant the PWA was installed from and redirects accordingly

(function() {
    console.log('PWA Redirect: Starting check');
    console.log('Display mode standalone:', window.matchMedia('(display-mode: standalone)').matches);
    console.log('Navigator standalone:', window.navigator.standalone);
    console.log('Current URL:', window.location.href);
    
    // Check if this is a PWA launch (standalone mode)
    if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone) {
        // Clear old localStorage to avoid conflicts
        localStorage.removeItem('pwa_restaurant');
        
        // Get the restaurant from URL parameters (set when PWA is installed)
        const urlParams = new URLSearchParams(window.location.search);
        const restaurantSubdomain = urlParams.get('restaurant');
        
        console.log('PWA Redirect: Restaurant from URL:', restaurantSubdomain);
        
        if (restaurantSubdomain && restaurantSubdomain !== 'null') {
            const redirectUrl = `/r/${restaurantSubdomain}/business/login`;
            console.log('PWA Redirect: Redirecting to:', redirectUrl);
            window.location.href = redirectUrl;
        } else {
            console.log('PWA Redirect: No restaurant param, using fallback');
            window.location.href = '/r/test-restaurant/business/login';
        }
    } else {
        console.log('PWA Redirect: Not in PWA mode, skipping redirect');
    }
})();