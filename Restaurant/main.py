from fastapi import FastAPI, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
import sys
import os
from datetime import date, timedelta

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from models import create_tables, get_db, MenuItem, Order, OrderItem, Table, Waiter, User  # type: ignore
    from crud import (  # type: ignore
        init_sample_data, get_table_by_number, get_active_menu_items, get_menu_items_by_category,
        create_order, update_table_status, get_all_tables, get_order_details,
        finish_order, toggle_menu_item_active, create_menu_item, get_active_order_by_table, add_items_to_order,
        get_sales_by_table_and_period, get_total_sales_summary, get_all_waiters, create_waiter, delete_waiter, finish_order_with_waiter,
        get_sales_by_waiter_and_period, get_detailed_sales_data
    )
    from auth import authenticate_user, create_access_token, get_current_user, require_admin  # type: ignore
except ImportError as e:
    print(f"Import error: {e}")
    raise

# Initialize sample data
from contextlib import asynccontextmanager
try:
    from setup import is_setup_complete, apply_setup, get_setup_config  # type: ignore
except ImportError as e:
    print(f"Setup import error: {e}")
    raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    
    # Always initialize sample data
    db = next(get_db())
    init_sample_data(db)
    db.close()
    
    if is_setup_complete():
        config = get_setup_config()
        print(f"\nWelcome back to {config.get('restaurant_name', 'TablePulse')}!")
    else:
        print("\nSetup available at /setup - using default data for now")
    
    yield

app = FastAPI(lifespan=lifespan)

# Mount static files and templates
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Add routes to prevent HTTP warnings
@app.get("/favicon.ico")
async def favicon():
    return JSONResponse({"message": "No favicon"}, status_code=204)

@app.get("/robots.txt")
async def robots():
    return JSONResponse({"message": "No robots.txt"}, status_code=204)

@app.get("/apple-touch-icon.png")
async def apple_touch_icon():
    return JSONResponse({"message": "No apple touch icon"}, status_code=204)

def get_restaurant_name():
    config = get_setup_config()
    return config.get('restaurant_name', 'TablePulse Restaurant')

# Setup routes
@app.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    if is_setup_complete():
        return templates.TemplateResponse("setup_complete.html", {"request": request})
    return templates.TemplateResponse("setup.html", {"request": request})

@app.post("/setup")
async def complete_setup(
    restaurant_name: str = Form(...),
    admin_username: str = Form(...),
    admin_password: str = Form(...),
    menu_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        print(f"Setup request received: {restaurant_name}, {admin_username}")
        
        if is_setup_complete():
            print("Setup already completed")
            return JSONResponse({"error": "Setup already completed"}, status_code=400)
        
        config = {
            'restaurant_name': restaurant_name,
            'admin_username': admin_username,
            'admin_password': admin_password
        }
        
        if menu_file and menu_file.filename:
            print(f"Menu file provided: {menu_file.filename}")
            menu_content = await menu_file.read()
            config['menu_file'] = menu_content
            config['menu_filename'] = menu_file.filename
        
        print("Applying setup...")
        apply_setup(config)
        print("Initializing sample data...")
        init_sample_data(db)
        print("Setup completed successfully")
        
        return JSONResponse({"message": "Setup completed successfully!", "redirect": "/business/login"})
    except Exception as e:
        print(f"Setup error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if not is_setup_complete():
        return templates.TemplateResponse("setup.html", {"request": request})
    return templates.TemplateResponse("welcome.html", {"request": request, "restaurant_name": get_restaurant_name()})

# Client routes
@app.get("/client", response_class=HTMLResponse)
async def client_page(request: Request, table: int = None):
    restaurant_name = get_restaurant_name()
    return templates.TemplateResponse("client.html", {
        "request": request, 
        "table_number": table,
        "restaurant_name": restaurant_name
    })

@app.get("/client/menu")
async def get_menu(table: int, db: Session = Depends(get_db)):
    table_obj = get_table_by_number(db, table)
    if not table_obj:
        raise HTTPException(status_code=404, detail="Table not found")
    
    categories = get_menu_items_by_category(db)
    menu_by_category = {}
    for category, items in categories.items():
        menu_by_category[category] = [
            {
                "id": item.id,
                "name": item.name,
                "ingredients": item.ingredients,
                "price": item.price
            }
            for item in items
        ]
    
    response = JSONResponse({
        "table_number": table,
        "table_code": table_obj.code,
        "restaurant_name": get_restaurant_name(),
        "menu": menu_by_category
    })
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/client/order_details/{table_number}")
async def get_client_order_details(table_number: int, db: Session = Depends(get_db)):
    details = get_order_details(db, table_number)
    table = get_table_by_number(db, table_number)
    
    if not details:
        return {"has_order": False}
    
    return {
        "has_order": True, 
        "checkout_requested": table.checkout_requested if table else False,
        **details
    }

@app.post("/client/checkout")
async def request_checkout(
    table_number: int = Form(...),
    checkout_method: str = Form(...),
    tip_amount: float = Form(...),
    db: Session = Depends(get_db)
):
    table = get_table_by_number(db, table_number)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    if table.status != 'occupied':
        raise HTTPException(status_code=400, detail="No active order for this table")
    
    table.checkout_requested = True
    table.checkout_method = checkout_method
    table.tip_amount = tip_amount
    db.commit()
    
    return {"message": f"Checkout requested with {checkout_method} and €{tip_amount:.2f} tip"}

@app.post("/client/order")
async def place_order(
    table_number: int = Form(...),
    code: str = Form(...),
    items: str = Form(...),
    db: Session = Depends(get_db)
):
    table = get_table_by_number(db, table_number)
    if not table or table.code != code:
        raise HTTPException(status_code=400, detail="Invalid table or code")
    
    import json
    try:
        order_items = json.loads(items)
    except:
        raise HTTPException(status_code=400, detail="Invalid items format")
    
    if table.checkout_requested:
        raise HTTPException(status_code=400, detail="Cannot place orders after checkout has been requested. Please wait for staff assistance.")
    
    existing_order = get_active_order_by_table(db, table_number)
    
    if existing_order:
        add_items_to_order(db, existing_order.id, order_items)
        table.has_extra_order = True
        db.commit()
        return {"message": "Items added to existing order", "order_id": existing_order.id}
    else:
        order = create_order(db, table_number, order_items)
        update_table_status(db, table_number, 'occupied')
        return {"message": "Order placed successfully", "order_id": order.id}

# Authentication routes
@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@app.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}

# Business routes
@app.get("/business/login", response_class=HTMLResponse)
async def business_login_page(request: Request):
    return templates.TemplateResponse("business_login.html", {"request": request})



@app.get("/test-login", response_class=HTMLResponse)
async def test_login_page(request: Request):
    with open("test_login.html", "r") as f:
        return HTMLResponse(f.read())

@app.get("/business", response_class=HTMLResponse)
async def business_dashboard(request: Request):
    return templates.TemplateResponse("business.html", {
        "request": request, 
        "user": {"username": "admin", "role": "admin"},
        "restaurant_name": get_restaurant_name()
    })

@app.get("/business/tables")
async def get_tables_status(db: Session = Depends(get_db)):
    tables = get_all_tables(db)
    return [{"number": t.table_number, "status": t.status, "code": t.code, "checkout_requested": t.checkout_requested, "has_extra_order": t.has_extra_order} for t in tables]

@app.get("/business/order/{table_number}")
async def get_business_order_details(table_number: int, db: Session = Depends(get_db)):
    return get_order_details(db, table_number)

@app.post("/business/finish_order")
async def finish_table_order(
    table_number: int = Form(...),
    waiter_id: int = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if waiter_id:
        finish_order_with_waiter(db, table_number, waiter_id)
    else:
        finish_order(db, table_number)
    return {"message": "Order finished successfully"}

@app.get("/business/menu")
async def get_business_menu(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = get_menu_items_by_category(db, include_inactive=True)
    menu_by_category = {}
    for category, items in categories.items():
        menu_by_category[category] = [
            {
                "id": item.id,
                "name": item.name,
                "ingredients": item.ingredients,
                "price": item.price,
                "is_active": item.active
            }
            for item in items
        ]
    return menu_by_category

@app.post("/business/menu/toggle")
async def toggle_menu_item(
    item_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    toggle_menu_item_active(db, item_id)
    return {"message": "Menu item status updated"}

@app.post("/business/menu/add")
async def add_menu_item(
    name: str = Form(...),
    ingredients: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    create_menu_item(db, name, ingredients, price, category)
    return {"message": "Menu item added successfully"}

@app.get("/test")
async def test_route():
    return {"message": "Server is working"}

@app.get("/test-csv")
async def test_csv():
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Test', 'CSV', 'Download'])
    writer.writerow(['This', 'is', 'working'])
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=test.csv"}
    )

@app.post("/business/menu/upload")
async def upload_menu_file(
    menu_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        print(f"Upload request received for file: {menu_file.filename}")
        
        if not menu_file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        file_content = await menu_file.read()
        print(f"File size: {len(file_content)} bytes")
        
        if menu_file.filename.endswith(('.xlsx', '.xls')):
            from setup import process_excel_content
            process_excel_content(db, file_content)
        elif menu_file.filename.endswith('.pdf'):
            from setup import process_pdf_content
            process_pdf_content(db, file_content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use Excel (.xlsx, .xls) or PDF files.")
        
        return {"message": "Menu uploaded successfully"}
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")



@app.get("/business/waiters")
async def get_waiters_list(db: Session = Depends(get_db)):
    waiters = get_all_waiters(db)
    return {"waiters": waiters}

@app.post("/business/waiters/add")
async def add_waiter(
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    create_waiter(db, name)
    return {"message": "Waiter added successfully"}

@app.delete("/business/waiters/{waiter_id}")
async def remove_waiter(waiter_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    delete_waiter(db, waiter_id)
    return {"message": "Waiter removed successfully"}

# Additional endpoints needed by business.js
@app.get("/business/dashboard")
async def get_dashboard_data(db: Session = Depends(get_db)):
    try:
        tables = get_all_tables(db)
        result_tables = []
        
        for table in tables:
            table_data = {
                "table_number": table.table_number,
                "status": table.status,
                "code": table.code,
                "has_extra_order": table.has_extra_order,
                "checkout_requested": table.checkout_requested,
                "checkout_method": table.checkout_method,
                "tip_amount": table.tip_amount
            }
            result_tables.append(table_data)
        
        return {"tables": result_tables}
    except Exception as e:
        print(f"Dashboard error: {e}")
        return {"tables": [], "error": str(e)}

@app.post("/business/mark_viewed/{table_number}")
async def mark_order_viewed(
    table_number: int,
    db: Session = Depends(get_db)
):
    table = get_table_by_number(db, table_number)
    if table:
        table.has_extra_order = False
        
        # Clear is_new_extra flag from all order items for this table
        active_order = get_active_order_by_table(db, table_number)
        if active_order:
            db.query(OrderItem).filter(
                OrderItem.order_id == active_order.id,
                OrderItem.is_new_extra == True
            ).update({OrderItem.is_new_extra: False})
        
        db.commit()
    return {"message": "Order marked as viewed"}

@app.get("/business/order_details/{table_number}")
async def get_order_details_route(table_number: int, db: Session = Depends(get_db)):
    return get_order_details(db, table_number)

@app.post("/business/checkout_table/{table_number}")
async def checkout_table(
    table_number: int,
    waiter_id: int = Form(...),
    db: Session = Depends(get_db)
):
    from models import AnalyticsRecord
    from datetime import datetime
    
    finish_order_with_waiter(db, table_number, waiter_id)
    table = get_table_by_number(db, table_number)
    # Clear table status after checkout
    if table:
        table.status = 'free'
        table.checkout_requested = False
        table.has_extra_order = False
        table.checkout_method = None
        table.tip_amount = 0.0
        db.commit()
    return {"message": "Table checkout completed successfully"}

@app.get("/business/menu_items")
async def get_menu_items_route(db: Session = Depends(get_db)):
    try:
        print("Loading menu items...")
        categories = get_menu_items_by_category(db, include_inactive=True)
        print(f"Found {len(categories)} categories")
        items = []
        for category, category_items in categories.items():
            print(f"Processing category {category} with {len(category_items)} items")
            for item in category_items:
                items.append({
                    "id": item.id,
                    "name": item.name,
                    "ingredients": item.ingredients,
                    "price": item.price,
                    "active": item.active,
                    "category": category
                })
        print(f"Returning {len(items)} total items")
        return {"items": items}
    except Exception as e:
        print(f"Error in menu_items_route: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/business/toggle_product/{item_id}")
async def toggle_product_route(item_id: int, db: Session = Depends(get_db)):
    toggle_menu_item_active(db, item_id)
    return {"message": "Product status updated"}

@app.post("/business/waiters")
async def add_waiter_route(
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    create_waiter(db, name)
    return {"message": "Waiter added successfully"}

@app.get("/business/top-menu-items")
async def get_top_menu_items(
    period: str = "day",
    target_date: str = None,
    limit: int = 5,
    waiter_id: int = None,
    db: Session = Depends(get_db)
):
    from models import Order, OrderItem, MenuItem
    from datetime import datetime, timedelta
    
    if target_date is None:
        from datetime import date
        target_date = date.today().isoformat()
    
    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    
    # Calculate date range
    if period == "day":
        start_date = target_date_obj
        end_date = target_date_obj
    elif period == "week":
        start_date = target_date_obj - timedelta(days=target_date_obj.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == "month":
        start_date = target_date_obj.replace(day=1)
        next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        end_date = next_month - timedelta(days=1)
    else:  # year
        start_date = target_date_obj.replace(month=1, day=1)
        end_date = target_date_obj.replace(month=12, day=31)
    
    # Query top menu items from actual orders
    query = db.query(
        MenuItem.name,
        func.sum(OrderItem.qty).label('total_quantity'),
        func.sum(OrderItem.qty * MenuItem.price).label('total_revenue')
    ).join(OrderItem).join(Order).filter(
        Order.status == 'finished',
        func.date(Order.created_at) >= start_date,
        func.date(Order.created_at) <= end_date
    )
    
    if waiter_id:
        query = query.filter(Order.waiter_id == waiter_id)
    
    top_items = query.group_by(MenuItem.id, MenuItem.name).order_by(
        func.sum(OrderItem.qty).desc()
    ).limit(limit).all()
    
    return {
        'items': [
            {
                'name': item.name,
                'quantity': item.total_quantity,
                'revenue': float(item.total_revenue)
            }
            for item in top_items
        ]
    }

@app.get("/business/sales")
async def get_sales_route(
    period: str = "day",
    target_date: str = None,
    waiter_id: int = None,
    db: Session = Depends(get_db)
):
    if target_date is None:
        from datetime import date
        target_date = date.today().isoformat()
    
    from analytics_service import get_analytics_for_period
    print(f"Sales API: period={period}, target_date={target_date}, waiter_id={waiter_id}")
    result = get_analytics_for_period(db, target_date, period, waiter_id)
    print(f"Sales API result: {result['summary']}")
    return {
        'summary': result['summary'],
        'table_sales': [],  # Business dashboard doesn't need detailed sales list
        'waiters': result.get('waiters', [])  # Include waiter performance data
    }

@app.get("/business/sales/download/csv")
async def download_sales_csv(
    period: str = "day",
    target_date: str = None,
    waiter_id: int = None,
    db: Session = Depends(get_db)
):
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    if target_date is None:
        from datetime import date
        target_date = date.today().isoformat()
    
    try:
        data = get_detailed_sales_data(db, period, target_date, waiter_id)
    except Exception as e:
        print(f"Error getting sales data: {e}")
        data = {'summary': {'total_orders': 0, 'total_sales': 0, 'total_tips': 0}, 'table_sales': []}
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['Order ID', 'Table Number', 'Waiter', 'Sales', 'Tips', 'Date'])
    
    # Write data
    if data.get('table_sales'):
        for order in data['table_sales']:
            writer.writerow([
                order['order_id'],
                order['table_number'],
                order['waiter_name'],
                f"€{order['total_sales']:.2f}",
                f"€{order['total_tips']:.2f}",
                order['created_at']
            ])
    else:
        writer.writerow(['No sales data available for this period', '', '', '', '', ''])
    
    # Write summary
    writer.writerow([])
    writer.writerow(['SUMMARY'])
    writer.writerow(['Total Orders', data['summary']['total_orders']])
    writer.writerow(['Total Sales', f"€{data['summary']['total_sales']:.2f}"])
    writer.writerow(['Total Tips', f"€{data['summary']['total_tips']:.2f}"])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=sales_{period}_{target_date}.csv"}
    )

@app.get("/business/sales/download/excel")
async def download_sales_excel(
    period: str = "day",
    target_date: str = None,
    waiter_id: int = None,
    db: Session = Depends(get_db)
):
    try:
        import pandas as pd
    except ImportError:
        raise HTTPException(status_code=500, detail="Excel export not available")
    import io
    from fastapi.responses import StreamingResponse
    
    if target_date is None:
        from datetime import date
        target_date = date.today().isoformat()
    
    data = get_detailed_sales_data(db, period, target_date, waiter_id)
    
    # Create DataFrame
    df = pd.DataFrame(data['table_sales'])
    if not df.empty:
        df = df[['order_id', 'table_number', 'waiter_name', 'total_sales', 'total_tips', 'created_at']]
        df.columns = ['Order ID', 'Table Number', 'Waiter', 'Sales (€)', 'Tips (€)', 'Date']
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sales Data', index=False)
        
        # Add summary sheet
        summary_df = pd.DataFrame([
            ['Total Orders', data['summary']['total_orders']],
            ['Total Sales (€)', data['summary']['total_sales']],
            ['Total Tips (€)', data['summary']['total_tips']]
        ], columns=['Metric', 'Value'])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=sales_{period}_{target_date}.xlsx"}
    )

@app.get("/business/analytics/dashboard")
async def get_analytics_dashboard(
    target_date: str = None,
    period: str = "day",
    waiter_id: int = None,
    db: Session = Depends(get_db)
):
    try:
        from analytics_service import get_analytics_for_period
        
        if target_date is None:
            from datetime import date
            target_date = date.today().isoformat()
        
        print(f"Analytics Dashboard API: period={period}, target_date={target_date}, waiter_id={waiter_id}")
        result = get_analytics_for_period(db, target_date, period, waiter_id)
        print(f"Analytics Dashboard result: {result['summary']}")
        return result
        
    except Exception as e:
        return {
            "summary": {"total_orders": 0, "total_sales": 0, "total_tips": 0},
            "top_items": [],
            "categories": [],
            "trends": [],
            "waiters": [],
            "error": str(e)
        }

@app.get("/business/analytics/top-items")
async def get_top_items(
    period: str = "day",
    target_date: str = None,
    limit: int = 10,
    waiter_id: int = None,
    db: Session = Depends(get_db)
):
    from analytics_service import get_top_items_by_period
    return get_top_items_by_period(db, period, target_date, limit, waiter_id)

@app.get("/business/analytics/item-trends/{item_name}")
async def get_item_trends(
    item_name: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    from analytics_service import get_item_performance_trends
    return get_item_performance_trends(db, item_name, days)

@app.get("/business/analytics/categories")
async def get_category_analytics(
    period: str = "month",
    target_date: str = None,
    waiter_id: int = None,
    db: Session = Depends(get_db)
):
    from analytics_service import get_category_comparison
    return get_category_comparison(db, period, target_date, waiter_id)

@app.get("/business/analytics")
async def analytics_page(request: Request):
    return templates.TemplateResponse("simple_analytics.html", {"request": request})

@app.get("/business/analytics/export/csv")
async def export_analytics_csv(
    period: str = "month",
    target_date: str = None,
    db: Session = Depends(get_db)
):
    import csv
    import io
    from fastapi.responses import StreamingResponse
    from analytics_service import get_top_items_by_period
    
    if target_date is None:
        from datetime import date
        target_date = date.today().isoformat()
    
    data = get_top_items_by_period(db, period, target_date, 50)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['Rank', 'Item Name', 'Category', 'Quantity Sold', 'Revenue', 'Orders', 'Avg Price', 'Avg Revenue/Order'])
    
    # Write data
    for i, item in enumerate(data['top_items'], 1):
        writer.writerow([
            i,
            item['name'],
            item['category'],
            item['quantity_sold'],
            f"€{item['revenue']:.2f}",
            item['orders_appeared_in'],
            f"€{item['avg_price']:.2f}",
            f"€{item['avg_revenue_per_order']:.2f}"
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=top_items_{period}_{target_date}.csv"}
    )

@app.get("/debug/database")
async def debug_database(period: str = "day", db: Session = Depends(get_db)):
    from models import AnalyticsRecord, Waiter
    from datetime import date
    
    today = date.today()
    
    # Calculate date range based on period
    if period == "day":
        start_date = today
        end_date = today
    elif period == "month":
        start_date = today.replace(day=1)
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1)
        else:
            next_month = today.replace(month=today.month + 1)
        end_date = next_month - timedelta(days=1)
    else:
        start_date = today
        end_date = today
    
    # Get analytics records for the period
    records = db.query(AnalyticsRecord).filter(
        func.date(AnalyticsRecord.checkout_date) >= start_date,
        func.date(AnalyticsRecord.checkout_date) <= end_date
    ).all()
    
    # Get waiter names
    waiters = {w.id: w.name for w in db.query(Waiter).all()}
    
    # Group by waiter
    waiter_stats = {}
    total_sales = 0
    total_tips = 0
    total_orders = len(records)
    
    for record in records:
        waiter_name = waiters.get(record.waiter_id, f'Waiter {record.waiter_id}')
        if waiter_name not in waiter_stats:
            waiter_stats[waiter_name] = {'orders': 0, 'sales': 0, 'tips': 0}
        
        waiter_stats[waiter_name]['orders'] += 1
        waiter_stats[waiter_name]['sales'] += record.total_price
        waiter_stats[waiter_name]['tips'] += record.tip_amount
        
        total_sales += record.total_price
        total_tips += record.tip_amount
    
    return {
        'date': today.isoformat(),
        'total_records': total_orders,
        'total_sales': total_sales,
        'total_tips': total_tips,
        'waiter_breakdown': waiter_stats,
        'raw_records': [
            {
                'waiter': waiters.get(r.waiter_id, f'Waiter {r.waiter_id}'),
                'table': r.table_number,
                'sales': r.total_price,
                'tips': r.tip_amount,
                'date': r.checkout_date.isoformat()
            } for r in records[:10]  # Show first 10 records
        ]
    }

@app.get("/export/sales-csv")
async def export_sales_csv_simple(
    period: str = "day",
    target_date: str = None,
    db: Session = Depends(get_db)
):
    import csv
    import io
    from fastapi.responses import StreamingResponse
    from models import AnalyticsRecord
    from datetime import datetime
    
    if target_date is None:
        from datetime import date
        target_date = date.today().isoformat()
    
    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    
    try:
        print(f"CSV Export: period={period}, target_date={target_date}")
        # Get order data
        data = get_detailed_sales_data(db, period, target_date, None)
        print(f"CSV Export: Found {len(data.get('table_sales', []))} orders")
        
        # Get analytics order count using same period logic as dashboard
        from datetime import timedelta
        
        if period == "day":
            start_date = target_date_obj
            end_date = target_date_obj
        elif period == "week":
            start_date = target_date_obj - timedelta(days=target_date_obj.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == "month":
            start_date = target_date_obj.replace(day=1)
            next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
            end_date = next_month - timedelta(days=1)
        else:  # year
            start_date = target_date_obj.replace(month=1, day=1)
            end_date = target_date_obj.replace(month=12, day=31)
        
        analytics_orders = db.query(
            func.count(func.distinct(AnalyticsRecord.checkout_date))
        ).filter(
            func.date(AnalyticsRecord.checkout_date) >= start_date,
            func.date(AnalyticsRecord.checkout_date) <= end_date
        ).scalar() or 0
        
        # Override order count with analytics count
        data['summary']['total_orders'] = analytics_orders
        
        # If analytics shows fewer orders, limit the CSV data to match
        if analytics_orders < len(data.get('table_sales', [])):
            # Keep only the most recent orders to match analytics count
            data['table_sales'] = data['table_sales'][:analytics_orders]
        
    except Exception as e:
        data = {'summary': {'total_orders': 0, 'total_sales': 0, 'total_tips': 0}, 'table_sales': []}
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Order ID', 'Table Number', 'Waiter', 'Sales', 'Tips', 'Date'])
    
    if data.get('table_sales'):
        for order in data['table_sales']:
            writer.writerow([
                order['order_id'],
                order['table_number'],
                order['waiter_name'],
                f"€{order['total_sales']:.2f}",
                f"€{order['total_tips']:.2f}",
                order['created_at']
            ])
    else:
        writer.writerow(['No sales data available', '', '', '', '', ''])
    
    writer.writerow([])
    writer.writerow(['SUMMARY'])
    writer.writerow(['Total Orders', data['summary']['total_orders']])
    writer.writerow(['Total Sales', f"€{data['summary']['total_sales']:.2f}"])
    writer.writerow(['Total Tips', f"€{data['summary']['total_tips']:.2f}"])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=sales_{period}_{target_date}.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)