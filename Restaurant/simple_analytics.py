from sqlalchemy.orm import Session
from models import Order, OrderItem, MenuItem, Waiter
from sqlalchemy import func, extract
from datetime import date, timedelta

def get_simple_top_items(db: Session, limit: int = 10, target_date: str = None):
    """Simple top items with optional date filtering"""
    try:
        query = db.query(
            MenuItem.id,
            MenuItem.name,
            MenuItem.category,
            MenuItem.price,
            func.sum(OrderItem.qty).label('total_quantity'),
            func.sum(OrderItem.qty * MenuItem.price).label('total_revenue'),
            func.count(func.distinct(Order.id)).label('order_frequency')
        ).select_from(MenuItem).join(OrderItem, MenuItem.id == OrderItem.product_id).join(Order, OrderItem.order_id == Order.id).filter(Order.status == 'finished')
        
        # Add date filter if provided
        if target_date:
            query = query.filter(func.date(Order.created_at) == target_date)
        
        query = query.group_by(MenuItem.id, MenuItem.name, MenuItem.category, MenuItem.price)
        query = query.order_by(func.sum(OrderItem.qty).desc())
        query = query.limit(limit)
        
        return query.all()
    except Exception as e:
        print(f"Error in get_simple_top_items: {e}")
        return []

def get_simple_trends(db: Session, days: int = 7):
    """Simple trends for last N days"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        query = db.query(
            func.date(Order.created_at).label('date'),
            func.count(func.distinct(Order.id)).label('orders'),
            func.sum(OrderItem.qty * MenuItem.price).label('revenue')
        ).join(OrderItem).join(MenuItem).filter(
            Order.status == 'finished',
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at))
        
        return query.all()
    except Exception as e:
        print(f"Error in get_simple_trends: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_simple_categories(db: Session, target_date: str = None):
    """Simple category performance with optional date filtering"""
    try:
        query = db.query(
            MenuItem.category,
            func.sum(OrderItem.qty).label('total_quantity'),
            func.sum(OrderItem.qty * MenuItem.price).label('total_revenue')
        ).join(OrderItem).join(Order).filter(Order.status == 'finished')
        
        # Add date filter if provided
        if target_date:
            query = query.filter(func.date(Order.created_at) == target_date)
        
        query = query.group_by(MenuItem.category)
        query = query.order_by(func.sum(OrderItem.qty * MenuItem.price).desc())
        
        return query.all()
    except Exception as e:
        print(f"Error in get_simple_categories: {e}")
        return []