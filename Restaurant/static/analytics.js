// Advanced Analytics Dashboard
let currentPeriod = 'day';
let currentDate = new Date().toISOString().split('T')[0];

document.addEventListener('DOMContentLoaded', function() {
    // Set default date
    const dateInput = document.getElementById('analytics-date-picker');
    if (dateInput) {
        dateInput.value = currentDate;
    }
});

async function loadAnalyticsDashboard() {
    try {
        const response = await fetch(`/business/analytics/dashboard?target_date=${currentDate}&period=${currentPeriod}&_t=${Date.now()}`);
        
        if (response.ok) {
            const data = await response.json();
            displayDashboardSummary(data);
            displayTopItems(data.top_items);
            displayWaiterPerformance(data.waiters);
        }
    } catch (error) {
        console.error('Error loading analytics dashboard:', error);
    }
}

function displayDashboardSummary(data) {
    const summaryDiv = document.getElementById('analytics-summary');
    if (!summaryDiv) return;
    
    summaryDiv.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-icon">💰</div>
                <div class="kpi-value">€${data.summary.total_sales.toFixed(2)}</div>
                <div class="kpi-label">Total Revenue</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">📋</div>
                <div class="kpi-value">${data.summary.total_orders}</div>
                <div class="kpi-label">Total Orders</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">💡</div>
                <div class="kpi-value">€${data.summary.total_tips.toFixed(2)}</div>
                <div class="kpi-label">Total Tips</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">📊</div>
                <div class="kpi-value">€${(data.summary.total_sales / Math.max(data.summary.total_orders, 1)).toFixed(2)}</div>
                <div class="kpi-label">Avg Order Value</div>
            </div>
        </div>
    `;
}

function displayTopItems(items) {
    const container = document.getElementById('top-items-list');
    if (!container) return;
    
    if (!items || items.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No top items data available</p>';
        return;
    }
    
    container.innerHTML = items.map((item, index) => `
        <div class="top-item-row">
            <div class="item-rank">#${index + 1}</div>
            <div class="item-info">
                <div class="item-name">${item.name}</div>
                <div class="item-category">Food</div>
            </div>
            <div class="item-stats">
                <div class="stat">
                    <span class="stat-value">${item.quantity}</span>
                    <span class="stat-label">Sold</span>
                </div>
                <div class="stat">
                    <span class="stat-value">€${item.revenue.toFixed(2)}</span>
                    <span class="stat-label">Revenue</span>
                </div>
            </div>
        </div>
    `).join('');
}

function displayWaiterPerformance(waiters) {
    const container = document.getElementById('waiter-performance');
    if (!container) return;
    
    if (!waiters || waiters.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No waiter performance data available</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="performance-table">
            <div class="table-header">
                <div>Waiter</div>
                <div>Orders</div>
                <div>Sales</div>
                <div>Tips</div>
                <div>Avg Order</div>
            </div>
            ${waiters.map(waiter => `
                <div class="table-row">
                    <div class="waiter-name">${waiter.name}</div>
                    <div>${waiter.total_orders}</div>
                    <div>€${waiter.total_sales.toFixed(2)}</div>
                    <div>€${waiter.total_tips.toFixed(2)}</div>
                    <div>€${waiter.avg_order_value.toFixed(2)}</div>
                </div>
            `).join('')}
        </div>
    `;
}

function changePeriod(period) {
    currentPeriod = period;
    document.querySelectorAll('.period-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`${period}-btn`).classList.add('active');
    loadAnalyticsDashboard();
}

function changeDate() {
    const datePicker = document.getElementById('analytics-date-picker');
    if (datePicker) {
        currentDate = datePicker.value;
        loadAnalyticsDashboard();
    }
}

function refreshAnalytics() {
    loadAnalyticsDashboard();
}

function initializeAnalytics() {
    loadAnalyticsDashboard();
}