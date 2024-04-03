import urllib.parse
from typing import Any, Mapping

import requests
from pydantic import BaseModel

from .claim import Claim, RateSheet
from .pricing import Pricing
from .response import Response, Responses

Header = Mapping[str, str | bytes | None]


class PriceConfig(BaseModel):
    """PriceConfig is used to configure the behavior of the pricing API"""

    is_commercial: bool
    """set to true to use commercial code crosswalks"""

    disable_cost_based_reimbursement: bool
    """by default, the API will use cost-based reimbursement for MAC priced line-items. This is the best estimate we have for this proprietary pricing"""

    use_commercial_synthetic_for_not_allowed: bool
    """set to true to use a synthetic Medicare price for line-items that are not allowed by Medicare"""

    use_drg_from_grouper: bool
    """set to true to always use the DRG from the inpatient grouper"""

    use_best_drg_price: bool
    """set to true to use the best DRG price between the price on the claim and the price from the grouper"""

    override_threshold: float
    """set to a value greater than 0 to allow the pricer flexibility to override NCCI edits and other overridable errors and return a price"""

    include_edits: bool
    """set to true to include edit details in the response"""


class Client:
    url: str
    headers: Header

    def __init__(self, isTest: bool, apiKey: str):
        if isTest:
            self.url = "https://api-test.myprice.health"
        else:
            self.url = "https://api.myprice.health"

        self.headers = {"x-api-key": apiKey}

    def _do_request(
        self,
        path: str,
        json: Any | None,
        method: str = "POST",
        headers: Header = {},
    ) -> requests.Response:
        return requests.request(
            method,
            urllib.parse.urljoin(self.url, path),
            json=json,
            headers={**self.headers, **headers},
        )

    def _receive_response[
        Model: BaseModel
    ](
        self,
        path: str,
        json: Any | None,
        model: type[Model],
        method: str = "POST",
        headers: Header = {},
    ) -> Response[Model]:
        return Response[model].model_validate_json(
            self._do_request(path, json, method, headers).content
        )

    def _receive_responses[
        Model: BaseModel
    ](
        self,
        path: str,
        json: Any | None,
        model: type[Model],
        method: str = "POST",
        headers: Header = {},
    ) -> Responses[Model]:
        return Responses[model].model_validate_json(
            self._do_request(path, json, method, headers).content
        )

    def estimate_rate_sheet(self, *inputs: RateSheet) -> Responses[Pricing]:
        return self._receive_responses(
            "/v1/medicare/estimate/rate-sheet",
            inputs,
            Pricing,
        )

    def estimate_claims(
        self, config: PriceConfig, *inputs: Claim
    ) -> Responses[Pricing]:
        return self._receive_responses(
            "/v1/medicare/estimate/claims",
            inputs,
            Pricing,
            headers=self._get_price_headers(config),
        )

    def price(self, config: PriceConfig, *inputs: Claim) -> Response[Pricing]:
        return self._receive_response(
            "/v1/medicare/price/claim",
            inputs,
            Pricing,
            headers=self._get_price_headers(config),
        )

    def _get_price_headers(self, config: PriceConfig) -> Header:
        headers: Header = {}
        if config.is_commercial:
            headers["is-commercial"] = "true"

        if config.disable_cost_based_reimbursement:
            headers["disable-cost-based-reimbursement"] = "true"

        if config.use_commercial_synthetic_for_not_allowed:
            headers["use-commercial-synthetic-for-not-allowed"] = "true"

        if config.override_threshold > 0:
            headers["override-threshold"] = str(config.override_threshold)

        if config.include_edits:
            headers["include-edits"] = "true"

        if config.use_drg_from_grouper:
            headers["use-drg-from-grouper"] = "true"

        if config.use_best_drg_price:
            headers["use-best-drg-price"] = "true"

        return headers
