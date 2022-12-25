import argparse

from pydantic import BaseModel

from exachange_api.moex_api import MoexApi


class A(BaseModel):
    name: str


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", nargs=1, required=True)

    args = parser.parse_args()

    ticker = args.ticker[0]

    api = MoexApi()
    bond_info = api.get_bond_info(ticker)
    print(bond_info)
