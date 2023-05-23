from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from db import crud, db_models, models
from db.database import SessionLocal, engine

# models.Base.metadata.create_all(bind=engine)

# app = FastAPI()


# # Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# @app.post("/login", response_model=models.User)
# def create_user(user: models.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Chto-to")
#     return crud.create_user(db=db, user=user)
