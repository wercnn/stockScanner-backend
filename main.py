from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from fastapi.responses import Response
from fastapi import HTTPException
import csv
import io


sessions = {}
session_counter = 1 


app = FastAPI()

@app.get("/")
def root():
    return {"message": "StockScanner backend running"}

@app.post("/sessions")
def create_session():
    global session_counter 
    session_id = session_counter
    session_counter += 1
        
    sessions[session_id] = {
        "created_at": datetime.utcnow().isoformat(),
        "items": {}
    }
    return {"session_id": session_id}

# Validation model for adding an item
class AddItem(BaseModel):
    barcode: str
    quantity: int
# Endpoint to add an item to a session
@app.post("/sessions/{session_id}/items")
def add_item(session_id: int, payload: AddItem):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    sessions[session_id]["items"][payload.barcode] = payload.quantity
    return {"ok": True}
# Endpoint to get session details
@app.get("/sessions/{session_id}")
def get_session(session_id: int):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "items": sessions[session_id]["items"]
    }

# Endpoint to export session data as CSV
@app.get("/sessions/{session_id}/export")
def export_session(session_id: int):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Barcode", "Quantity"])

    for barcode, qty in sessions[session_id]["items"].items():
        writer.writerow([barcode, qty])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=stocks.csv"}
    )

