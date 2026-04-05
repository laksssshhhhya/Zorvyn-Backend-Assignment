from contextlib import asynccontextmanager
from decimal import Decimal
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import SQLModel, Session, create_engine

from models import Transaction, LedgerEntry, AuditLog
from auth import require_admin, require_analyst, require_viewer
from logic import create_double_entry_transaction, log_audit, calculate_net_balance, calculate_burn_rate, get_all_audit_logs

sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="Zorvyn Finance Data Backend", lifespan=lifespan)

class TransactionRequest(BaseModel):
    reference: str
    debit_account: str
    credit_account: str
    amount: Decimal

@app.post("/transactions")
def create_transaction_endpoint(
    request: TransactionRequest,
    session: Session = Depends(get_session),
    user_role: str = Depends(require_analyst)
):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    transaction = create_double_entry_transaction(
        session=session,
        reference=request.reference,
        debit_account=request.debit_account,
        credit_account=request.credit_account,
        amount=request.amount,
        creator_role=user_role
    )
    
    log_audit(
        session=session,
        user_role=user_role,
        action="create_transaction",
        target="Transaction",
        details_dict={"transaction_id": transaction.id, "amount": str(request.amount)}
    )
    
    return {"status": "success", "transaction_id": transaction.id}

@app.get("/dashboard/net-balance")
def get_net_balance(
    session: Session = Depends(get_session),
    user_role: str = Depends(require_viewer)
):
    balance = calculate_net_balance(session)
    return {"net_balance": balance}

@app.get("/dashboard/burn-rate")
def get_burn_rate(
    session: Session = Depends(get_session),
    user_role: str = Depends(require_viewer)
):
    burn_rate = calculate_burn_rate(session)
    return {"burn_rate": burn_rate}

@app.get("/audit")
def get_audit(
    session: Session = Depends(get_session),
    user_role: str = Depends(require_admin)
):
    logs = get_all_audit_logs(session)
    return logs
