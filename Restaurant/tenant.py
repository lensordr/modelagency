from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from models import Restaurant
from typing import Optional

class TenantContext:
    def __init__(self):
        self.restaurant_id: Optional[int] = None
        self.restaurant: Optional[Restaurant] = None

# Thread-local tenant context
import threading
tenant_context = threading.local()

def get_restaurant_from_subdomain(subdomain: str, db: Session) -> Optional[Restaurant]:
    """Get restaurant by subdomain"""
    return db.query(Restaurant).filter(
        Restaurant.subdomain == subdomain,
        Restaurant.active == True
    ).first()

def get_restaurant_from_request(request: Request, db: Session) -> Restaurant:
    """Extract restaurant from request (subdomain or path parameter)"""
    
    # Method 1: Extract from subdomain (for production)
    host = request.headers.get("host", "")
    if "." in host and not host.startswith("localhost"):
        subdomain = host.split(".")[0]
        restaurant = get_restaurant_from_subdomain(subdomain, db)
        if restaurant:
            return restaurant
    
    # Method 2: Extract from path parameter (for development)
    path = str(request.url.path)
    if path.startswith("/r/"):
        parts = path.split("/")
        if len(parts) >= 3:
            subdomain = parts[2]
            restaurant = get_restaurant_from_subdomain(subdomain, db)
            if restaurant:
                return restaurant
    
    # Method 3: Default restaurant for development (localhost)
    if "localhost" in host or "127.0.0.1" in host:
        restaurant = db.query(Restaurant).filter(Restaurant.active == True).first()
        if restaurant:
            return restaurant
    
    raise HTTPException(status_code=404, detail="Restaurant not found")

def set_tenant_context(restaurant: Restaurant):
    """Set the current tenant context"""
    if not hasattr(tenant_context, 'restaurant_id'):
        tenant_context.restaurant_id = None
        tenant_context.restaurant = None
    tenant_context.restaurant_id = restaurant.id
    tenant_context.restaurant = restaurant

def get_current_restaurant_id() -> int:
    """Get current restaurant ID from context"""
    if not hasattr(tenant_context, 'restaurant_id') or not tenant_context.restaurant_id:
        raise HTTPException(status_code=400, detail="No restaurant context")
    return tenant_context.restaurant_id

def get_current_restaurant() -> Restaurant:
    """Get current restaurant from context"""
    if not hasattr(tenant_context, 'restaurant') or not tenant_context.restaurant:
        raise HTTPException(status_code=400, detail="No restaurant context")
    return tenant_context.restaurant

def requires_plan(required_plan: str):
    """Decorator to check if restaurant has required plan"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            restaurant = get_current_restaurant()
            
            # Trial users get professional features
            if restaurant.plan_type == "trial":
                return func(*args, **kwargs)
            
            # Check plan hierarchy: professional > basic
            if required_plan == "professional" and restaurant.plan_type != "professional":
                raise HTTPException(status_code=403, detail="Professional plan required")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator