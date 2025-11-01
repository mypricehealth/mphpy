import json
import os
import sys
from pathlib import Path

import pytest

# This import annoys Pylance for some reason.
from pytest_snapshot.plugin import Snapshot  # type: ignore

from .client import Claim, Client, PriceConfig
from .credentials import Credentials
from .date import DateTime
from .env import load_env
from .pricing import ClaimStatus, PricedService, Pricing, status_new
from .response import ResponseError


@pytest.fixture(autouse=True)
def run_around_tests():
    load_env()


def test_client(snapshot: Snapshot):
    api_key = os.getenv("MPH_API_KEY")
    if api_key is None:
        raise EnvironmentError("MPH_API_KEY must be set")

    api_url = os.getenv("API_URL")
    app_url = os.getenv("APP_URL")
    app_api_key = os.getenv("FIREBASE_API_KEY")
    if app_api_key is None:
        raise Exception("FIREBASE_API_KEY must be set")

    app_referer = os.getenv("FIREBASE_REFERER")
    if app_referer is None:
        raise Exception("FIREBASE_REFERER must be set")

    app_credentials = Credentials(
        api_key=app_api_key,
        referer=app_referer,
        credentials_path=Path("fake-credentials-path"),
        email="test-user@mypricehealth.com",
        id_token="fake-id-token",
        refresh_token="fake-refresh-token",
        expires_at=sys.float_info.max,
    )

    client = Client(
        api_key,
        api_url=api_url,
        app_url=app_url,
        app_api_key=app_api_key,
        app_referer=app_referer,
        app_credentials=app_credentials,
    )

    config = PriceConfig(
        is_commercial=True,
        disable_cost_based_reimbursement=False,
        use_commercial_synthetic_for_not_allowed=True,
        use_drg_from_grouper=False,
        use_best_drg_price=True,
        override_threshold=300,
        include_edits=True,
    )

    tests = ["hcfa", "inpatient", "outpatient"]

    for test in tests:
        with open(f"testdata/{test}.json", "r") as f:
            data = json.load(f)

            claim = Claim.model_validate(data)
            pricing = client.price(config, claim)

            snapshot.assert_match(pricing.model_dump_json(indent=4), f"{test}.json")

    try:
        client.insert_claim_status(
            "123",
            ClaimStatus(
                step=status_new.step,
                status=status_new.status,
                updated_by="1",
                updated_at=DateTime(2000, 1, 1),
                pricing=Pricing(
                    services=[PricedService(line_number="6789")]
                ),
            )
        )
    except ResponseError as response_error:
        # The claim and line item won't exist in the database
        assert (
            response_error.detail
            == "expected to insert 1 line item repricing rows but inserted 0"
        )

        pass
