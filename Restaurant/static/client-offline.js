// Offline functionality for client orders
class ClientOfflineManager {
  constructor() {
    this.offlineOrders = [];
    this.isOnline = navigator.onLine;
    this.init();
  }

  init() {
    // Load offline orders from localStorage
    this.loadOfflineOrders();
    
    // Setup online/offline event listeners
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());
    
    // Intercept order submissions
    this.interceptOrderSubmissions();
  }

  loadOfflineOrders() {
    try {
      const stored = localStorage.getItem('tablelink_offline_orders');
      this.offlineOrders = stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Error loading offline orders:', error);
      this.offlineOrders = [];
    }
  }

  saveOfflineOrders() {
    try {
      localStorage.setItem('tablelink_offline_orders', JSON.stringify(this.offlineOrders));
    } catch (error) {
      console.error('Error saving offline orders:', error);
    }
  }

  handleOnline() {
    console.log('Client: Back online');
    this.isOnline = true;
    this.hideOfflineMessage();
    this.syncOfflineOrders();
  }

  handleOffline() {
    console.log('Client: Gone offline');
    this.isOnline = false;
    this.showOfflineMessage();
  }

  showOfflineMessage() {
    let offlineMsg = document.getElementById('client-offline-message');
    if (!offlineMsg) {
      offlineMsg = document.createElement('div');
      offlineMsg.id = 'client-offline-message';
      offlineMsg.innerHTML = `
        <div style="background: #ffc107; color: #212529; padding: 10px 20px; text-align: center; font-weight: 600; position: fixed; top: 0; left: 0; right: 0; z-index: 1000;">
          📡 You are offline. Orders will be saved and sent when connection returns.
          ${this.offlineOrders.length > 0 ? `<br><small>${this.offlineOrders.length} order(s) waiting to sync</small>` : ''}
        </div>
      `;
      document.body.appendChild(offlineMsg);
    }
  }

  hideOfflineMessage() {
    const offlineMsg = document.getElementById('client-offline-message');
    if (offlineMsg) {
      offlineMsg.remove();
    }
  }

  interceptOrderSubmissions() {
    // Override the global placeOrder function if it exists
    if (typeof window.placeOrder === 'function') {
      const originalPlaceOrder = window.placeOrder;
      window.placeOrder = async (event) => {
        if (!this.isOnline) {
          return this.handleOfflineOrder(event);
        }
        return originalPlaceOrder(event);
      };
    }
  }

  async handleOfflineOrder(event) {
    event.preventDefault();
    
    const code = document.getElementById('table-code').value;
    const tableNumber = document.getElementById('table-number-input').value;
    
    if (code.length !== 3) {
      this.showMessage('Please enter a valid 3-digit code', 'error');
      return;
    }
    
    if (!window.order || window.order.length === 0) {
      this.showMessage('Please select at least one item', 'error');
      return;
    }
    
    // Create offline order
    const offlineOrder = {
      id: Date.now(),
      tableNumber: tableNumber,
      code: code,
      items: JSON.parse(JSON.stringify(window.order)), // Deep copy
      timestamp: new Date().toISOString(),
      synced: false
    };
    
    // Save offline order
    this.offlineOrders.push(offlineOrder);
    this.saveOfflineOrders();
    
    // Show success message
    this.showMessage('Order saved offline. Will be sent when connection returns.', 'success');
    
    // Reset form
    window.order = [];
    document.getElementById('order-form').reset();
    document.querySelectorAll('[id^=\"qty-\"]').forEach(el => el.textContent = '0');
    if (typeof window.updateOrderDisplay === 'function') {
      window.updateOrderDisplay();
    }
    
    // Update offline message to show pending orders
    this.showOfflineMessage();
  }

  async syncOfflineOrders() {
    if (this.offlineOrders.length === 0) return;
    
    console.log(`Syncing ${this.offlineOrders.length} offline orders`);
    
    for (const offlineOrder of this.offlineOrders) {
      if (offlineOrder.synced) continue;
      
      try {
        const formData = new FormData();
        formData.append('table_number', offlineOrder.tableNumber);
        formData.append('code', offlineOrder.code);
        formData.append('items', JSON.stringify(offlineOrder.items));
        
        const baseUrl = window.location.pathname.includes('/r/') ? 
          window.location.pathname.split('/table/')[0] : '';
        
        const response = await fetch(`${baseUrl}/client/order`, {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          offlineOrder.synced = true;
          console.log(`Synced offline order ${offlineOrder.id}`);
        } else {
          console.error(`Failed to sync order ${offlineOrder.id}`);
        }
      } catch (error) {
        console.error(`Error syncing order ${offlineOrder.id}:`, error);
      }
    }
    
    // Remove synced orders
    this.offlineOrders = this.offlineOrders.filter(order => !order.synced);
    this.saveOfflineOrders();
    
    if (this.offlineOrders.length === 0) {
      this.showMessage('All offline orders synced successfully!', 'success');
    }
  }

  showMessage(message, type) {
    if (typeof window.showMessage === 'function') {
      window.showMessage(message, type);
    } else {
      // Fallback message display
      const messageDiv = document.createElement('div');
      messageDiv.textContent = message;
      messageDiv.style.cssText = `
        position: fixed;
        top: 50px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        font-weight: 600;
        z-index: 1001;
        ${type === 'success' ? 'background: #28a745; color: white;' : 'background: #dc3545; color: white;'}
      `;
      document.body.appendChild(messageDiv);
      
      setTimeout(() => {
        messageDiv.remove();
      }, 5000);
    }
  }

  // Get offline order status for display
  getOfflineStatus() {
    return {
      hasOfflineOrders: this.offlineOrders.length > 0,
      offlineOrderCount: this.offlineOrders.length,
      isOnline: this.isOnline
    };
  }
}

// Initialize offline manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.clientOfflineManager = new ClientOfflineManager();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ClientOfflineManager;
}