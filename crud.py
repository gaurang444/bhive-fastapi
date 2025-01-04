from sqlalchemy.orm import Session
from models import User, Portfolio
from utils import hash_password

# User Operations
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, password: str):
    hashed_password = hash_password(password)
    db_user = User(email=email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Portfolio Operations
def get_user_portfolio(db: Session, user_id: int):
    return db.query(Portfolio).filter(Portfolio.user_id == user_id).first()

def update_user_portfolio(db: Session, user_id: int, data: str, last_refreshed: str):
    portfolio = get_user_portfolio(db, user_id)
    if portfolio:
        portfolio.data = data
        portfolio.last_refreshed = last_refreshed
    else:
        portfolio = Portfolio(user_id=user_id, data=data, last_refreshed=last_refreshed)
        db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio
