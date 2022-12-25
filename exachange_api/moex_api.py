from datetime import datetime
from typing import Any

import requests as requests

from exachange_api.api import Api, BondInfo, Coupon


class MoexApiConst:
    DESCRIPTION = "description"
    DATA = "data"
    COUPONS = "coupons"
    COUPONDATE = "coupondate"
    VALUE = "value"


class BondDescriptionConst:
    TICKER = "SECID"
    NAME = "NAME"
    START_DATE = "ISSUEDATE"
    FINISH_DATE = "MATDATE"
    BUYBACK_DATE = "BUYBACKDATE"
    FACEVALUE = "FACEVALUE"


class MoexApi(Api):
    DATE_FORMAT = "%Y-%m-%d"
    BASE_URL = "https://iss.moex.com"
    SECURITY_INFO_URL = BASE_URL + "/iss/securities/{ticker}.json"
    COUPONS_URL = (
        BASE_URL
        + "/iss/securities/{ticker}/bondization.json"
        + "?iss.json=extended&iss.meta=off&iss.only=coupons&lang=ru&limit=unlimited"
    )

    def get_bond_info(self, ticker: str) -> BondInfo:
        bond_info = self._get_bond_info_raw(ticker)
        bond_info.coupons = self._get_coupons(ticker)
        return bond_info

    def _get_bond_info_raw(self, ticker: str) -> BondInfo:
        response = requests.get(self.SECURITY_INFO_URL.format(ticker=ticker))
        params = response.json()[MoexApiConst.DESCRIPTION][MoexApiConst.DATA]
        name = str(self._get_value(params, BondDescriptionConst.NAME))
        start_date = datetime.strptime(self._get_value(params, BondDescriptionConst.START_DATE), self.DATE_FORMAT)
        finish_date = datetime.strptime(self._get_value(params, BondDescriptionConst.FINISH_DATE), self.DATE_FORMAT)
        buyback_date_str = self._get_value(params, BondDescriptionConst.BUYBACK_DATE)
        buyback_date = datetime.strptime(buyback_date_str, self.DATE_FORMAT) if buyback_date_str else None
        face_value = float(self._get_value(params, BondDescriptionConst.FACEVALUE))
        return BondInfo(
            ticker=ticker,
            name=name,
            start_date=start_date,
            finish_date=finish_date,
            buyback_date=buyback_date,
            face_value=face_value,
            coupons=[],
        )

    def _get_coupons(self, ticker: str) -> list[Coupon]:
        response = requests.get(self.COUPONS_URL.format(ticker=ticker))
        coupons: list[Coupon] = []
        for coupon_info in response.json()[1][MoexApiConst.COUPONS]:
            coupons.append(
                Coupon(
                    date=datetime.strptime(coupon_info[MoexApiConst.COUPONDATE], self.DATE_FORMAT),
                    value=coupon_info[MoexApiConst.VALUE],
                )
            )
        return coupons

    def _get_value(self, params: list[Any], key: str) -> Any:
        key_index = 0
        value_index = 2
        result = None
        try:
            result = next(x[value_index] for x in params if x[key_index] == key)
        except StopIteration:
            pass
        return result
