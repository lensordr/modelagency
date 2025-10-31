// PWA Installation and Management
class PWAInstaller {
  constructor() {
    this.deferredPrompt = null;
    this.isInstalled = false;
    this.init();
  }

  init() {
    // Register service worker
    this.registerServiceWorker();
    
    // Handle install prompt
    this.setupInstallPrompt();
    
    // Check if already installed
    this.checkInstallStatus();
    
    // Setup notification permissions
    this.setupNotifications();
  }

  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/static/sw.js');
        console.log('PWA: Service Worker registered successfully', registration);
        
        // Handle updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.showUpdateAvailable();
            }
          });
        });
        
        return registration;
      } catch (error) {
        console.error('PWA: Service Worker registration failed', error);
      }
    }
  }

  setupInstallPrompt() {
    // Listen for beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
      console.log('PWA: Install prompt available');
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallButton();
    });

    // Listen for app installed event
    window.addEventListener('appinstalled', () => {
      console.log('PWA: App installed successfully');
      this.isInstalled = true;
      this.hideInstallButton();
      this.showInstalledMessage();
    });
  }

  checkInstallStatus() {
    // Check if running in standalone mode (installed)
    if (window.matchMedia('(display-mode: standalone)').matches || 
        window.navigator.standalone === true) {
      this.isInstalled = true;
      console.log('PWA: Running in standalone mode');
    }
  }

  async setupNotifications() {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      console.log('PWA: Notification permission:', permission);
    }
  }

  showInstallButton() {
    // Create install button if it doesn't exist
    let installBtn = document.getElementById('pwa-install-btn');
    if (!installBtn) {
      installBtn = document.createElement('button');
      installBtn.id = 'pwa-install-btn';
      installBtn.innerHTML = '📱 Install App';
      installBtn.className = 'pwa-install-btn';
      installBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #007bff;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,123,255,0.3);
        z-index: 1000;
        font-size: 14px;
        transition: all 0.3s ease;
      `;
      
      installBtn.addEventListener('mouseenter', () => {
        installBtn.style.transform = 'scale(1.05)';
        installBtn.style.boxShadow = '0 6px 16px rgba(0,123,255,0.4)';
      });
      
      installBtn.addEventListener('mouseleave', () => {
        installBtn.style.transform = 'scale(1)';
        installBtn.style.boxShadow = '0 4px 12px rgba(0,123,255,0.3)';
      });
      
      installBtn.addEventListener('click', () => this.installApp());
      document.body.appendChild(installBtn);
    }
    installBtn.style.display = 'block';
  }

  hideInstallButton() {
    const installBtn = document.getElementById('pwa-install-btn');
    if (installBtn) {
      installBtn.style.display = 'none';
    }
  }

  async installApp() {
    if (this.deferredPrompt) {
      this.deferredPrompt.prompt();
      const { outcome } = await this.deferredPrompt.userChoice;
      console.log('PWA: Install prompt outcome:', outcome);
      
      if (outcome === 'accepted') {
        this.hideInstallButton();
      }
      
      this.deferredPrompt = null;
    }
  }

  showInstalledMessage() {
    const message = document.createElement('div');
    message.innerHTML = '✅ TableLink installed successfully!';
    message.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #28a745;
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      font-weight: 600;
      z-index: 1001;
      box-shadow: 0 4px 12px rgba(40,167,69,0.3);
    `;
    
    document.body.appendChild(message);
    
    setTimeout(() => {
      message.remove();
    }, 3000);
  }

  showUpdateAvailable() {
    const updateBanner = document.createElement('div');
    updateBanner.innerHTML = `
      <span>🔄 New version available!</span>
      <button onclick="pwaInstaller.updateApp()" style="background: white; color: #007bff; border: none; padding: 5px 10px; border-radius: 4px; margin-left: 10px; cursor: pointer;">Update</button>
      <button onclick="this.parentElement.remove()" style="background: transparent; color: white; border: 1px solid white; padding: 5px 10px; border-radius: 4px; margin-left: 5px; cursor: pointer;">Later</button>
    `;
    updateBanner.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background: #007bff;
      color: white;
      padding: 12px 20px;
      text-align: center;
      z-index: 1002;
      font-weight: 600;
    `;
    
    document.body.appendChild(updateBanner);
  }

  updateApp() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistration().then(registration => {
        if (registration && registration.waiting) {
          registration.waiting.postMessage({ type: 'SKIP_WAITING' });
          window.location.reload();
        }
      });
    }
  }

  // Utility methods for offline functionality
  isOnline() {
    return navigator.onLine;
  }

  showOfflineMessage() {
    const offlineMsg = document.createElement('div');
    offlineMsg.id = 'offline-message';
    offlineMsg.innerHTML = '📡 You are offline. Some features may be limited.';
    offlineMsg.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background: #ffc107;
      color: #212529;
      padding: 10px 20px;
      text-align: center;
      z-index: 1003;
      font-weight: 600;
    `;
    document.body.appendChild(offlineMsg);
  }

  hideOfflineMessage() {
    const offlineMsg = document.getElementById('offline-message');
    if (offlineMsg) {
      offlineMsg.remove();
    }
  }

  // Setup online/offline event listeners
  setupConnectionListeners() {
    window.addEventListener('online', () => {
      console.log('PWA: Back online');
      this.hideOfflineMessage();
    });

    window.addEventListener('offline', () => {
      console.log('PWA: Gone offline');
      this.showOfflineMessage();
    });

    // Initial check
    if (!this.isOnline()) {
      this.showOfflineMessage();
    }
  }
}

// Initialize PWA installer when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.pwaInstaller = new PWAInstaller();
  window.pwaInstaller.setupConnectionListeners();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PWAInstaller;
}