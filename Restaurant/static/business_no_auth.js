let tables = [];
let menuItems = [];

// Sound alerts
const newOrderSound = new Audio('/static/sounds/new-order.mp3');
const checkoutSound = new Audio('/static/sounds/checkout-request.mp3');

// Track previous state for sound alerts
let previousTables = [];

// Track notifications
let notificationCount = 0;
let currentSection = 'live-orders';

document.addEventListener('DOMContentLoaded', function() {
    currentDate = new Date().toISOString().split('T')[0];
    currentSection = 'live-orders';
    showSection('live-orders');
    
    document.getElementById('upload-form').addEventListener('submit', uploadMenu);
    
    // Modal controls
    const modal = document.getElementById('order-modal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.onclick = function() {
        closeModal();
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            closeModal();
        }
    }
    
    document.getElementById('checkout-table-btn').addEventListener('click', finishTable);
    
    // Load waiters for modal
    loadWaitersForModal();
    
    // Auto-refresh dashboard every 3 seconds
    setInterval(loadDashboard, 3000);
    
    // Initialize app
    loadDashboard();
    loadMenuItems();
    loadSales('day');
    loadWaiters();
});

let currentTableNumber = null;

async function closeModal() {
    const modal = document.getElementById('order-modal');
    
    // Mark order as viewed when closing modal
    if (currentTableNumber) {
        try {
            console.log(`Marking table ${currentTableNumber} as viewed`);
            const response = await fetch(`/business/mark_viewed/${currentTableNumber}`, {
                method: 'POST'
            });
            if (response.ok) {
                console.log('Order marked as viewed successfully');
            }
        } catch (error) {
            console.error('Error marking order as viewed:', error);
        }
    }
    
    modal.style.display = 'none';
    currentTableNumber = null;
}

function getAuthHeaders() {
    return {
        'Content-Type': 'application/json'
    };
}

function logout() {
    window.location.href = '/business/login';
}

async function loadDashboard() {
    try {
        const response = await fetch('/business/dashboard');
        const data = await response.json();
        
        if (response.ok) {
            // Check for sound alerts before updating tables
            checkForSoundAlerts(data.tables);
            
            tables = data.tables;
            displayTables();
            
            // Update previous state
            previousTables = JSON.parse(JSON.stringify(data.tables));
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function checkForSoundAlerts(currentTables) {
    if (previousTables.length === 0) {
        previousTables = JSON.parse(JSON.stringify(currentTables));
        return;
    }
    
    let newNotifications = 0;
    
    currentTables.forEach(currentTable => {
        const previousTable = previousTables.find(t => t.table_number === currentTable.table_number);
        
        if (previousTable) {
            // Check for new orders or extra orders
            if ((currentTable.status === 'occupied' && previousTable.status === 'free') ||
                (currentTable.has_extra_order && !previousTable.has_extra_order)) {
                try {
                    newOrderSound.play().catch(e => console.log('Sound play failed:', e));
                } catch (e) {
                    console.log('Sound not available');
                }
                
                // Add notification if not on live orders tab
                if (currentSection !== 'live-orders') {
                    newNotifications++;
                    console.log(`New order notification added for table ${currentTable.table_number}`);
                }
            }
            
            // Check for checkout requests
            if (currentTable.checkout_requested && !previousTable.checkout_requested) {
                try {
                    checkoutSound.play().catch(e => console.log('Sound play failed:', e));
                } catch (e) {
                    console.log('Sound not available');
                }
                
                // Add notification if not on live orders tab
                if (currentSection !== 'live-orders') {
                    newNotifications++;
                    console.log(`Checkout notification added for table ${currentTable.table_number}`);
                }
            }
        }
    });
    
    // Update notification count
    if (newNotifications > 0) {
        notificationCount += newNotifications;
        console.log(`Total notifications: ${notificationCount}`);
        updateNotificationBadge();
    }
}

function displayTables() {
    const tablesGrid = document.getElementById('tables-grid');
    tablesGrid.innerHTML = '';
    
    tables.forEach(table => {
        const tableCard = document.createElement('div');
        let cardClass = `table-card ${table.status}`;
        
        if (table.checkout_requested) {
            cardClass += ' checkout-requested';
            tableCard.setAttribute('data-checkout-method', table.checkout_method);
        } else if (table.has_extra_order) {
            cardClass += ' extra-order';
            console.log(`Table ${table.table_number} has extra order - adding red styling`);
        }
        
        tableCard.className = cardClass;
        tableCard.innerHTML = `
            <div>Table ${table.table_number}</div>
            <div style="font-size: 12px; margin-top: 5px;">Code: ${table.code}</div>
        `;
        
        if (table.status === 'occupied') {
            tableCard.onclick = () => showOrderDetails(table.table_number);
        }
        
        tablesGrid.appendChild(tableCard);
    });
}

async function showOrderDetails(tableNumber) {
    // Switch to live-orders section first
    showSection('live-orders');
    
    try {
        const response = await fetch(`/business/order_details/${tableNumber}`);
        const data = await response.json();
        
        // Find table data for tip information
        const table = tables.find(t => t.table_number === tableNumber);
        
        if (response.ok) {
            currentTableNumber = tableNumber;
            console.log(`Opening modal for table ${tableNumber}`);
            
            document.getElementById('modal-table-number').textContent = tableNumber;
            
            const orderDetailsDiv = document.getElementById('order-details');
            orderDetailsDiv.innerHTML = `
                <p><strong>Order ID:</strong> ${data.order_id}</p>
                <p><strong>Order Time:</strong> ${new Date(data.created_at).toLocaleString()}</p>
                <h3>Items:</h3>
                <div class="order-items">
                    ${data.items.map(item => {
                        let customizationText = '';
                        if (item.customizations) {
                            try {
                                const custom = JSON.parse(item.customizations);
                                const customParts = [];
                                
                                if (custom.ingredients) {
                                    Object.entries(custom.ingredients).forEach(([ing, qty]) => {
                                        if (qty === 0) {
                                            customParts.push(`No ${ing}`);
                                        } else if (qty > 1) {
                                            customParts.push(`Extra ${ing} X${qty}`);
                                        }
                                    });
                                }
                                
                                if (custom.extra && custom.extra.length > 0) {
                                    customParts.push(`Add: ${custom.extra.join(', ')}`);
                                }
                                
                                if (custom.removed && custom.removed.length > 0) {
                                    customParts.push(`No: ${custom.removed.join(', ')}`);
                                }
                                if (custom.added && custom.added.length > 0) {
                                    customParts.push(`Extra: ${custom.added.join(', ')}`);
                                }
                                
                                if (customParts.length > 0) {
                                    customizationText = `<br><small style="color: #666; font-style: italic;">${customParts.join(' | ')}</small>`;
                                }
                            } catch (e) {
                                console.error('Error parsing customizations:', e);
                            }
                        }
                        
                        return `
                            <div class="order-detail-item">
                                <span>
                                    ${item.name} x${item.qty}
                                    ${item.is_new_extra ? '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color: red; font-weight: bold;">NEW</span>' : ''}
                                    ${customizationText}
                                </span>
                                <span>€${item.total.toFixed(2)}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
                <div style="margin-top: 15px; font-size: 18px; font-weight: bold;">
                    Subtotal: €${data.total.toFixed(2)}<br>
                    Tip: €${(table.tip_amount || 0).toFixed(2)}<br>
                    <div style="border-top: 1px solid #ccc; padding-top: 5px; margin-top: 5px;">
                        Total to Charge: €${(data.total + (table.tip_amount || 0)).toFixed(2)}
                    </div>
                </div>
            `;
            
            document.getElementById('checkout-table-btn').setAttribute('data-table', tableNumber);
            document.getElementById('order-modal').style.display = 'block';
        }
    } catch (error) {
        showMessage('Error loading order details', 'error');
    }
}

async function finishTable() {
    const tableNumber = document.getElementById('checkout-table-btn').getAttribute('data-table');
    const waiterId = document.getElementById('waiter-select').value;
    
    if (!waiterId) {
        showMessage('Please select a waiter', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('waiter_id', waiterId);
        
        const response = await fetch(`/business/checkout_table/${tableNumber}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Table checkout completed successfully', 'success');
            closeModal();
            await loadDashboard();
        } else {
            showMessage(data.detail || 'Error processing checkout', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
}

async function loadMenuItems() {
    try {
        const response = await fetch('/business/menu_items');
        const data = await response.json();
        
        if (response.ok) {
            menuItems = data.items;
            displayMenuItems();
        }
    } catch (error) {
        console.error('Error loading menu items:', error);
    }
}

function displayMenuItems() {
    const menuItemsList = document.getElementById('menu-items-list');
    menuItemsList.innerHTML = '';
    
    menuItems.forEach(item => {
        const itemRow = document.createElement('div');
        itemRow.className = 'menu-item-row';
        itemRow.innerHTML = `
            <div class="menu-item-info">
                <div class="menu-item-name">${item.name}</div>
                <div class="menu-item-price">€${item.price.toFixed(2)}</div>
                <div style="font-size: 12px; color: #666;">${item.ingredients}</div>
            </div>
            <button class="toggle-btn ${item.active ? 'active' : 'inactive'}" 
                    onclick="toggleProduct(${item.id})">
                ${item.active ? 'Active' : 'Inactive'}
            </button>
        `;
        menuItemsList.appendChild(itemRow);
    });
}

async function toggleProduct(productId) {
    try {
        const response = await fetch(`/business/toggle_product/${productId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message, 'success');
            loadMenuItems();
        } else {
            showMessage(data.detail || 'Error toggling product', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
}

async function uploadMenu(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('menu-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('Please select a file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('menu_file', file);
    
    try {
        const response = await fetch('/business/menu/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Menu uploaded successfully', 'success');
            fileInput.value = '';
            loadMenuItems();
        } else {
            showMessage(data.detail || 'Error uploading menu', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
}

let currentPeriod = 'day';
let currentDate = new Date().toISOString().split('T')[0];
let currentWaiterId = null;
let showOverall = false;

async function loadSales(period) {
    currentPeriod = period;
    currentDate = new Date().toISOString().split('T')[0];
    
    console.log(`Loading sales for period: ${period}, date: ${currentDate}`);
    try {
        let url = `/business/sales?period=${period}&target_date=${currentDate}`;
        if (currentWaiterId) {
            url += `&waiter_id=${currentWaiterId}`;
        }
        console.log(`Fetching: ${url}`);
        const response = await fetch(url);
        const data = await response.json();
        console.log(`Sales data received:`, data);
        
        if (response.ok) {
            displaySalesData(data);
            updatePeriodButtons(period);
            loadTopItems();
        }
    } catch (error) {
        console.error('Error loading sales:', error);
    }
}

async function loadTopItems() {
    try {
        const response = await fetch(`/business/top-menu-items?period=day&limit=5`);
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            const container = document.getElementById('top-items-list');
            container.innerHTML = data.items.map((item, index) => `
                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee;">
                    <div>
                        <span style="color: #007bff; font-weight: bold;">#${index + 1}</span>
                        <span style="margin-left: 8px;">${item.name}</span>
                    </div>
                    <div style="text-align: right; font-size: 12px;">
                        <div><strong>${item.quantity}</strong> sold</div>
                        <div style="color: #666;">€${item.revenue.toFixed(2)}</div>
                    </div>
                </div>
            `).join('');
        } else {
            document.getElementById('top-items-list').innerHTML = '<p style="color: #666; font-size: 12px; margin: 0;">No sales data yet</p>';
        }
    } catch (error) {
        console.error('Error loading top items:', error);
        document.getElementById('top-items-list').innerHTML = '<p style="color: #666; font-size: 12px; margin: 0;">Error loading data</p>';
    }
}

function displaySalesData(data) {
    const summaryDiv = document.getElementById('sales-summary');
    const tableSalesDiv = document.getElementById('table-sales');
    
    summaryDiv.innerHTML = `
        <div class="sales-summary-cards">
            <div class="summary-card">
                <h4>💰 Total Sales</h4>
                <div class="summary-value">€${data.summary.total_sales.toFixed(2)}</div>
            </div>
            <div class="summary-card">
                <h4>🎯 Total Orders</h4>
                <div class="summary-value">${data.summary.total_orders}</div>
            </div>
            <div class="summary-card">
                <h4>💡 Total Tips</h4>
                <div class="summary-value">€${data.summary.total_tips.toFixed(2)}</div>
            </div>
        </div>
    `;
    
    if (data.waiters && data.waiters.length > 0) {
        tableSalesDiv.innerHTML = `
            <h4>👨🍳 Waiter Performance</h4>
            <div class="table-sales-grid">
                ${data.waiters.map(waiter => `
                    <div class="table-sale-card waiter-summary">
                        <div class="table-sale-header">${waiter.name}</div>
                        <div class="table-sale-stats">
                            <div>Orders: ${waiter.total_orders}</div>
                            <div>Sales: €${waiter.total_sales.toFixed(2)}</div>
                            <div>Tips: €${waiter.total_tips.toFixed(2)}</div>
                            <div>Avg: €${waiter.avg_order_value.toFixed(2)}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
}

function updatePeriodButtons(activePeriod) {
    document.querySelectorAll('.period-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`${activePeriod}-btn`).classList.add('active');
}

function showSection(sectionName) {
    console.log('Showing section:', sectionName);
    currentSection = sectionName;
    
    document.querySelectorAll('.section-content').forEach(section => {
        section.style.display = 'none';
    });
    
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(sectionName).style.display = 'block';
    document.getElementById(sectionName + '-btn').classList.add('active');
    
    // Clear notifications when viewing live orders
    if (sectionName === 'live-orders') {
        console.log('Clearing notifications - switched to live orders');
        clearNotifications();
        loadDashboard();
    } else if (sectionName === 'analytics') {
        loadSales(currentPeriod);
        loadTopItems();
    } else if (sectionName === 'menu-management') {
        loadMenuItems();
    } else if (sectionName === 'waiters-new') {
        loadWaiters();
    }
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = message;
    messageDiv.className = type;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

async function loadWaiters() {
    try {
        const response = await fetch('/business/waiters');
        const data = await response.json();
        
        if (response.ok) {
            showWaiters(data.waiters);
        }
    } catch (error) {
        console.error('Error:', error);
        showWaiters([]);
    }
}

function showWaiters(waiters) {
    const container = document.getElementById('waiters-container');
    
    if (waiters.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 20px; background: #f7fafc; border-radius: 8px;">No waiters yet. Add one above!</p>';
        return;
    }
    
    container.innerHTML = waiters.map(w => `
        <div style="background: white; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; border: 2px solid #e2e8f0;">
            <span style="font-weight: 600; color: #2d3748;">${w.name}</span>
            <button onclick="removeWaiter(${w.id})" style="background: #e53e3e; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer;">Delete</button>
        </div>
    `).join('');
}

async function addWaiter() {
    const input = document.getElementById('waiter-input');
    const name = input.value.trim();
    
    if (!name) {
        alert('Please enter a name');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('name', name);
        
        const response = await fetch('/business/waiters', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            input.value = '';
            loadWaiters();
            loadWaitersForModal();
            showMessage('Waiter added!', 'success');
        }
    } catch (error) {
        alert('Error adding waiter');
    }
}

async function removeWaiter(id) {
    if (!confirm('Delete this waiter?')) return;
    
    try {
        const response = await fetch(`/business/waiters/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadWaiters();
            loadWaitersForModal();
            showMessage('Waiter deleted!', 'success');
        }
    } catch (error) {
        alert('Error deleting waiter');
    }
}

async function loadWaitersForModal() {
    try {
        const response = await fetch('/business/waiters');
        const data = await response.json();
        
        if (response.ok) {
            const select = document.getElementById('waiter-select');
            select.innerHTML = '<option value="">Choose waiter...</option>';
            data.waiters.forEach(waiter => {
                const option = document.createElement('option');
                option.value = waiter.id;
                option.textContent = waiter.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading waiters for modal:', error);
    }
}

function updateNotificationBadge() {
    const liveOrdersBtn = document.getElementById('live-orders-btn');
    
    console.log(`Updating notifications: hasNotifications=${notificationCount > 0}, section=${currentSection}`);
    
    if (notificationCount > 0 && currentSection !== 'live-orders') {
        liveOrdersBtn.classList.add('has-notifications');
        console.log('Button blinking started');
    } else {
        liveOrdersBtn.classList.remove('has-notifications');
        console.log('Button blinking stopped');
    }
}

function clearNotifications() {
    console.log('Clearing all notifications');
    notificationCount = 0;
    const liveOrdersBtn = document.getElementById('live-orders-btn');
    liveOrdersBtn.classList.remove('has-notifications');
}