// Advanced Analytics Dashboard JavaScript
class AnalyticsDashboard {
    constructor() {
        this.currentPeriod = 'day';
        this.currentDate = new Date().toISOString().split('T')[0];
        this.charts = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
    }

    setupEventListeners() {
        // Period selector
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.currentPeriod = e.target.dataset.period;
                this.updatePeriodButtons();
                this.loadDashboard();
            });
        });

        // Date picker
        const datePicker = document.getElementById('analytics-date');
        if (datePicker) {
            datePicker.addEventListener('change', (e) => {
                this.currentDate = e.target.value;
                this.loadDashboard();
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-analytics');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadDashboard());
        }
    }

    updatePeriodButtons() {
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.period === this.currentPeriod);
        });
    }

    async loadDashboard() {
        try {
            this.showLoading();
            
            // Load all analytics data
            const [topItems, categories, dashboard] = await Promise.all([
                this.fetchTopItems(),
                this.fetchCategories(),
                this.fetchDashboard()
            ]);

            this.renderTopItems(topItems);
            this.renderCategories(categories);
            this.renderSummary(dashboard.summary);
            this.renderTrends(dashboard.trends);
            
            this.hideLoading();
        } catch (error) {
            console.error('Analytics loading error:', error);
            this.showError('Failed to load analytics data');
        }
    }

    async fetchTopItems() {
        const response = await fetch(`/business/analytics/top-items?period=${this.currentPeriod}&target_date=${this.currentDate}&limit=10`);
        return await response.json();
    }

    async fetchCategories() {
        const response = await fetch(`/business/analytics/categories?period=${this.currentPeriod}&target_date=${this.currentDate}`);
        return await response.json();
    }

    async fetchDashboard() {
        const response = await fetch(`/business/analytics/dashboard?period=${this.currentPeriod}&target_date=${this.currentDate}`);
        return await response.json();
    }

    renderTopItems(data) {
        const container = document.getElementById('top-items-list');
        if (!container || !data.top_items) return;

        container.innerHTML = data.top_items.map((item, index) => `
            <div class="top-item-card" onclick="analytics.showItemDetails('${item.name}')">
                <div class="item-rank">#${index + 1}</div>
                <div class="item-info">
                    <h4>${item.name}</h4>
                    <span class="item-category">${item.category}</span>
                </div>
                <div class="item-stats">
                    <div class="stat">
                        <span class="stat-value">${item.quantity_sold}</span>
                        <span class="stat-label">Sold</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">€${item.revenue.toFixed(2)}</span>
                        <span class="stat-label">Revenue</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">${item.orders_appeared_in}</span>
                        <span class="stat-label">Orders</span>
                    </div>
                </div>
            </div>
        `).join('');

        // Update summary
        const summaryEl = document.getElementById('top-items-summary');
        if (summaryEl && data.summary) {
            summaryEl.innerHTML = `
                <div class="summary-stat">
                    <span class="summary-value">${data.summary.total_orders}</span>
                    <span class="summary-label">Total Orders</span>
                </div>
                <div class="summary-stat">
                    <span class="summary-value">€${data.summary.total_revenue.toFixed(2)}</span>
                    <span class="summary-label">Total Revenue</span>
                </div>
                <div class="summary-stat">
                    <span class="summary-value">${data.summary.unique_items_sold}</span>
                    <span class="summary-label">Unique Items</span>
                </div>
            `;
        }
    }

    renderCategories(data) {
        const container = document.getElementById('categories-chart');
        if (!container || !data.categories) return;

        // Create pie chart for categories
        const ctx = container.getContext('2d');
        
        if (this.charts.categories) {
            this.charts.categories.destroy();
        }

        this.charts.categories = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.categories.map(cat => cat.category),
                datasets: [{
                    data: data.categories.map(cat => cat.revenue),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const category = data.categories[context.dataIndex];
                                return `${category.category}: €${category.revenue.toFixed(2)} (${category.revenue_percentage.toFixed(1)}%)`;
                            }
                        }
                    }
                }
            }
        });

        // Update categories table
        const tableContainer = document.getElementById('categories-table');
        if (tableContainer) {
            tableContainer.innerHTML = `
                <table class="analytics-table">
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Items Sold</th>
                            <th>Revenue</th>
                            <th>% of Total</th>
                            <th>Avg Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.categories.map(cat => `
                            <tr>
                                <td><strong>${cat.category}</strong></td>
                                <td>${cat.quantity_sold}</td>
                                <td>€${cat.revenue.toFixed(2)}</td>
                                <td>${cat.revenue_percentage.toFixed(1)}%</td>
                                <td>€${cat.avg_item_price.toFixed(2)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    }

    renderSummary(summary) {
        const elements = {
            'total-orders': summary.total_orders,
            'total-sales': `€${summary.total_sales.toFixed(2)}`,
            'total-tips': `€${summary.total_tips.toFixed(2)}`,
            'avg-order-value': `€${(summary.total_sales / Math.max(summary.total_orders, 1)).toFixed(2)}`
        };

        Object.entries(elements).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        });
    }

    renderTrends(trends) {
        const container = document.getElementById('trends-chart');
        if (!container || !trends) return;

        const ctx = container.getContext('2d');
        
        if (this.charts.trends) {
            this.charts.trends.destroy();
        }

        this.charts.trends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: trends.map(t => new Date(t.date).toLocaleDateString()),
                datasets: [{
                    label: 'Orders',
                    data: trends.map(t => t.orders),
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    yAxisID: 'y'
                }, {
                    label: 'Revenue (€)',
                    data: trends.map(t => t.revenue),
                    borderColor: '#FF6384',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'Orders' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'Revenue (€)' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }

    async showItemDetails(itemName) {
        try {
            const response = await fetch(`/business/analytics/item-trends/${encodeURIComponent(itemName)}?days=30`);
            const data = await response.json();
            
            this.openModal('Item Performance Details', this.renderItemModal(data));
        } catch (error) {
            console.error('Error loading item details:', error);
        }
    }

    renderItemModal(data) {
        return `
            <div class="item-modal-content">
                <h3>${data.item_name} - 30 Day Performance</h3>
                <div class="item-summary">
                    <div class="summary-grid">
                        <div class="summary-item">
                            <span class="summary-value">${data.summary.total_quantity}</span>
                            <span class="summary-label">Total Sold</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-value">€${data.summary.total_revenue.toFixed(2)}</span>
                            <span class="summary-label">Total Revenue</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-value">${data.summary.active_days}</span>
                            <span class="summary-label">Active Days</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-value">${data.summary.avg_daily_quantity.toFixed(1)}</span>
                            <span class="summary-label">Avg Daily Sales</span>
                        </div>
                    </div>
                </div>
                <canvas id="item-trend-chart" width="400" height="200"></canvas>
            </div>
        `;
    }

    openModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'analytics-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Close modal events
        modal.querySelector('.modal-close').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }

    showLoading() {
        const loader = document.getElementById('analytics-loader');
        if (loader) loader.style.display = 'block';
    }

    hideLoading() {
        const loader = document.getElementById('analytics-loader');
        if (loader) loader.style.display = 'none';
    }

    showError(message) {
        const errorEl = document.getElementById('analytics-error');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }
        this.hideLoading();
    }
}

// Initialize analytics dashboard
let analytics;
document.addEventListener('DOMContentLoaded', () => {
    analytics = new AnalyticsDashboard();
});