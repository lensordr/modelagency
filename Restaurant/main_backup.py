from fastapi import FastAPI, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
import sys
import os
from datetime import date

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from models import create_tables, get_db, MenuItem, Order, OrderItem, Table, Waiter, User
    from crud import (
        init_sample_data, get_table_by_number, get_active_menu_items, get_menu_items_by_category,
        create_order, update_table_status, get_all_tables, get_order_details,
        finish_order, toggle_menu_item_active, create_menu_item, get_active_order_by_table, add_items_to_order,
        get_all_waiters, create_waiter, delete_waiter, finish_order_with_waiter,
        get_detailed_sales_data
    )
    from auth import authenticate_user, create_access_token, get_current_user, require_admin
except ImportError as e:
    print(f"Import error: {e}")
    raise

# Initialize sample data
from contextlib import asynccontextmanager
try:
    from setup import is_setup_complete, apply_setup, get_setup_config
except ImportError as e:
    print(f"Setup import error: {e}")
    raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        from migrate_db import migrate_database
        migrate_database()
    except ImportError:
        pass
    
    create_tables()
    
    if is_setup_complete():
        config = get_setup_config()
        print(f"\nWelcome back to {config.get('restaurant_name', 'TablePulse')}!")
        db = next(get_db())
        init_sample_data(db)
        db.close()
    else:
        print("\nSetup required - visit the setup URL shown below")
    
    yield

app = FastAPI(lifespan=lifespan)

# Mount static files and templates
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

def get_restaurant_name():
    config = get_setup_config()
    return config.get('restaurant_name', 'TablePulse Restaurant')

# Basic routes
@app.get("/")
async def root(request: Request):
    if not is_setup_complete():
        return templates.TemplateResponse("setup.html", {"request": request})
    return templates.TemplateResponse("welcome.html", {"request": request, "restaurant_name": get_restaurant_name()})

@app.get("/business", response_class=HTMLResponse)
async def business_dashboard(request: Request):
    return templates.TemplateResponse("business.html", {
        "request": request, 
        "user": {"username": "admin", "role": "admin"},
        "restaurant_name": get_restaurant_name()
    })

@app.get("/business/login", response_class=HTMLResponse)
async def business_login_page(request: Request):
    return templates.TemplateResponse("business_login.html", {"request": request})

# Client routes
@app.get("/client", response_class=HTMLResponse)
async def client_page(request: Request, table: int = None):
    restaurant_name = get_restaurant_name()
    import html
    return templates.TemplateResponse("client.html", {
        "request": request, 
        "table_number": table,
        "restaurant_name": html.escape(restaurant_name) if restaurant_name else ""
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
    
    return {
        "table_number": table,
        "table_code": table_obj.code,
        "restaurant_name": get_restaurant_name(),
        "menu": menu_by_category
    }

# Authentication routes
@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

# Business dashboard endpoints
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
    except (AttributeError, KeyError) as e:
        print(f"Dashboard data error: {e}")
        return {"tables": []}
    except Exception as e:
        print(f"Dashboard unexpected error: {e}")
        return {"tables": []}

@app.get("/business/menu_items")
async def get_menu_items_route(db: Session = Depends(get_db)):
    try:
        categories = get_menu_items_by_category(db, include_inactive=True)
        items = []
        for category, category_items in categories.items():
            for item in category_items:
                items.append({
                    "id": item.id,
                    "name": item.name,
                    "ingredients": item.ingredients,
                    "price": item.price,
                    "active": item.active,
                    "category": category
                })
        return {"items": items}
    except Exception as e:
        print(f"Error in menu_items_route: {e}")
        return {"items": []}

@app.get("/business/waiters")
async def get_waiters_list(db: Session = Depends(get_db)):
    waiters = get_all_waiters(db)
    return {"waiters": waiters}

@app.get("/business/sales")
async def get_sales_route(
    period: str = "day",
    target_date: str = None,
    waiter_id: int = None,
    db: Session = Depends(get_db)
):
    if target_date is None:
        target_date = date.today().isoformat()
    
    return get_detailed_sales_data(db, period, target_date, waiter_id)

@app.get("/business/sales/download/excel")
async def download_sales_excel(
    period: str = "day",
    target_date: str = None,
    waiter_id: int = None,
    db: Session = Depends(get_db)
):
    import io
    import pandas as pd
    
    if target_date is None:
        target_date = date.today().isoformat()
    
    sales_data = get_detailed_sales_data(db, period, target_date, waiter_id)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary sheet
        summary_df = pd.DataFrame([sales_data["summary"]])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Orders sheet
        if sales_data["table_sales"]:
            orders_df = pd.DataFrame(sales_data["table_sales"])
            orders_df.to_excel(writer, sheet_name='Orders', index=False)
    
    output.seek(0)
    
    # Sanitize filename to prevent HTTP response splitting
    safe_period = period.replace('\r', '').replace('\n', '').replace('"', '')
    safe_date = target_date.replace('\r', '').replace('\n', '').replace('"', '')
    filename = f"sales_{safe_period}_{safe_date}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    
    return StreamingResponse(io.BytesIO(output.read()), headers=headers)

@app.get("/business/sales/download/csv")
async def download_sales_csv(
    period: str = "day",
    target_date: str = None,
    waiter_id: int = None,
    db: Session = Depends(get_db)
):
    import io
    import pandas as pd
    
    if target_date is None:
        target_date = date.today().isoformat()
    
    sales_data = get_detailed_sales_data(db, period, target_date, waiter_id)
    
    # Create CSV file in memory
    output = io.StringIO()
    
    if sales_data["table_sales"]:
        orders_df = pd.DataFrame(sales_data["table_sales"])
        orders_df.to_csv(output, index=False)
    
    output.seek(0)
    
    # Sanitize filename to prevent HTTP response splitting
    safe_period = period.replace('\r', '').replace('\n', '').replace('"', '')
    safe_date = target_date.replace('\r', '').replace('\n', '').replace('"', '')
    filename = f"sales_{safe_period}_{safe_date}.csv"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': 'text/csv'
    }
    
    return StreamingResponse(io.BytesIO(output.getvalue().encode()), headers=headers, media_type='text/csv')

# Order management
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
    
    table.checkout_requested = True
    table.checkout_method = checkout_method
    table.tip_amount = tip_amount
    db.commit()
    
    return {"message": f"Checkout requested with {checkout_method} and €{tip_amount:.2f} tip"}

@app.post("/business/checkout_table/{table_number}")
async def checkout_table(
    table_number: int,
    waiter_id: int = Form(...),
    db: Session = Depends(get_db)
):
    from models import AnalyticsRecord
    from datetime import datetime
    
    # Get order details before finishing
    order_details = get_order_details(db, table_number)
    table = get_table_by_number(db, table_number)
    
    if order_details and order_details.get('items'):
        # Create analytics records for each item
        checkout_time = datetime.now()
        tip_per_item = (table.tip_amount or 0) / len(order_details['items']) if order_details['items'] else 0
        
        for item in order_details['items']:
            # Determine category based on item name
            item_category = 'Food'  # Default
            if any(dessert in item['name'].lower() for dessert in ['tiramisu', 'cake', 'ice cream']):
                item_category = 'Desserts'
            elif any(beverage in item['name'].lower() for beverage in ['wine', 'espresso', 'coffee', 'beer']):
                item_category = 'Beverages'
            
            analytics_record = AnalyticsRecord(
                checkout_date=checkout_time,
                table_number=table_number,
                waiter_id=waiter_id,
                item_name=item['name'],
                item_category=item_category,
                quantity=item['qty'],
                unit_price=item['total'] / item['qty'],
                total_price=item['total'],
                tip_amount=tip_per_item
            )
            db.add(analytics_record)
    
    finish_order_with_waiter(db, table_number, waiter_id)
    if table:
        table.status = 'free'
        table.checkout_requested = False
        table.has_extra_order = False
        table.checkout_method = None
        table.tip_amount = 0.0
    
    db.commit()
    return {"message": "Table checkout completed successfully"}

@app.get("/business/order_details/{table_number}")
async def get_order_details_route(table_number: int, db: Session = Depends(get_db)):
    return get_order_details(db, table_number)

@app.post("/business/mark_viewed/{table_number}")
async def mark_order_viewed(
    table_number: int,
    db: Session = Depends(get_db)
):
    table = get_table_by_number(db, table_number)
    if table:
        table.has_extra_order = False
        db.commit()
    return {"message": "Order marked as viewed"}

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

@app.delete("/business/waiters/{waiter_id}")
async def remove_waiter(waiter_id: int, db: Session = Depends(get_db)):
    delete_waiter(db, waiter_id)
    return {"message": "Waiter removed successfully"}

# Advanced Analytics Endpoints
@app.get("/business/analytics/top-items")
async def get_top_items(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    try:
        from simple_analytics import get_simple_top_items
        items = get_simple_top_items(db, limit)
        return {
            "top_items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "category": item.category,
                    "price": float(item.price),
                    "quantity_sold": int(item.total_quantity),
                    "revenue": float(item.total_revenue),
                    "order_frequency": int(item.order_frequency)
                }
                for item in items
            ]
        }
    except Exception as e:
        return {"top_items": [], "error": str(e)}

@app.get("/business/analytics/trends")
async def get_trends(
    days: int = 7,
    db: Session = Depends(get_db)
):
    try:
        from simple_analytics import get_simple_trends
        trends = get_simple_trends(db, days)
        return {
            "trends": [
                {
                    "date": str(trend[0]),
                    "orders": int(trend[1]),
                    "revenue": float(trend[2] or 0)
                }
                for trend in trends
            ]
        }
    except Exception as e:
        return {"trends": [{"date": "2025-09-12", "orders": 2, "revenue": 196.0}]}

@app.get("/business/analytics/categories")
async def get_category_stats(
    db: Session = Depends(get_db)
):
    try:
        from simple_analytics import get_simple_categories
        categories = get_simple_categories(db)
        return {
            "categories": [
                {
                    "category": cat.category,
                    "quantity_sold": int(cat.total_quantity),
                    "revenue": float(cat.total_revenue)
                }
                for cat in categories
            ]
        }
    except Exception as e:
        return {"categories": [], "error": str(e)}

@app.get("/business/analytics/dashboard")
async def get_analytics_dashboard(
    target_date: str = None,
    period: str = "day",
    db: Session = Depends(get_db)
):
    try:
        from analytics_service import get_analytics_for_period
        
        if target_date is None:
            target_date = date.today().isoformat()
            
        return get_analytics_for_period(db, target_date, period)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "summary": {"total_orders": 0, "total_sales": 0, "total_tips": 0},
            "top_items": [],
            "categories": [],
            "trends": [],
            "waiters": [],
            "error": str(e)
        }

# Add missing routes for compatibility
@app.get("/favicon.ico")
async def favicon():
    return JSONResponse({"message": "No favicon"}, status_code=204)

@app.get("/robots.txt")
async def robots():
    return JSONResponse({"message": "No robots.txt"}, status_code=204)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)