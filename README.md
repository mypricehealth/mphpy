# mphapi

A Python client library to make it easy to connect to the My Price Health API. It can be accessed at https://api.myprice.health. This client library makes it easy to connect to the API for Python developers.

## The My Price Health API

The My Price Health API can be used to get pricing and estimated pricing for Medicare reimbursement. Medicare benchmarks are a great tool to advance the quadruple aim in healthcare.

## Usage

See also the examples folder for additional examples

```python
from mphapi import Claim, Client, Date, Diagnosis, FormType, PriceConfig, Service


def main():
    config = PriceConfig(
        is_commercial=True,  # uses commercial code crosswalks
        disable_cost_based_reimbursement=False,  # use cost-based reimbursement for MAC priced line-items
        use_commercial_synthetic_for_not_allowed=True,  # use synthetic Medicare for line items not allowed by Medicare, but which may still be paid by commercial plans
        use_drg_from_grouper=False,  # always use the DRG from the inpatient grouper (not applicable with UseBestDRGPrice set to true)
        use_best_drg_price=True,  # price both using the DRG supplied in the claim and the DRG from the grouper and return the lowest price
        override_threshold=300,  # for claims which fail NCCI or other edit rules, override the errors up to this amount to get a price
        include_edits=True,  # get detailed information from the code editor about why a claim failed)
    )

    c = Client("apiKey")  # replace this with your API key
    result = c.price(config, inpatient_claim)
    print(result)


inpatient_claim = Claim(
    npi="1962999664",
    provider_zip="35960",
    drg="461",
    patient_date_of_birth=Date(1988, 1, 2),
    form_type=FormType.UB_04,
    bill_type_or_pos="111",
    billed_amount=47224,
    date_from=Date(2020, 2, 27),
    date_through=Date(2020, 2, 28),
    principal_diagnosis=Diagnosis(code="N186"),
    other_diagnoses=[
        Diagnosis(code="Z992"),
        Diagnosis(code="I120"),
        Diagnosis(code="E6601"),
        Diagnosis(code="E785"),
        Diagnosis(code="Z6832"),
    ],
    services=[
        Service(
            line_number="1",
            rev_code="320",
            billed_amount=2126,
            date_from=Date(2020, 2, 27),
            date_through=Date(2020, 2, 27),
            procedure_code="76000",
            quantity=1,
        ),
        Service(
            line_number="2",
            rev_code="360",
            billed_amount=28684,
            date_from=Date(2020, 2, 27),
            date_through=Date(2020, 2, 27),
            procedure_code="36821",
            quantity=1,
        ),
        Service(
            line_number="3",
            rev_code="370",
            billed_amount=16414,
            date_from=Date(2020, 2, 27),
            date_through=Date(2020, 2, 27),
            procedure_code="",
            quantity=48,
        ),
    ],
)


if __name__ == "__main__":
    main()
```

## Why Medicare Pricing?

It is possible and practical to achieve the quadruple aim in healthcare. With Medicare pricing for all your claims data, you’ll have the tools you need to:

- Lower cost through better provider negotiation, better plan design and more engaged members
- Better outcomes through an effective health plan prioritizing quality care, low cost and better health management
- Happier plan members through education and a better health plan
- More engaged providers who act as partners, not adversaries

For more information about how Medicare pricing can advance the quadruple aim in healthcare, see our [Advancing the quadruple aim with Medicare pricing white paper](https://myprice.health/Advancing%20the%20quadruple%20aim%20with%20Medicare%20pricing%20-%20v2.pdf).
