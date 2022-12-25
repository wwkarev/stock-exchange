from datetime import datetime

from pydantic import BaseModel


class Coupon(BaseModel):
    date: datetime
    value: float


class BondInfo(BaseModel):
    name: str
    ticker: str
    face_value: float
    start_date: datetime
    finish_date: datetime
    buyback_date: datetime | None
    coupons: list[Coupon]


class Api:
    def get_bond_info(self, ticker: str) -> BondInfo:
        raise NotImplementedError()
