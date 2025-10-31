// PWA redirect script
// Detects which restaurant the PWA was installed from and redirects accordingly

(function() {
    // Check if this is a PWA launch (standalone mode)
    if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone) {
        // Get the restaurant from localStorage (set when PWA is installed)
        const restaurantSubdomain = localStorage.getItem('pwa_restaurant');
        
        if (restaurantSubdomain && restaurantSubdomain !== 'null') {
            // Redirect to the specific restaurant login
            window.location.href = `/r/${restaurantSubdomain}/business/login`;
        } else {
            // Fallback to test-restaurant
            window.location.href = '/r/test-restaurant/business/login';
        }
    }
})();