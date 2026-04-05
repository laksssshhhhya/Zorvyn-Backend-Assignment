import json
from decimal import Decimal
from sqlmodel import Session, select, func
from models import Transaction, LedgerEntry, AuditLog

def create_double_entry_transaction(session: Session, reference: str, debit_account: str, credit_account: str, amount: Decimal, creator_role: str) -> Transaction:
    new_transaction = Transaction(reference=reference, created_by=creator_role)
    session.add(new_transaction)
    session.commit()
    session.refresh(new_transaction)

    debit_entry = LedgerEntry(transaction_id=new_transaction.id, account=debit_account, entry_type="debit", amount=amount)
    credit_entry = LedgerEntry(transaction_id=new_transaction.id, account=credit_account, entry_type="credit", amount=amount)
    
    session.add(debit_entry)
    session.add(credit_entry)
    session.commit()
    session.refresh(new_transaction)
    
    return new_transaction

def log_audit(session: Session, user_role: str, action: str, target: str, details_dict: dict):
    audit_entry = AuditLog(
        user_role=user_role,
        action=action,
        target=target,
        details=json.dumps(details_dict)
    )
    session.add(audit_entry)
    session.commit()

def calculate_net_balance(session: Session) -> Decimal:
    debits = session.exec(select(func.sum(LedgerEntry.amount)).where(LedgerEntry.entry_type == "debit")).first()
    credits = session.exec(select(func.sum(LedgerEntry.amount)).where(LedgerEntry.entry_type == "credit")).first()
    return (debits or Decimal("0.0")) - (credits or Decimal("0.0"))

def calculate_burn_rate(session: Session) -> Decimal:
    expenses = session.exec(
        select(func.sum(LedgerEntry.amount))
        .where(
            LedgerEntry.entry_type == "debit",
            LedgerEntry.account.like("%Expense%")
        )
    ).first()
    return expenses or Decimal("0.0")

def get_all_audit_logs(session: Session):
    return session.exec(select(AuditLog).order_by(AuditLog.timestamp.desc())).all()
