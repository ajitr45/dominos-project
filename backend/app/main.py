
from fastapi import FastAPI, Depends, HTTPException
from requests import Session
from app.database import Base, engine, SessionLocal
from app.models import User
from app.schemas import UserCreate, UserResponse


app = FastAPI()


# Database tables create karna
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "Welcome to domino's Food ordering API"
    }
    
    
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    db_user = User(
        username=user.username,
        email=user.email,
        password=user.password,
        phone=user.phone
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "phone": db_user.phone
    }
    
@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    
    users = db.query(User).all()

    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user