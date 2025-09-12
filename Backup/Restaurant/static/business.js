let tables = [];
let menuItems = [];

// Sound alerts
const newOrderSound = new Audio('/static/sounds/new-order.mp3');
const checkoutSound = new Audio('/static/sounds/checkout-request.mp3');

// Track previous state for sound alerts
let previousTables = [];

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    document.getElementById('date-picker').value = new Date().toISOString().split('T')[0];
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
});

let currentTableNumber = null;

async function closeModal() {
    const modal = document.getElementById('order-modal');
    
    // Mark order as viewed when closing modal
    if (currentTableNumber) {
        try {
            console.log(`Marking table ${currentTableNumber} as viewed`);
            const response = await fetch(`/business/mark_viewed/${currentTableNumber}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
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

function checkAuth() {
    // Check if we have a real access token from login
    const token = localStorage.getItem('access_token');
    if (!token) {
        // Redirect to login if no token
        window.location.href = '/business/login';
        return;
    }
    
    // Initialize app
    loadDashboard();
    loadMenuItems();
    loadSales('day');
    loadWaiters();
}

function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('role');
    window.location.href = '/business/login';
}

async function loadDashboard() {
    try {
        const response = await fetch('/business/dashboard', {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
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
            }
            
            // Check for checkout requests
            if (currentTable.checkout_requested && !previousTable.checkout_requested) {
                try {
                    checkoutSound.play().catch(e => console.log('Sound play failed:', e));
                } catch (e) {
                    console.log('Sound not available');
                }
            }
        }
    });
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
        const response = await fetch(`/business/order_details/${tableNumber}`, {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const data = await response.json();
        
        // Find table data for tip information
        const table = tables.find(t => t.table_number === tableNumber);
        
        if (response.ok) {
            currentTableNumber = tableNumber;
            console.log(`Opening modal for table ${tableNumber}`);
            console.log('All items:', data.items);
            console.log('Items with new_extra status:', data.items.filter(item => item.is_new_extra));
            console.log('Items that should be red:', data.items.map(item => ({
                name: item.name,
                is_new_extra: item.is_new_extra,
                css_class: item.is_new_extra ? 'new-extra-item' : (item.is_extra_item ? 'extra-item' : '')
            })));
            
            document.getElementById('modal-table-number').textContent = tableNumber;
            
            const orderDetailsDiv = document.getElementById('order-details');
            orderDetailsDiv.innerHTML = `
                <p><strong>Order ID:</strong> ${data.order_id}</p>
                <p><strong>Order Time:</strong> ${new Date(data.created_at).toLocaleString()}</p>
                <h3>Items:</h3>
                <div class="order-items">
                    ${data.items.map(item => {
                        console.log(`Item ${item.name}: is_new_extra=${item.is_new_extra}, is_extra_item=${item.is_extra_item}`);
                        
                        let customizationText = '';
                        if (item.customizations) {
                            try {
                                const custom = JSON.parse(item.customizations);
                                const customParts = [];
                                
                                // Handle new ingredient quantity format
                                if (custom.ingredients) {
                                    Object.entries(custom.ingredients).forEach(([ing, qty]) => {
                                        if (qty === 0) {
                                            customParts.push(`No ${ing}`);
                                        } else if (qty > 1) {
                                            customParts.push(`Extra ${ing} X${qty}`);
                                        }
                                    });
                                }
                                
                                // Handle extra ingredients
                                if (custom.extra && custom.extra.length > 0) {
                                    customParts.push(`Add: ${custom.extra.join(', ')}`);
                                }
                                
                                // Handle old format for backward compatibility
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
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
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
        const response = await fetch('/business/menu_items', {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
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
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message, 'success');
            loadMenuItems(); // Refresh menu items
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
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Menu uploaded successfully', 'success');
            fileInput.value = '';
            loadMenuItems(); // Refresh menu items
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
    try {
        let url = `/business/sales?period=${period}&target_date=${currentDate}`;
        if (currentWaiterId) {
            url += `&waiter_id=${currentWaiterId}`;
        }
        const response = await fetch(url, {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            displaySalesData(data);
            updatePeriodButtons(period);
        }
    } catch (error) {
        console.error('Error loading sales:', error);
    }
}

async function loadSalesForDate() {
    currentDate = document.getElementById('date-picker').value;
    loadSales(currentPeriod);
}

async function loadSalesWithFilters() {
    const waiterSelect = document.getElementById('waiter-filter');
    currentWaiterId = waiterSelect.value || null;
    loadSales(currentPeriod);
}

function toggleOverallView() {
    showOverall = !showOverall;
    const btn = document.getElementById('overall-btn');
    btn.textContent = showOverall ? 'Show By Table' : 'Show Overall';
    btn.classList.toggle('active', showOverall);
    loadSales(currentPeriod);
}

async function loadWaitersForFilter() {
    try {
        const response = await fetch('/business/waiters', {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            const select = document.getElementById('waiter-filter');
            select.innerHTML = '<option value="">All Waiters</option>';
            data.waiters.forEach(waiter => {
                const option = document.createElement('option');
                option.value = waiter.id;
                option.textContent = waiter.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading waiters for filter:', error);
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
        <div class="download-buttons" style="margin-top: 1rem; text-align: center;">
            <button onclick="downloadCSV()" style="margin-right: 10px; background: #38a169;">📊 Download CSV</button>
            <button onclick="downloadExcel()" style="background: #2b6cb0;">📈 Download Excel</button>
        </div>
    `;
    
    if (data.table_sales.length === 0) {
        tableSalesDiv.innerHTML = '<p style="text-align: center; color: #718096;">No sales data for this period</p>';
        return;
    }
    
    if (showOverall) {
        // Group by waiter for overall view
        const waiterTotals = {};
        data.table_sales.forEach(sale => {
            const waiter = sale.waiter_name || 'Unknown';
            if (!waiterTotals[waiter]) {
                waiterTotals[waiter] = { orders: 0, sales: 0, tips: 0, checkouts: 0 };
            }
            waiterTotals[waiter].orders += 1; // Each record is one order
            waiterTotals[waiter].sales += sale.total_sales;
            waiterTotals[waiter].tips += sale.total_tips;
            waiterTotals[waiter].checkouts += 1; // Each record is one checkout
        });
        
        tableSalesDiv.innerHTML = `
            <h4>👨‍🍳 Sales by Waiter</h4>
            <div class="table-sales-grid">
                ${Object.entries(waiterTotals).map(([waiter, totals]) => `
                    <div class="table-sale-card waiter-summary">
                        <div class="table-sale-header">${waiter}</div>
                        <div class="table-sale-stats">
                            <div>Checkouts: ${totals.checkouts}</div>
                            <div>Orders: ${totals.orders}</div>
                            <div>Sales: €${totals.sales.toFixed(2)}</div>
                            <div>Tips: €${totals.tips.toFixed(2)}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        tableSalesDiv.innerHTML = `
            <h4>📊 Sales by Order</h4>
            <div class="table-sales-grid">
                ${data.table_sales.map(sale => `
                    <div class="table-sale-card">
                        <div class="table-sale-header">Table ${sale.table_number}</div>
                        <div class="waiter-info">Waiter: ${sale.waiter_name}</div>
                        <div class="table-sale-stats">
                            <div>Order ID: ${sale.order_id}</div>
                            <div>Sales: €${sale.total_sales.toFixed(2)}</div>
                            <div>Tips: €${sale.total_tips.toFixed(2)}</div>
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
    // Hide all sections
    document.querySelectorAll('.section-content').forEach(section => {
        section.style.display = 'none';
    });
    
    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionName).style.display = 'block';
    document.getElementById(sectionName + '-btn').classList.add('active');
    
    // Load data based on section
    if (sectionName === 'live-orders') {
        loadDashboard();
    } else if (sectionName === 'analytics') {
        loadWaitersForFilter();
        loadSales(currentPeriod);
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
// Simple waiter functions
async function loadWaiters() {
    try {
        const response = await fetch('/business/waiters', {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
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
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
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
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
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

async function downloadCSV() {
    let url = `/business/sales/download/csv?period=${currentPeriod}&target_date=${currentDate}`;
    if (currentWaiterId) {
        url += `&waiter_id=${currentWaiterId}`;
    }
    
    try {
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = `sales_${currentPeriod}_${currentDate}.csv`;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(downloadUrl);
        }
    } catch (error) {
        console.error('Error downloading CSV:', error);
    }
}

async function downloadExcel() {
    let url = `/business/sales/download/excel?period=${currentPeriod}&target_date=${currentDate}`;
    if (currentWaiterId) {
        url += `&waiter_id=${currentWaiterId}`;
    }
    
    try {
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = `sales_${currentPeriod}_${currentDate}.xlsx`;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(downloadUrl);
        }
    } catch (error) {
        console.error('Error downloading Excel:', error);
    }
}

// Keep modal loading function
async function loadWaitersForModal() {
    try {
        const response = await fetch('/business/waiters', {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
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
