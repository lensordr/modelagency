from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from models import get_db, Restaurant
from tenant import get_restaurant_from_request, set_tenant_context
import os

# Initialize templates
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip tenant resolution for static files, website, webhooks, and health checks
        if (request.url.path.startswith("/static/") or 
            request.url.path.startswith("/debug/") or
            request.url.path.startswith("/web/") or
            request.url.path.startswith("/webhooks/") or
            request.url.path in ["/", "/favicon.ico", "/robots.txt", "/apple-touch-icon.png", "/test"]):
            return await call_next(request)
        
        # Skip for setup routes and global pages
        if (request.url.path.startswith("/setup") or 
            request.url.path in ["/onboarding", "/onboard", "/admin", "/signup"] or
            request.url.path.startswith("/admin/")):
            return await call_next(request)
        
        try:
            # Get database session
            db = next(get_db())
            
            # Store original path before any rewriting
            original_path = str(request.url.path)
            print(f"Middleware: Processing original path: {original_path}")
            
            # Get restaurant from request (using original path)
            restaurant = get_restaurant_from_request(request, db, original_path)
            
            # Set tenant context
            set_tenant_context(restaurant)
            
            # Add restaurant to request state
            request.state.restaurant = restaurant
            request.state.restaurant_id = restaurant.id
            
            print(f"Middleware: Set restaurant_id={restaurant.id} ({restaurant.name}) for path={original_path}")
            
            # Rewrite URL for /r/subdomain/ requests but preserve restaurant context
            if original_path.startswith("/r/"):
                parts = original_path.split("/")
                if len(parts) >= 4:
                    # Remove /r/subdomain from path
                    new_path = "/" + "/".join(parts[3:])
                    request.scope["path"] = new_path
                    print(f"Middleware: Rewrote path to {new_path} for restaurant {restaurant.id} ({restaurant.name})")
            
            db.close()
            
        except HTTPException as e:
            print(f"Restaurant not found: {e}")
            # Return 404 for all requests
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Restaurant not found or inactive"}, status_code=404)
        except Exception as e:
            print(f"Tenant middleware error: {e}")
            # Only set fallback for direct localhost access (not /r/ URLs)
            if not str(request.url.path).startswith('/r/'):
                try:
                    db = next(get_db())
                    restaurant = db.query(Restaurant).filter(
                        Restaurant.subdomain == 'demo',
                        Restaurant.active == True
                    ).first()
                    if restaurant:
                        request.state.restaurant = restaurant
                        request.state.restaurant_id = restaurant.id
                        set_tenant_context(restaurant)
                        print(f"Middleware: Using fallback restaurant {restaurant.id} ({restaurant.name})")
                    db.close()
                except:
                    pass
        
        response = await call_next(request)
        return response