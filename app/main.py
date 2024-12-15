from fastapi import FastAPI
from app.routers import products
from sendo.sendo_database import create_or_reset_table #import your table creation logic

#Initialize the FastAPI app
app = FastAPI()

#Include routers
app.include_router(products.router)
#Create or reset the database table when the app starts
@app.on_event("startup")
def startup():
    create_or_reset_table(reset=True)
#Pydantic model for input validation

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sendo Data API!"}