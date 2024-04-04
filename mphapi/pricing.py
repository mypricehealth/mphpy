from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import core_schema

from .claim import Service, camel_case_model_config
from .response import ResponseError


class ClaimRepricingCode(str, Enum):
    """claim-level repricing codes"""

    MEDICARE = "MED"
    CONTRACT_PRICING = "CON"
    RBP_PRICING = "RBP"
    SINGLE_CASE_AGREEMENT = "SCA"
    NEEDS_MORE_INFO = "IFO"


class LineRepricingCode(str, Enum):
    # line-level Medicare repricing codes
    MEDICARE = "MED"
    SYNTHETIC_MEDICARE = "SYN"
    COST_PERCENT = "CST"
    MEDICARE_PERCENT = "MPT"
    MEDICARE_NO_OUTLIER = "MNO"
    BILLED_PERCENT = "BIL"
    FEE_SCHEDULE = "FSC"
    PER_DIEM = "PDM"
    FLAT_RATE = "FLT"
    LIMITED_TO_BILLED = "LTB"

    # line-level zero dollar repricing explanations
    NOT_ALLOWED_BY_MEDICARE = "NAM"
    PACKAGED = "PKG"
    NEEDS_MORE_INFO = "IFO"
    PROCEDURE_CODE_PROBLEM = "CPB"
    NOT_REPRICED_PER_REQUEST = "NRP"


class HospitalType(str, Enum):
    ACUTE_CARE = "Acute Care Hospitals"
    CRITICAL_ACCESS = "Critical Access Hospitals"
    CHILDRENS = "Childrens"
    PSYCHIATRIC = "Psychiatric"
    ACUTE_CARE_DOD = "Acute Care - Department of Defense"


class InpatientPriceDetail(BaseModel):
    """InpatientPriceDetail contains pricing details for an inpatient claim"""

    model_config = camel_case_model_config

    drg: Optional[str] = None
    """Diagnosis Related Group (DRG) code used to price the claim"""

    drg_amount: Optional[float] = None
    """Amount Medicare would pay for the DRG"""

    passthrough_amount: Optional[float] = None
    """Per diem amount to cover capital-related costs, direct medical education, and other costs"""

    outlier_amount: Optional[float] = None
    """Additional amount paid for high cost cases"""

    indirect_medical_education_amount: Optional[float] = None
    """Additional amount paid for teaching hospitals"""

    disproportionate_share_amount: Optional[float] = None
    """Additional amount paid for hospitals with a high number of low-income patients"""

    uncompensated_care_amount: Optional[float] = None
    """Additional amount paid for patients who are unable to pay for their care"""

    readmission_adjustment_amount: Optional[float] = None
    """Adjustment amount for hospitals with high readmission rates"""

    value_based_purchasing_amount: Optional[float] = None
    """Adjustment for hospitals based on quality measures"""


class OutpatientPriceDetail(BaseModel):
    """OutpatientPriceDetail contains pricing details for an outpatient claim"""

    model_config = camel_case_model_config

    outlier_amount: float
    """Additional amount paid for high cost cases"""

    first_passthrough_drug_offset_amount: float
    """Amount built into the APC payment for certain drugs"""

    second_passthrough_drug_offset_amount: float
    """Amount built into the APC payment for certain drugs"""

    third_passthrough_drug_offset_amount: float
    """Amount built into the APC payment for certain drugs"""

    first_device_offset_amount: float
    """Amount built into the APC payment for certain devices"""

    second_device_offset_amount: float
    """Amount built into the APC payment for certain devices"""

    full_or_partial_device_credit_offset_amount: float
    """Credit for devices that are supplied for free or at a reduced cost"""

    terminated_device_procedure_offset_amount: float
    """Credit for devices that are not used due to a terminated procedure"""


class RuralIndicator(str, Enum):
    RURAL = "R"
    SUPER_RURAL = "B"
    URBAN = ""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        def from_int(value: int) -> RuralIndicator:
            if value == 82:
                return RuralIndicator.RURAL
            elif value == 66:
                return RuralIndicator.SUPER_RURAL
            elif value == 32:
                return RuralIndicator.URBAN
            else:
                raise ValueError(f"Unknown rural indicator value: {value}")

        def to_int(instance: RuralIndicator) -> int:
            if instance == RuralIndicator.RURAL:
                return 82
            elif instance == RuralIndicator.SUPER_RURAL:
                return 66
            elif instance == RuralIndicator.URBAN:
                return 32
            else:
                raise ValueError(f"Unknown rural indicator: {instance}")

        from_int_schema = core_schema.chain_schema(
            [
                core_schema.int_schema(),
                core_schema.no_info_plain_validator_function(from_int),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_int_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(RuralIndicator),
                    from_int_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(to_int),
        )


class ProviderDetail(BaseModel):
    """
    ProviderDetail contains basic information about the provider and/or locality used for pricing.
    Not all fields are returned with every pricing request. For example, the CMS Certification
    Number (CCN) is only returned for facilities which have a CCN such as hospitals.
    """

    model_config = camel_case_model_config

    ccn: Optional[str] = None
    """CMS Certification Number for the facility"""

    mac: Optional[int] = None
    """Medicare Administrative Contractor number"""

    locality: Optional[int] = None
    """Geographic locality number used for pricing"""

    rural_indicator: Optional[RuralIndicator] = None
    """Indicates whether provider is Rural (R), Super Rural (B), or Urban (blank)"""

    specialty_type: Optional[str] = None
    """Medicare provider specialty type"""

    hospital_type: Optional[HospitalType] = None
    """Type of hospital"""


class ClaimEdits(BaseModel):
    """ClaimEdits contains errors which cause the claim to be denied, rejected, suspended, or returned to the provider."""

    model_config = camel_case_model_config

    claim_overall_disposition: Optional[str] = None
    claim_rejection_disposition: Optional[str] = None
    claim_denial_disposition: Optional[str] = None
    claim_return_to_provider_disposition: Optional[str] = None
    claim_suspension_disposition: Optional[str] = None
    line_item_rejection_disposition: Optional[str] = None
    line_item_denial_disposition: Optional[str] = None
    claim_rejection_reasons: Optional[list[str]] = None
    claim_denial_reasons: Optional[list[str]] = None
    claim_return_to_provider_reasons: Optional[list[str]] = None
    claim_suspension_reasons: Optional[list[str]] = None
    line_item_rejection_reasons: Optional[list[str]] = None
    line_item_denial_reasons: Optional[list[str]] = None


class Pricing(BaseModel):
    """Pricing contains the results of a pricing request"""

    model_config = camel_case_model_config

    claim_id: Optional[str] = None
    """The unique identifier for the claim (copied from input)"""

    medicare_amount: Optional[float] = None
    """The amount Medicare would pay for the service"""

    allowed_amount: Optional[float] = None
    """The allowed amount based on a contract or RBP pricing"""

    allowed_calculation_error: Optional[str] = None
    """The reason the allowed amount was not calculated"""

    medicare_repricing_code: Optional[ClaimRepricingCode] = None
    """Explains the methodology used to calculate Medicare (MED or IFO)"""

    medicare_repricing_note: Optional[str] = None
    """Note explaining approach for pricing or reason for error"""

    allowed_repricing_code: Optional[ClaimRepricingCode] = None
    """Explains the methodology used to calculate allowed amount (CON, RBP, SCA, or IFO)"""

    allowed_repricing_note: Optional[str] = None
    """Note explaining approach for pricing or reason for error"""

    medicare_std_dev: Optional[float] = None
    """The standard deviation of the estimated Medicare amount (estimates service only)"""

    medicare_source: Optional[str] = None
    """Source of the Medicare amount (e.g. physician fee schedule, OPPS, etc.)"""

    inpatient_price_detail: Optional[InpatientPriceDetail] = None
    """Details about the inpatient pricing"""

    outpatient_price_detail: Optional[OutpatientPriceDetail] = None
    """Details about the outpatient pricing"""

    provider_detail: Optional[ProviderDetail] = None
    """The provider details used when pricing the claim"""

    edit_detail: Optional[ClaimEdits] = None
    """Errors which cause the claim to be denied, rejected, suspended, or returned to the provider"""

    pricer_result: Optional[str] = None
    """Pricer return details"""

    services: Optional[list[Service]] = None
    """ricing for each service line on the claim"""

    edit_error: Optional[ResponseError] = None
    """An error that occurred during some step of the pricing process"""


class LineEdits(BaseModel):
    """LineEdits contains errors which cause the line item to be unable to be priced."""

    model_config = camel_case_model_config

    denial_or_rejection_text: str
    procedure_edits: list[str]
    modifier1_edits: list[str]
    modifier2_edits: list[str]
    modifier3_edits: list[str]
    modifier4_edits: list[str]
    modifier5_edits: list[str]
    data_edits: list[str]
    revenue_edits: list[str]
    professional_edits: list[str]


class PricedService(BaseModel):
    """PricedService contains the results of a pricing request for a single service line"""

    model_config = camel_case_model_config

    line_number: str
    """Number of the service line item (copied from input)"""

    provider_detail: Optional[ProviderDetail] = None
    """Provider Details used when pricing the service if different than the claim"""

    medicare_amount: float
    """Amount Medicare would pay for the service"""

    allowed_amount: float
    """Allowed amount based on a contract or RBP pricing"""

    allowed_calculation_error: str
    """Reason the allowed amount was not calculated"""

    repricing_code: LineRepricingCode
    """Explains the methodology used to calculate Medicare"""

    repricing_note: str
    """Note explaining approach for pricing or reason for error"""

    technical_component_amount: float
    """Amount Medicare would pay for the technical component"""

    professional_component_amount: float
    """Amount Medicare would pay for the professional component"""

    medicare_std_dev: float
    """Standard deviation of the estimated Medicare amount (estimates service only)"""

    medicare_source: str
    """Source of the Medicare amount (e.g. physician fee schedule, OPPS, etc.)"""

    pricer_result: str
    """Pricing service return details"""

    status_indicator: str
    """Code which gives more detail about how Medicare pays for the service"""

    payment_indicator: str
    """Text which explains the type of payment for Medicare"""

    payment_apc: str
    """Ambulatory Payment Classification"""

    edit_detail: Optional[LineEdits] = None
    """Errors which cause the line item to be unable to be priced"""
