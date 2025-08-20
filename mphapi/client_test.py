import json
import os

from . import Claim, Client, PriceConfig

# This import annoys Pylance for some reason.
from pytest_snapshot.plugin import Snapshot  # type: ignore


def test_client(snapshot: Snapshot):
    api_key = os.getenv("API_KEY")
    if api_key is None:
        raise EnvironmentError("API_KEY must be set")

    client = Client(api_key)

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

            snapshot.assert_match(pricing.model_dump_json(indent=2), f"{test}.json")
