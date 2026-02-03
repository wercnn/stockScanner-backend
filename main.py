from fastapi import FastAPI,HTTPException, Depends
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi.responses import Response
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import StockSession, StockItem
import csv
import io


app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "StockScanner backend running"}

@app.post("/sessions")
def create_session(db: Session = Depends(get_session)):
    session = StockSession()
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id}

# Validation model for adding an item
class AddItem(BaseModel):
    barcode: str
    quantity: int = Field(gt=0)
# Endpoint to add an item to a session
@app.post("/sessions/{session_id}/items")
def add_item(
    session_id: int,
    payload: AddItem,
    db: Session = Depends(get_session)
):
    session = db.get(StockSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    item = StockItem(
        session_id=session_id,
        barcode=payload.barcode,
        quantity=payload.quantity
    )

    db.add(item)
    db.commit()
    return {"ok": True}
# Endpoint to get session details
@app.get("/sessions/{session_id}")
def get_session_details(
    session_id: int,
    db: Session = Depends(get_session)
):
    session = db.get(StockSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    items = db.exec(
        select(StockItem).where(StockItem.session_id == session_id)
    ).all()

    return {
        "session_id": session.id,
        "created_at": session.created_at,
        "items": [
            {"barcode": i.barcode, "quantity": i.quantity}
            for i in items
        ]
    }


# Endpoint to export session data as CSV
@app.get("/sessions/{session_id}/export")
def export_session(
    session_id: int,
    db: Session = Depends(get_session)
):
    session = db.get(StockSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    items = db.exec(
        select(StockItem).where(StockItem.session_id == session_id)
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Barcode", "Quantity"])

    for item in items:
        writer.writerow([item.barcode, item.quantity])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=stocks.csv"
        }
    )
