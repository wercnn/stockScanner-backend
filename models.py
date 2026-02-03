from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class StockSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StockItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="stocksession.id")
    barcode: str
    quantity: int
