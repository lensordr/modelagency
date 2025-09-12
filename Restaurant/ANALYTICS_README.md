# Advanced Analytics System

## Overview
Comprehensive analytics system for restaurant management with top items tracking, performance optimization, and detailed reporting.

## Data Collection

### Analytics Records
Each checkout creates detailed analytics records with:
- **Order Details**: Checkout timestamp, table number, waiter ID
- **Product Information**: Item name, category, quantity, unit price, total price
- **Financial Data**: Revenue per item, tip allocation
- **Metadata**: Waiter assignments, order relationships

### Database Schema
```sql
CREATE TABLE analytics_records (
    id INTEGER PRIMARY KEY,
    checkout_date DATETIME NOT NULL,
    table_number INTEGER NOT NULL,
    waiter_id INTEGER,
    item_name TEXT NOT NULL,
    item_category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    tip_amount REAL DEFAULT 0
);
```

## Analytics Features

### 1. Top Items Analysis
**Endpoint**: `/business/analytics/top-items`

**Parameters**:
- `period`: "day", "week", "month"
- `target_date`: YYYY-MM-DD format
- `limit`: Number of items to return (default: 10)

**Metrics Provided**:
- Quantity sold
- Total revenue
- Orders appeared in
- Average price
- Average revenue per order

**SQL Logic**:
```sql
SELECT 
    item_name,
    item_category,
    SUM(quantity) as total_quantity,
    SUM(total_price) as total_revenue,
    COUNT(DISTINCT checkout_date) as orders_count,
    AVG(unit_price) as avg_price
FROM analytics_records 
WHERE DATE(checkout_date) BETWEEN start_date AND end_date
GROUP BY item_name, item_category
ORDER BY SUM(quantity) DESC
```

### 2. Item Performance Trends
**Endpoint**: `/business/analytics/item-trends/{item_name}`

**Parameters**:
- `item_name`: Specific item to analyze
- `days`: Number of days to analyze (default: 30)

**Features**:
- Daily sales trends
- Revenue patterns
- Active selling days
- Performance summaries

### 3. Category Comparison
**Endpoint**: `/business/analytics/categories`

**Metrics**:
- Revenue by category
- Quantity sold per category
- Category performance percentages
- Average item prices
- Unique items per category

### 4. Dashboard Analytics
**Endpoint**: `/business/analytics/dashboard`

**Comprehensive View**:
- Summary statistics
- Top 10 items
- Category breakdown
- 7-day trends
- Waiter performance

## Performance Optimization

### Database Indexes
```sql
-- Date-based queries (most common)
CREATE INDEX idx_analytics_checkout_date ON analytics_records(checkout_date);

-- Item analysis
CREATE INDEX idx_analytics_item_date ON analytics_records(item_name, checkout_date);

-- Category analysis  
CREATE INDEX idx_analytics_category_date ON analytics_records(item_category, checkout_date);

-- Waiter performance
CREATE INDEX idx_analytics_waiter_date ON analytics_records(waiter_id, checkout_date);

-- Top items queries
CREATE INDEX idx_analytics_quantity_date ON analytics_records(quantity, checkout_date DESC);
```

### Summary Tables
Pre-aggregated tables for faster queries:

1. **daily_analytics_summary**: Daily totals
2. **item_daily_summary**: Item performance by day
3. **category_daily_summary**: Category performance by day

### Data Archiving
- Archive records older than 365 days
- Maintain performance with large datasets
- Preserve historical data in archive tables

### Query Optimization
- Use date ranges instead of full table scans
- Leverage composite indexes
- Pre-calculate common aggregations
- Batch update summary tables

## Visualization Dashboard

### Charts and Graphs
- **Pie Charts**: Category revenue distribution
- **Line Charts**: Sales trends over time
- **Bar Charts**: Top items comparison
- **Doughnut Charts**: Category breakdowns

### Interactive Features
- Period selection (day/week/month)
- Date picker for specific periods
- Item detail modals with trends
- Export functionality (CSV)

### Key Performance Indicators (KPIs)
- Total orders
- Total revenue
- Average order value
- Top performing items
- Category performance
- Waiter efficiency

## API Endpoints

### Core Analytics
```
GET /business/analytics/dashboard
GET /business/analytics/top-items
GET /business/analytics/item-trends/{item_name}
GET /business/analytics/categories
```

### Export Functions
```
GET /business/analytics/export/csv
GET /business/sales/download/csv
GET /business/sales/download/excel
```

### Dashboard Access
```
GET /business/analytics (HTML page)
```

## Usage Examples

### Get Top Items for Current Month
```javascript
fetch('/business/analytics/top-items?period=month&limit=20')
  .then(response => response.json())
  .then(data => {
    console.log('Top items:', data.top_items);
    console.log('Summary:', data.summary);
  });
```

### Analyze Item Performance
```javascript
fetch('/business/analytics/item-trends/Pizza Margherita?days=30')
  .then(response => response.json())
  .then(data => {
    console.log('Daily trends:', data.daily_trends);
    console.log('Summary stats:', data.summary);
  });
```

### Category Analysis
```javascript
fetch('/business/analytics/categories?period=week')
  .then(response => response.json())
  .then(data => {
    data.categories.forEach(cat => {
      console.log(`${cat.category}: €${cat.revenue} (${cat.revenue_percentage}%)`);
    });
  });
```

## Performance Considerations

### For Large Datasets
1. **Indexing**: Ensure proper indexes are created
2. **Archiving**: Regular data archiving (run monthly)
3. **Summary Tables**: Update daily summaries nightly
4. **Query Limits**: Use LIMIT clauses for large result sets
5. **Caching**: Consider Redis for frequently accessed data

### Optimization Commands
```python
# Setup optimization
python database_optimization.py

# Update daily summaries
from database_optimization import update_daily_summaries
update_daily_summaries()

# Archive old data
from database_optimization import archive_old_data
archive_old_data(days_to_keep=365)
```

## Monitoring and Maintenance

### Database Statistics
```python
from database_optimization import get_database_stats
stats = get_database_stats()
print(f"Analytics records: {stats.get('analytics_records', 0)}")
print(f"Indexes: {stats.get('indexes', [])}")
```

### Regular Maintenance Tasks
1. **Daily**: Update summary tables
2. **Weekly**: Analyze query performance
3. **Monthly**: Archive old data
4. **Quarterly**: Review and optimize indexes

## Security Considerations
- All analytics endpoints require authentication
- Data export functions include user verification
- Sensitive data is aggregated, not exposed individually
- Rate limiting on expensive queries

## Future Enhancements
- Real-time analytics with WebSocket updates
- Machine learning for demand forecasting
- Advanced filtering and segmentation
- Custom report builder
- Mobile analytics dashboard
- Integration with external BI tools