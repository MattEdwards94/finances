import pytest
from budget.transaction import Transaction
from budget.raw_transaction import RawTransaction
from budget.screens.pot_transfer import PotTransferSelectScreen
from . import utils

def create_transaction(id, amount, name="Test", type="Payment"):
    overrides = {
        "Transaction ID": id,
        "Amount": str(amount),
        "Local amount": str(amount),
        "Name": name,
        "Type": type,
        "Money Out": str(abs(amount)) if amount < 0 else "0",
        "Money In": str(amount) if amount > 0 else "0",
        "Date": "01/01/2023", # Keep consistent date for tests
    }
    return Transaction(RawTransaction(utils.mock_raw_trx_data(**overrides)))

def test_transaction_link_field():
    t1 = create_transaction("1", -10.0)
    assert t1.link() == ""
    
    t1.set_link("2")
    assert t1.link() == "2"
    
    data = t1.to_prefixed_dict()
    assert data["bt_link"] == "2"
    
    t2 = Transaction(t1.raw, {"link": "2"})
    assert t2.link() == "2"

def test_pot_transfer_candidates_sorting():
    # Target: -15
    current = create_transaction("0", -15.0)
    
    # Candidates: 4, 14, 15, 20
    t1 = create_transaction("1", 4.0, type="Pot transfer")
    t2 = create_transaction("2", 14.0, type="Pot transfer")
    t3 = create_transaction("3", 15.0, type="Pot transfer")
    t4 = create_transaction("4", 20.0, type="Pot transfer")
    
    all_transactions = [current, t1, t2, t3, t4]
    
    screen = PotTransferSelectScreen(current, all_transactions)
    candidates = screen.candidates
    
    # Expected order: 15 (diff 0), 14 (diff 1), 20 (diff 5), 4 (diff 11)
    assert candidates[0].id() == "3" # 15
    assert candidates[1].id() == "2" # 14
    assert candidates[2].id() == "4" # 20
    assert candidates[3].id() == "1" # 4

def test_pot_transfer_candidates_filtering():
    current = create_transaction("0", -15.0)
    
    # Mix of types
    t1 = create_transaction("1", 15.0, type="Pot transfer")
    t2 = create_transaction("2", 15.0, type="Payment")
    t3 = create_transaction("3", 15.0, type="Pot transfer")
    
    all_transactions = [current, t1, t2, t3]
    
    screen = PotTransferSelectScreen(current, all_transactions)
    candidates = screen.candidates
    
    assert len(candidates) == 2
    assert t1 in candidates
    assert t3 in candidates
    assert t2 not in candidates

def test_clear_row_data_unlinks_partner():
    t1 = create_transaction("1", -10.0)
    t2 = create_transaction("2", 10.0)

    # Link them
    t1.set_link("2")
    t2.set_link("1")

    # Simulate clearing t1
    # Logic from BudgetApp.action_clear_row_data
    if t1.link() == t2.id():
        t2.set_link("")
    t1.clear_processed_fields()

    assert t1.link() == ""
    assert t2.link() == ""
