from sqlalchemy.orm import Session
from models import Table, MenuItem, Order, OrderItem, Waiter, User
from datetime import datetime, date
from sqlalchemy import func, extract
from auth import get_password_hash

# Table operations
def get_all_tables(db: Session):
    return db.query(Table).all()

def get_table_by_number(db: Session, table_number: int):
    return db.query(Table).filter(Table.table_number == table_number).first()

def update_table_status(db: Session, table_number: int, status: str):
    table = get_table_by_number(db, table_number)
    if table:
        table.status = status
        db.commit()
        db.refresh(table)
    return table

# Menu operations
def get_active_menu_items(db: Session):
    return db.query(MenuItem).filter(MenuItem.active == True).order_by(MenuItem.category, MenuItem.name).all()

def get_menu_items_by_category(db: Session, include_inactive: bool = False):
    if include_inactive:
        items = db.query(MenuItem).order_by(MenuItem.category, MenuItem.name).all()
    else:
        items = db.query(MenuItem).filter(MenuItem.active == True).order_by(MenuItem.category, MenuItem.name).all()
    categories = {}
    for item in items:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append(item)
    return categories

def get_menu_item_by_id(db: Session, item_id: int):
    return db.query(MenuItem).filter(MenuItem.id == item_id).first()

def toggle_menu_item_active(db: Session, item_id: int):
    item = get_menu_item_by_id(db, item_id)
    if item:
        item.active = not item.active
        db.commit()
        db.refresh(item)
    return item

def create_menu_item(db: Session, name: str, ingredients: str, price: float, category: str = 'Food'):
    item = MenuItem(name=name, ingredients=ingredients, price=price, category=category)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# Order operations
def create_order(db: Session, table_number: int, items: list):
    order = Order(table_number=table_number)
    db.add(order)
    db.commit()
    db.refresh(order)
    
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            qty=item['qty'],
            customizations=item.get('customizations')
        )
        db.add(order_item)
    
    db.commit()
    return order

def add_items_to_order(db: Session, order_id: int, items: list):
    print(f"Adding items to order {order_id}: {items}")
    
    for item in items:
        # Always add as separate entry for extra orders to avoid mistakes
        print(f"Adding new extra item {item['product_id']} with qty {item['qty']}")
        order_item = OrderItem(
            order_id=order_id,
            product_id=item['product_id'],
            qty=item['qty'],
            is_extra_item=True,
            is_new_extra=True,
            customizations=item.get('customizations')
        )
        db.add(order_item)
        print(f"Added new item with is_new_extra=True")
    
    db.commit()
    print(f"Committed changes to order {order_id}")

def get_active_order_by_table(db: Session, table_number: int):
    return db.query(Order).filter(
        Order.table_number == table_number,
        Order.status == 'active'
    ).first()

def finish_order(db: Session, table_number: int):
    order = get_active_order_by_table(db, table_number)
    if order:
        order.status = 'finished'
        db.commit()
        db.refresh(order)
    return order

def get_order_details(db: Session, table_number: int):
    order = get_active_order_by_table(db, table_number)
    if not order:
        return None
    
    details = {
        'order_id': order.id,
        'table_number': order.table_number,
        'created_at': order.created_at,
        'items': [],
        'total': 0
    }
    
    for order_item in order.order_items:
        item_total = order_item.menu_item.price * order_item.qty
        is_extra = getattr(order_item, 'is_extra_item', False)
        is_new_extra = getattr(order_item, 'is_new_extra', False)
        
        print(f"Item {order_item.menu_item.name}: is_extra_item={is_extra}, is_new_extra={is_new_extra}")
        
        details['items'].append({
            'name': order_item.menu_item.name,
            'price': order_item.menu_item.price,
            'qty': order_item.qty,
            'total': item_total,
            'is_extra_item': is_extra,
            'is_new_extra': is_new_extra,
            'customizations': order_item.customizations
        })
        details['total'] += item_total
    
    return details

# Initialize tables with sample data
def init_sample_data(db: Session):
    # Create tables 1-10 with random 3-digit codes
    table_codes = ['123', '456', '789', '321', '654', '987', '147', '258', '369', '741']
    
    for i in range(1, 11):
        existing_table = get_table_by_number(db, i)
        if not existing_table:
            table = Table(table_number=i, code=table_codes[i-1])
            db.add(table)
    
    # Create sample menu items
    sample_items = [
        {'name': 'Pizza Margherita', 'ingredients': 'Tomato, Mozzarella, Basil', 'price': 12.50, 'category': 'Food'},
        {'name': 'Pasta Carbonara', 'ingredients': 'Pasta, Eggs, Bacon, Parmesan', 'price': 14.00, 'category': 'Food'},
        {'name': 'Caesar Salad', 'ingredients': 'Lettuce, Croutons, Parmesan, Caesar Dressing', 'price': 9.50, 'category': 'Food'},
        {'name': 'Grilled Chicken', 'ingredients': 'Chicken Breast, Herbs, Vegetables', 'price': 16.00, 'category': 'Food'},
        {'name': 'Tiramisu', 'ingredients': 'Mascarpone, Coffee, Ladyfingers', 'price': 6.50, 'category': 'Desserts'}
    ]
    
    for item_data in sample_items:
        existing_item = db.query(MenuItem).filter(MenuItem.name == item_data['name']).first()
        if not existing_item:
            create_menu_item(db, **item_data)
    
    # Only create default admin if no setup was completed
    from setup import is_setup_complete
    if not is_setup_complete():
        existing_admin = get_user_by_username(db, 'admin')
        if not existing_admin:
            create_user(db, 'admin', 'rrares', 'admin')
    
    db.commit()

# Sales analytics functions
def get_sales_by_table_and_period(db: Session, period: str = 'day', target_date: date = None):
    if not target_date:
        target_date = date.today()
    
    query = db.query(
        Order.table_number,
        func.count(Order.id).label('total_orders'),
        func.sum(OrderItem.qty * MenuItem.price).label('total_sales'),
        func.sum(Table.tip_amount).label('total_tips')
    ).join(OrderItem).join(MenuItem).join(Table, Order.table_number == Table.table_number)
    
    if period == 'day':
        query = query.filter(func.date(Order.created_at) == target_date)
    elif period == 'month':
        query = query.filter(
            extract('year', Order.created_at) == target_date.year,
            extract('month', Order.created_at) == target_date.month
        )
    elif period == 'year':
        query = query.filter(extract('year', Order.created_at) == target_date.year)
    
    query = query.filter(Order.status == 'finished')
    query = query.group_by(Order.table_number)
    
    return query.all()

def get_total_sales_summary(db: Session, period: str = 'day', target_date: date = None, waiter_id: int = None):
    if not target_date:
        target_date = date.today()
    
    # Get sales and orders
    sales_query = db.query(
        func.count(func.distinct(Order.id)).label('total_orders'),
        func.sum(OrderItem.qty * MenuItem.price).label('total_sales')
    ).join(OrderItem).join(MenuItem)
    
    if period == 'day':
        sales_query = sales_query.filter(func.date(Order.created_at) == target_date)
    elif period == 'month':
        sales_query = sales_query.filter(
            extract('year', Order.created_at) == target_date.year,
            extract('month', Order.created_at) == target_date.month
        )
    elif period == 'year':
        sales_query = sales_query.filter(extract('year', Order.created_at) == target_date.year)
    
    sales_query = sales_query.filter(Order.status == 'finished')
    
    # Filter by waiter if specified
    if waiter_id:
        sales_query = sales_query.filter(Order.waiter_id == waiter_id)
    
    sales_result = sales_query.first()
    
    # Get tips from finished orders
    tips_query = db.query(
        func.sum(Order.tip_amount).label('total_tips')
    ).filter(Order.status == 'finished')
    
    # Filter by waiter if specified
    if waiter_id:
        tips_query = tips_query.filter(Order.waiter_id == waiter_id)
    
    if period == 'day':
        tips_query = tips_query.filter(func.date(Order.created_at) == target_date)
    elif period == 'month':
        tips_query = tips_query.filter(
            extract('year', Order.created_at) == target_date.year,
            extract('month', Order.created_at) == target_date.month
        )
    elif period == 'year':
        tips_query = tips_query.filter(extract('year', Order.created_at) == target_date.year)
    
    tips_result = tips_query.first()
    
    return {
        'total_orders': sales_result.total_orders or 0,
        'total_sales': float(sales_result.total_sales or 0),
        'total_tips': float(tips_result.total_tips or 0) if tips_result.total_tips else 0.0
    }
# Waiter operations
def get_all_waiters(db: Session):
    return db.query(Waiter).filter(Waiter.active == True).all()

def create_waiter(db: Session, name: str):
    waiter = Waiter(name=name)
    db.add(waiter)
    db.commit()
    db.refresh(waiter)
    return waiter

def delete_waiter(db: Session, waiter_id: int):
    waiter = db.query(Waiter).filter(Waiter.id == waiter_id).first()
    if waiter:
        waiter.active = False
        db.commit()
    return waiter

def finish_order_with_waiter(db: Session, table_number: int, waiter_id: int):
    order = get_active_order_by_table(db, table_number)
    table = get_table_by_number(db, table_number)
    if order and table:
        order.status = 'finished'
        order.waiter_id = waiter_id
        order.tip_amount = table.tip_amount or 0.0
        db.commit()
        db.refresh(order)
    return order

# User operations
def create_user(db: Session, username: str, password: str, role: str = 'waiter'):
    password_hash = get_password_hash(password)
    user = User(username=username, password_hash=password_hash, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username, User.active == True).first()

def get_sales_by_waiter_and_period(db: Session, waiter_id: int, period: str = 'day', target_date: date = None):
    if not target_date:
        target_date = date.today()
    
    query = db.query(
        func.count(func.distinct(Order.id)).label('total_orders'),
        func.sum(OrderItem.qty * MenuItem.price).label('total_sales'),
        func.sum(Order.tip_amount).label('total_tips')
    ).join(OrderItem).join(MenuItem).filter(Order.waiter_id == waiter_id)
    
    if period == 'day':
        query = query.filter(func.date(Order.created_at) == target_date)
    elif period == 'month':
        query = query.filter(
            extract('year', Order.created_at) == target_date.year,
            extract('month', Order.created_at) == target_date.month
        )
    elif period == 'year':
        query = query.filter(extract('year', Order.created_at) == target_date.year)
    
    query = query.filter(Order.status == 'finished')
    result = query.first()
    
    return {
        'waiter_id': waiter_id,
        'total_orders': result.total_orders or 0,
        'total_sales': float(result.total_sales or 0),
        'total_tips': float(result.total_tips or 0)
    }

def get_detailed_sales_data(db: Session, period: str = 'day', target_date: str = None, waiter_id: int = None):
    if not target_date:
        target_date = date.today().isoformat()
    else:
        target_date = date.fromisoformat(target_date)
    
    # Get detailed order data
    query = db.query(
        Order.id.label('order_id'),
        Order.table_number,
        Order.created_at,
        Order.tip_amount.label('total_tips'),
        Waiter.name.label('waiter_name'),
        func.sum(OrderItem.qty * MenuItem.price).label('total_sales')
    ).join(OrderItem).join(MenuItem).outerjoin(Waiter, Order.waiter_id == Waiter.id)
    
    if period == 'day':
        query = query.filter(func.date(Order.created_at) == target_date)
    elif period == 'month':
        query = query.filter(
            extract('year', Order.created_at) == target_date.year,
            extract('month', Order.created_at) == target_date.month
        )
    elif period == 'year':
        query = query.filter(extract('year', Order.created_at) == target_date.year)
    
    query = query.filter(Order.status == 'finished')
    
    if waiter_id:
        query = query.filter(Order.waiter_id == waiter_id)
    
    query = query.group_by(Order.id, Order.table_number, Order.created_at, Order.tip_amount, Waiter.name)
    query = query.order_by(Order.created_at.desc())
    
    orders = query.all()
    
    # Calculate summary
    total_orders = len(orders)
    total_sales = sum(float(order.total_sales or 0) for order in orders)
    total_tips = sum(float(order.total_tips or 0) for order in orders)
    
    return {
        'summary': {
            'total_orders': total_orders,
            'total_sales': total_sales,
            'total_tips': total_tips
        },
        'table_sales': [
            {
                'order_id': order.order_id,
                'table_number': order.table_number,
                'waiter_name': order.waiter_name or 'Unknown',
                'total_sales': float(order.total_sales or 0),
                'total_tips': float(order.total_tips or 0),
                'created_at': order.created_at.isoformat()
            }
            for order in orders
        ]
    }