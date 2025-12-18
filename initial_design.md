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


# Data layout

Raw data in the form:
trx_id, date, time, type, ..., money out, money in

We store in RawTransaction:
   trx_id, date, time, type, ..., notes
    raw_data

Then we'll have processed
    raw_trx
    processed_field1
    processed_field2
    ..

We want to be able to load both raw and processed
    - Do we want to treat them the same?

Same:
    - load_raw needs to be able to detect what columns are raw/processed

different:
    - need to have separate loaders/savers


This could be solved by simply storing in code all the columns that we expect
in the raw data, and anything else is processed
    - What happens if the raw data changes?
        - Just error? Deal with that later

load_data -> transactions
    raw_dict = read_raw(raw_columns)
    RawTransaction.from_dict(dict)
    
    headers = read_headers()
    processed_columns = headers - raw_columns
    if processed_columns:
        processed_dict = read_processed(processed_columns)
    
    Alert if processed data is missing for a raw transaction

    
trxs = [Transaction]

for trx in trxs:
    trx.process()

Transaction
    self.raw_trx: RawTransaction
    self.processed_field1
    self.processed_field2

    def save_processed(self):
        data = self.raw_trx.to_dict()
        data.update({
            'processed_field1': self.processed_field1,
            ...
        })
        csv_write_row(data)


# processing

## Pot spend

For each pot spend, we need to identify which pot it came from, and whether money
has actually been withdrawn from the pot

We can probably auto match some transactions, for example direct debits where monzo
automatically withdraws from the pot

we'll see:
    trx_id_1, 1/1/2025, 10:00, Pot transfer, ..., 12.34, ...
    trx_id_2, 1/1/2025, 10:01, Direct debit, ..., 12.34, ...

pot_trxs
for trx in trxs:
    if trx.type == 'Pot transfer':
        pot_trxs.append(trx)
    if trx.amount in pot_trxs:
        match them  -- how? bi-directional link?
        trx.set_matched()

# regular spend

Do we loop all transactions, or group by category

for trx in trxs:
    if trx.not_matched():
        
Would be nice to have some form of TUI for this?
        









