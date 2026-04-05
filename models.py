from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    role: str

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reference: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str

class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transaction.id")
    account: str
    entry_type: str
    amount: Decimal
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_role: str
    action: str
    target: str
    details: str
