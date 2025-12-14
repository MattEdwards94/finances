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
from budget.processed_transaction import ProcessedTransaction
from budget.import_data import load_raw_data

def process_transactions(raw_trxs: List[RawTransaction]) -> List[ProcessedTransaction]:
    processed = [ProcessedTransaction(raw=rt) for rt in raw_trxs]
    for p in processed:
        p.categorize()
    reconcile_pots(processed)
    return processed


def reconcile_pots(processed: List[ProcessedTransaction]):
    # Match pot transfers that cancel each other (simple heuristic): same abs(amount), same date, opposite sign
    pot_map: Dict[Tuple[datetime.date, Decimal, str], List[ProcessedTransaction]] = collections.defaultdict(list)
    for p in processed:
        if p.classification == 'Pot':
            key = (p.raw.date, abs(p.raw.amount), p.pot_name or p.raw.name)
            pot_map[key].append(p)
    # For each key, if there are both positive and negative entries, mark them matched
    for key, items in pot_map.items():
        positives = [i for i in items if i.raw.amount > 0]
        negatives = [i for i in items if i.raw.amount < 0]
        # pair up min(len(pos), len(neg))
        pairs = min(len(positives), len(negatives))
        for i in range(pairs):
            positives[i].pot_withdrawal_matched = True
            negatives[i].pot_withdrawal_matched = True


def summarize_monthly(processed: List[ProcessedTransaction]):
    by_month = collections.defaultdict(list)
    for p in processed:
        key = p.raw.date.strftime('%Y-%m')
        by_month[key].append(p)
    out = []
    for m in sorted(by_month.keys()):
        total = sum(p.raw.amount for p in by_month[m])
        income = sum(p.raw.amount for p in by_month[m] if p.raw.amount > 0)
        expenses = sum(p.raw.amount for p in by_month[m] if p.raw.amount < 0)
        out.append((m, total, income, expenses))
    return out


def print_summary(processed: List[ProcessedTransaction]):
    rows = summarize_monthly(processed)
    print(f"{'Month':10} {'Total':12} {'Income':12} {'Expenses':12}")
    for m, total, income, expenses in rows:
        print(f"{m:10} {total:12.2f} {income:12.2f} {expenses:12.2f}")


def print_by_category(processed: List[ProcessedTransaction], month: Optional[str] = None, top: int = 20):
    items = processed
    if month:
        items = [p for p in processed if p.raw.date.strftime('%Y-%m') == month]
        if not items:
            print('No data for month', month)
            return
    c = collections.Counter()
    for p in items:
        c[p.raw.category or 'Unknown'] += p.raw.amount
    for cat, amt in c.most_common(top):
        print(f"{amt:12.2f} {cat}")


def list_unmatched_pot_withdrawals(processed: List[ProcessedTransaction]):
    for p in processed:
        if p.classification == 'Pot' and p.raw.amount < 0 and not p.pot_withdrawal_matched:
            print(f"UNMATCHED POT WITHDRAWAL: {p.raw.date} {p.raw.amount:12.2f} {p.pot_name} ({p.raw.name})")


def parse_args():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument('--file', '-f')
    return arg_parse.parse_args()

def main():
    args = parse_args()

    raw = load_raw_data(args.file)
    if not raw:
        print('No transactions loaded from', args.file)
        sys.exit(1)





if __name__ == '__main__':
    main()
