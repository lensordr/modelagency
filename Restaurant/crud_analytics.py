from sqlalchemy.orm import Session
from models import AnalyticsRecord, Waiter
from datetime import datetime, date, timedelta
from sqlalchemy import func
from typing import Optional

def get_analytics_sales_data(db: Session, period: str = 'day', target_date: str = None, waiter_id: int = None):
    """Get sales data from AnalyticsRecord table (test database)"""
    if not target_date:
        target_date = date.today()
    else:
        target_date = date.fromisoformat(target_date) if isinstance(target_date, str) else target_date
    
    # Calculate date range based on period
    if period == 'day':
        start_date = target_date
        end_date = target_date
    elif period == 'week':
        start_date = target_date - timedelta(days=target_date.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'month':
        start_date = target_date.replace(day=1)
        if target_date.month == 12:
            next_month = target_date.replace(year=target_date.year + 1, month=1)
        else:
            next_month = target_date.replace(month=target_date.month + 1)
        end_date = next_month - timedelta(days=1)
    elif period == 'year':
        start_date = target_date.replace(month=1, day=1)
        end_date = target_date.replace(month=12, day=31)
    else:
        start_date = target_date
        end_date = target_date
    
    # Build query
    query = db.query(AnalyticsRecord).filter(
        func.date(AnalyticsRecord.checkout_date) >= start_date,
        func.date(AnalyticsRecord.checkout_date) <= end_date
    )
    
    # Filter by waiter if specified
    if waiter_id:
        query = query.filter(AnalyticsRecord.waiter_id == waiter_id)
    
    # Get records
    records = query.order_by(AnalyticsRecord.checkout_date.desc()).all()
    
    # Get waiter names
    waiters = {w.id: w.name for w in db.query(Waiter).all()}
    
    # Calculate totals
    total_orders = len(records)
    total_sales = sum(r.total_price for r in records)
    total_tips = sum(r.tip_amount for r in records)
    
    # Format table sales data
    table_sales = []
    for record in records:
        waiter_name = waiters.get(record.waiter_id, f'Waiter {record.waiter_id}')
        table_sales.append({
            'order_id': f'A{record.id}',  # Analytics record ID
            'table_number': record.table_number,
            'waiter_name': waiter_name,
            'total_sales': float(record.total_price),
            'total_tips': float(record.tip_amount),
            'created_at': record.checkout_date.isoformat()
        })
    
    return {
        'summary': {
            'total_orders': total_orders,
            'total_sales': float(total_sales),
            'total_tips': float(total_tips)
        },
        'table_sales': table_sales
    }