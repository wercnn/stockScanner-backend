from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel

sessions = {}
session_counter = 1 


app = FastAPI()

@app.get("/")
def root():
    return {"message": "StockScanner backend running"}
