The file ./MonzoDataExport_28Jul-27Aug_2025-08-25_094131.csv contains an 
example set of data for a month

Each transaction needs reconciling, into either:

Income
General spend
Pot spend

Within pot spend, the amount needs to be assigned to a particular pot, and we need to make sure
that the amount that was spent was actually withdrawn from the pot


All transactions will be loaded into memory, with each transaction being represented by a 
`RawTransaction`. This is effectively the ORM

raw_trxs = load_raw_data(file)
def load_raw_data(csv_filename: str) -> list[RawTransaction]

class RawTransaction:
    @classmethod
    def from_csv_row(row) -> RawTransaction:

We'll then have a class which represents a processed transaction

class ProcessedTransaction:
    def __init__(raw_trx: RawTransaction)

We'll then operate on the ProcessedTransaction to then decide how the trx should be categorised


