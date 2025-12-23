#!/usr/bin/env python3

import argparse

from budget.main import BudgetApp

def parse_args():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument('--file', '-f', required=False)
    return arg_parse.parse_args()

def main():
    args = parse_args()

    app = BudgetApp(file_path=args.file)
    app.run()



    # trxs = load_data(args.file)
    # if not trxs:
    #     print('No transactions loaded from', args.file)
    #     sys.exit(1)
    #
    # for i, trx in enumerate(trxs):
    #     if i < 10:
    #         print(f"{trx}")


if __name__ == '__main__':
    main()
