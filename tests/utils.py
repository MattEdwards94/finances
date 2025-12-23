

def mock_raw_trx_data(**overrides):
    """
    Returns a dictionary representing a mock raw transaction data row.
    """
    row = {
        "Transaction ID": " tx123 ",
        "Date": "28/07/2025",
        "Time": "12:34:56",
        "Type": "card",
        "Name": "Coffee Shop",
        "Emoji": "☕",
        "Category": "eating_out",
        "Amount": "-3.50",
        "Currency": "GBP",
        "Local amount": "-3.50",
        "Local currency": "GBP",
        "Notes and #tags": "latte #coffee",
        "Address": "123 Main St",
        "Receipt": "",
        "Description": "Coffee",
        "Category split": "",
        "Money Out": "-3.50",
        "Money In": ""
    }
    row.update(overrides)
    return row
