from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import requests
from auth import create_access_token, authenticate_user, get_db
from crud import create_user, get_user_portfolio, update_user_portfolio
from models import User, Portfolio
from datetime import timedelta

app = FastAPI()

# Register Route
@app.post("/auth/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    db_user = create_user(db, email, password)
    return {"email": db_user.email, "is_active": db_user.is_active}

# Login Route (JWT Token)
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected Route to Fetch Portfolio
@app.get("/portfolio")
def get_portfolio(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_user_by_email(db, token)
    portfolio = get_user_portfolio(db, user.id)
    if portfolio:
        return {"user_id": user.id, "data": portfolio.data, "last_refreshed": portfolio.last_refreshed}
    else:
        raise HTTPException(status_code=404, detail="Portfolio not found")

# Route to Update Portfolio Data
@app.post("/portfolio/update")
def update_portfolio(data: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_user_by_email(db, token)
    last_refreshed = datetime.utcnow().isoformat()
    portfolio = update_user_portfolio(db, user.id, data, last_refreshed)
    return {"user_id": user.id, "data": portfolio.data, "last_refreshed": portfolio.last_refreshed}

# Fetch Mutual Fund Data from RapidAPI
@app.get("/funds")
def fetch_funds():
    url = "https://latest-mutual-fund-nav.p.rapidapi.com/master?RTA_Agent_Code=CAMS&AMC_Code=BirlaSunLifeMutualFund_MF"
    headers = {
        "x-rapidapi-host": "latest-mutual-fund-nav.p.rapidapi.com",
        "x-rapidapi-key": "your-api-key"
    }
    response = requests.get(url, headers=headers)
    return response.json()
