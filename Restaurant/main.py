from fastapi import FastAPI, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import os
import json
import shutil
from datetime import datetime

from models import create_tables, get_db, Agency, User, Model, City, Booking
import os

app = FastAPI(title="Elite Models Barcelona")

# Initialize templates and static files
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
templates = Jinja2Templates(directory=templates_dir)

# Add custom filter for JSON parsing
import json
def from_json_filter(value):
    try:
        return json.loads(value) if value else []
    except:
        return []

templates.env.filters['from_json'] = from_json_filter

# Create uploads directory for model photos
uploads_dir = os.path.join(static_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    
    # Create sample data if database is empty
    db = next(get_db())
    if db.query(Agency).count() == 0:
        init_sample_data(db)
    db.close()
    print("🚀 Elite Models Agency started successfully")

def init_sample_data(db: Session):
    try:
        # Create sample agency
        agency = Agency(
            name="Elite Models Barcelona",
            subdomain="elite",
            description="Premier modeling agency in Barcelona specializing in fashion and commercial modeling.",
            phone="+34 93 123 4567",
            email="info@elitemodels.es",
            address="Passeig de Gràcia 123, Barcelona, Spain"
        )
        db.add(agency)
        db.flush()
        
        # Create admin user with safe password handling
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        password = "admin123"
        if len(password.encode('utf-8')) > 72:
            password = password.encode('utf-8')[:72].decode('utf-8')
        
        admin = User(
            agency_id=agency.id,
            username="admin",
            password_hash=pwd_context.hash(password),
            role="admin"
        )
        db.add(admin)
    except Exception as e:
        print(f"Error creating admin user: {e}")
        # Skip admin creation if it fails
        pass
    
    # Create cities
    cities_data = [
        {"name": "Barcelona", "country": "Spain"},
        {"name": "Madrid", "country": "Spain"},
        {"name": "Valencia", "country": "Spain"},
        {"name": "Sevilla", "country": "Spain"}
    ]
    
    for city_data in cities_data:
        city = City(
            agency_id=agency.id,
            name=city_data["name"],
            country=city_data["country"]
        )
        db.add(city)
    
    db.commit()

# Routes

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    agency = db.query(Agency).first()
    models = db.query(Model).filter(
        Model.status == "approved",
        Model.available == True
    ).limit(6).all()
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "agency": agency,
        "featured_models": models
    })

@app.get("/models", response_class=HTMLResponse)
async def models_page(
    request: Request, 
    city: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    height_min: Optional[int] = None,
    hair_color: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Model).filter(
        Model.status == "approved",
        Model.available == True
    )
    
    if city:
        query = query.join(City).filter(City.name == city)
    if age_min:
        query = query.filter(Model.age >= age_min)
    if age_max:
        query = query.filter(Model.age <= age_max)
    if height_min:
        query = query.filter(Model.height >= height_min)
    if hair_color:
        query = query.filter(Model.hair_color == hair_color)
    
    models = query.all()
    cities = db.query(City).filter(City.active == True).all()
    
    return templates.TemplateResponse("models.html", {
        "request": request,
        "models": models,
        "cities": cities,
        "filters": {
            "city": city,
            "age_min": age_min,
            "age_max": age_max,
            "height_min": height_min,
            "hair_color": hair_color
        }
    })

@app.get("/model/{model_id}", response_class=HTMLResponse)
async def model_profile(request: Request, model_id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.status == "approved"
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return templates.TemplateResponse("model_profile.html", {
        "request": request,
        "model": model
    })

@app.get("/cities", response_class=HTMLResponse)
async def cities_page(request: Request, db: Session = Depends(get_db)):
    cities = db.query(City).filter(City.active == True).all()
    
    # Get model count per city
    city_stats = []
    for city in cities:
        model_count = db.query(Model).filter(
            Model.city_id == city.id,
            Model.status == "approved",
            Model.available == True
        ).count()
        city_stats.append({
            "city": city,
            "model_count": model_count
        })
    
    return templates.TemplateResponse("cities.html", {
        "request": request,
        "city_stats": city_stats
    })

@app.get("/city/{city_name}", response_class=HTMLResponse)
async def city_models(request: Request, city_name: str, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.name == city_name).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    models = db.query(Model).filter(
        Model.city_id == city.id,
        Model.status == "approved",
        Model.available == True
    ).all()
    
    return templates.TemplateResponse("city_models.html", {
        "request": request,
        "city": city,
        "models": models
    })

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request, db: Session = Depends(get_db)):
    agency = db.query(Agency).first()
    return templates.TemplateResponse("about.html", {
        "request": request,
        "agency": agency
    })

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request, db: Session = Depends(get_db)):
    agency = db.query(Agency).first()
    return templates.TemplateResponse("contact.html", {
        "request": request,
        "agency": agency
    })

@app.post("/contact")
async def submit_contact(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    # Here you would typically send an email or save to database
    # For now, just return success
    return JSONResponse({
        "success": True,
        "message": "Thank you for your message. We will contact you soon."
    })

@app.get("/apply", response_class=HTMLResponse)
async def apply_page(request: Request, db: Session = Depends(get_db)):
    cities = db.query(City).filter(City.active == True).all()
    return templates.TemplateResponse("apply.html", {
        "request": request,
        "cities": cities
    })

@app.post("/apply")
async def submit_application(
    name: str = Form(...),
    age: int = Form(...),
    height: int = Form(...),
    hair_color: str = Form(...),
    eye_color: str = Form(...),
    city_id: int = Form(...),
    bio: str = Form(""),
    photos: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Save uploaded photos
        photo_urls = []
        for photo in photos:
            if photo.filename:
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{photo.filename}"
                file_path = os.path.join(uploads_dir, filename)
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(photo.file, buffer)
                
                photo_urls.append(f"/static/uploads/{filename}")
        
        # Create model application
        agency = db.query(Agency).first()
        model = Model(
            agency_id=agency.id,
            city_id=city_id,
            name=name,
            age=age,
            height=height,
            hair_color=hair_color,
            eye_color=eye_color,
            bio=bio,
            photos=json.dumps(photo_urls),
            status="pending"
        )
        
        db.add(model)
        db.commit()
        
        return JSONResponse({
            "success": True,
            "message": "Application submitted successfully! We will review it and contact you soon."
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Error submitting application: {str(e)}"
        })

@app.post("/book/{model_id}")
async def book_model(
    model_id: int,
    client_name: str = Form(...),
    client_email: str = Form(...),
    client_phone: str = Form(""),
    event_date: str = Form(...),
    event_type: str = Form(...),
    message: str = Form(""),
    db: Session = Depends(get_db)
):
    try:
        model = db.query(Model).filter(Model.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Parse event date
        event_datetime = datetime.strptime(event_date, "%Y-%m-%d")
        
        booking = Booking(
            agency_id=model.agency_id,
            model_id=model_id,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            event_date=event_datetime,
            event_type=event_type,
            message=message
        )
        
        db.add(booking)
        db.commit()
        
        return JSONResponse({
            "success": True,
            "message": "Booking request submitted successfully! We will contact you via WhatsApp or email within 24 hours to confirm details and discuss your requirements."
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Error submitting booking: {str(e)}"
        })

# Admin routes
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {
        "request": request
    })

@app.post("/admin/login")
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Check if admin user exists, create if not
        user = db.query(User).filter(User.username == username).first()
        
        if not user and username == "admin":
            # Create admin user if it doesn't exist
            agency = db.query(Agency).first()
            if agency:
                # Use simple password to avoid bcrypt issues
                simple_password = "admin"
                
                user = User(
                    agency_id=agency.id,
                    username="admin",
                    password_hash=pwd_context.hash(simple_password),
                    role="admin"
                )
                db.add(user)
                db.commit()
        
        if user:
            # Simple password verification
            if pwd_context.verify(password, user.password_hash):
                response = RedirectResponse(url="/admin/dashboard", status_code=302)
                response.set_cookie("admin_logged_in", "true")
                return response
        
        return templates.TemplateResponse("admin_login.html", {
            "request": request,
            "error": "Invalid credentials"
        })
        
    except Exception as e:
        return templates.TemplateResponse("admin_login.html", {
            "request": request,
            "error": f"Login error: {str(e)}"
        })

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    # Simple auth check
    if not request.cookies.get("admin_logged_in"):
        return RedirectResponse(url="/admin/login")
    
    stats = {
        "total_models": db.query(Model).count(),
        "approved_models": db.query(Model).filter(Model.status == "approved").count(),
        "pending_models": db.query(Model).filter(Model.status == "pending").count(),
        "total_bookings": db.query(Booking).count(),
        "pending_bookings": db.query(Booking).filter(Booking.status == "pending").count()
    }
    
    recent_applications = db.query(Model).filter(
        Model.status == "pending"
    ).order_by(Model.created_at.desc()).limit(5).all()
    
    recent_bookings = db.query(Booking).order_by(
        Booking.created_at.desc()
    ).limit(5).all()
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_applications": recent_applications,
        "recent_bookings": recent_bookings
    })

@app.get("/admin/logout")
async def admin_logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_logged_in")
    return response

@app.post("/admin/models/{model_id}/approve")
async def approve_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == model_id).first()
    if model:
        model.status = "approved"
        db.commit()
    return JSONResponse({"success": True})

@app.post("/admin/models/{model_id}/reject")
async def reject_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == model_id).first()
    if model:
        model.status = "rejected"
        db.commit()
    return JSONResponse({"success": True})

@app.post("/admin/bookings/{booking_id}/confirm")
async def confirm_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        booking.status = "confirmed"
        db.commit()
    return JSONResponse({"success": True})

@app.get("/admin/models", response_class=HTMLResponse)
async def admin_models_page(request: Request, db: Session = Depends(get_db)):
    if not request.cookies.get("admin_logged_in"):
        return RedirectResponse(url="/admin/login")
    
    models = db.query(Model).order_by(Model.created_at.desc()).all()
    cities = db.query(City).filter(City.active == True).all()
    
    return templates.TemplateResponse("admin_models.html", {
        "request": request,
        "models": models,
        "cities": cities
    })

@app.post("/admin/models/add")
async def add_model_admin(
    name: str = Form(...),
    age: int = Form(...),
    height: int = Form(...),
    hair_color: str = Form(...),
    eye_color: str = Form(...),
    city_id: int = Form(...),
    bio: str = Form(""),
    status: str = Form("approved"),
    photos: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Save uploaded photos
        photo_urls = []
        for photo in photos:
            if photo.filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{photo.filename}"
                file_path = os.path.join(uploads_dir, filename)
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(photo.file, buffer)
                
                photo_urls.append(f"/static/uploads/{filename}")
        
        # Create model
        agency = db.query(Agency).first()
        model = Model(
            agency_id=agency.id,
            city_id=city_id,
            name=name,
            age=age,
            height=height,
            hair_color=hair_color,
            eye_color=eye_color,
            bio=bio,
            photos=json.dumps(photo_urls),
            status=status,
            available=True
        )
        
        db.add(model)
        db.commit()
        
        return JSONResponse({
            "success": True,
            "message": "Model added successfully!"
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Error adding model: {str(e)}"
        })

@app.delete("/admin/models/{model_id}/delete")
async def delete_model_admin(model_id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == model_id).first()
    if model:
        db.delete(model)
        db.commit()
    return JSONResponse({"success": True})

@app.get("/admin/bookings", response_class=HTMLResponse)
async def admin_bookings_page(request: Request, db: Session = Depends(get_db)):
    if not request.cookies.get("admin_logged_in"):
        return RedirectResponse(url="/admin/login")
    
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    
    return templates.TemplateResponse("admin_bookings.html", {
        "request": request,
        "bookings": bookings
    })

@app.post("/admin/bookings/{booking_id}/cancel")
async def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        booking.status = "cancelled"
        db.commit()
    return JSONResponse({"success": True})

@app.get("/admin/bookings/{booking_id}/details")
async def get_booking_details(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        return JSONResponse({
            "success": True,
            "data": {
                "client_name": booking.client_name,
                "client_email": booking.client_email,
                "client_phone": booking.client_phone,
                "model_name": booking.model.name,
                "event_type": booking.event_type,
                "event_date": booking.event_date.strftime('%Y-%m-%d') if booking.event_date else None,
                "message": booking.message,
                "status": booking.status
            }
        })
    return JSONResponse({"success": False})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)