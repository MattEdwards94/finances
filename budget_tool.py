#!/usr/bin/env python3
"""
Budget tool implementing initial_design.md structures.

Provides:
- ProcessedTransaction which wraps RawTransaction and adds classification
- load_raw_data(csv_filename) -> list[RawTransaction]
- process_transactions(raw_trxs) -> list[ProcessedTransaction]

Small CLI: summary, list, reconcile-pots
"""
from __future__ import annotations
import csv
import datetime
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Dict, Tuple
import argparse
import sys
import collections

from budget.raw_transaction import RawTransaction
from budget.transaction import Transaction, save_transactions
from budget.import_data import load_data


def parse_args():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument('--file', '-f', required=True)
    return arg_parse.parse_args()

def main():
    args = parse_args()

    trxs = load_data(args.file)
    if not trxs:
        print('No transactions loaded from', args.file)
        sys.exit(1)

    for i, trx in enumerate(trxs):
        if i < 10:
            print(f"{trx}")





if __name__ == '__main__':
    main()
