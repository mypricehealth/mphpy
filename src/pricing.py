from enum import Enum

from pydantic import BaseModel

from .claim import Service
from .response import ResponseError


# TODO CHECK
class Byte:
    pass


class ClaimRepricingCode(str, Enum):
    """claim-level repricing codes"""

    Medicare = "MED"
    ContractPricing = "CON"
    RBPPricing = "RBP"
    SingleCaseAgreement = "SCA"
    NeedsMoreInfo = "IFO"


class LineRepricingCode(str, Enum):
    # line-level Medicare repricing codes
    Medicare = "MED"
    SyntheticMedicare = "SYN"
    CostPercent = "CST"
    MedicarePercent = "MPT"
    MedicareNoOutlier = "MNO"
    BilledPercent = "BIL"
    FeeSchedule = "FSC"
    PerDiem = "PDM"
    FlatRate = "FLT"
    LimitedToBilled = "LTB"

    # line-level zero dollar repricing explanations
    NotAllowedByMedicare = "NAM"
    Packaged = "PKG"
    NeedsMoreInfo = "IFO"
    ProcedureCodeProblem = "CPB"
    NotRepricedPerRequest = "NRP"


class HospitalType(str, Enum):
    AcuteCare = "Acute Care Hospitals"
    CriticalAccess = "Critical Access Hospitals"
    Childrens = "Childrens"
    Psychiatric = "Psychiatric"
    AcuteCareDOD = "Acute Care - Department of Defense"


class InpatientPriceDetail(BaseModel):
    """InpatientPriceDetail contains pricing details for an inpatient claim"""

    drg: str
    """Diagnosis Related Group (DRG) code used to price the claim"""

    drg_amount: float
    """Amount Medicare would pay for the DRG"""

    passthrough_amount: float
    """Per diem amount to cover capital-related costs, direct medical education, and other costs"""

    outlier_amount: float
    """Additional amount paid for high cost cases"""

    indirect_medical_education_amount: float
    """Additional amount paid for teaching hospitals"""

    disproportionate_share_amount: float
    """Additional amount paid for hospitals with a high number of low-income patients"""

    uncompensated_care_amount: float
    """Additional amount paid for patients who are unable to pay for their care"""

    readmission_adjustment_amount: float
    """Adjustment amount for hospitals with high readmission rates"""

    value_based_purchasing_amount: float
    """Adjustment for hospitals based on quality measures"""


class OutpatientPriceDetail(BaseModel):
    """OutpatientPriceDetail contains pricing details for an outpatient claim"""

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


class ProviderDetail(BaseModel):
    """
    ProviderDetail contains basic information about the provider and/or locality used for pricing.
    Not all fields are returned with every pricing request. For example, the CMS Certification
    Number (CCN) is only returned for facilities which have a CCN such as hospitals.
    """

    ccn: str
    """CMS Certification Number for the facility"""

    mac: int
    """Medicare Administrative Contractor number"""

    locality: int
    """Geographic locality number used for pricing"""

    rural_indicator: Byte
    """Indicates whether provider is Rural (R), Super Rural (B), or Urban (blank)"""

    specialty_type: str
    """Medicare provider specialty type"""

    hospital_type: HospitalType
    """Type of hospital"""


class ClaimEdits(BaseModel):
    """ClaimEdits contains errors which cause the claim to be denied, rejected, suspended, or returned to the provider."""

    ClaimOverallDisposition: str
    ClaimRejectionDisposition: str
    ClaimDenialDisposition: str
    ClaimReturnToProviderDisposition: str
    ClaimSuspensionDisposition: str
    LineItemRejectionDisposition: str
    LineItemDenialDisposition: str
    ClaimRejectionReasons: list[str]
    ClaimDenialReasons: list[str]
    ClaimReturnToProviderReasons: list[str]
    ClaimSuspensionReasons: list[str]
    LineItemRejectionReasons: list[str]
    LineItemDenialReasons: list[str]


class Pricing(BaseModel):
    """Pricing contains the results of a pricing request"""

    claim_id: str
    """The unique identifier for the claim (copied from input)"""

    medicare_amount: float
    """The amount Medicare would pay for the service"""

    allowed_amount: float
    """The allowed amount based on a contract or RBP pricing"""

    allowed_calculation_error: str
    """The reason the allowed amount was not calculated"""

    medicare_repricing_code: ClaimRepricingCode
    """Explains the methodology used to calculate Medicare (MED or IFO)"""

    medicare_repricing_note: str
    """Note explaining approach for pricing or reason for error"""

    allowed_repricing_code: ClaimRepricingCode
    """Explains the methodology used to calculate allowed amount (CON, RBP, SCA, or IFO)"""

    allowed_repricing_note: str
    """Note explaining approach for pricing or reason for error"""

    medicare_std_dev: float
    """The standard deviation of the estimated Medicare amount (estimates service only)"""

    medicare_source: str
    """Source of the Medicare amount (e.g. physician fee schedule, OPPS, etc.)"""

    inpatient_price_detail: InpatientPriceDetail | None
    """Details about the inpatient pricing"""

    outpatient_price_detail: OutpatientPriceDetail | None
    """Details about the outpatient pricing"""

    provider_detail: ProviderDetail | None
    """The provider details used when pricing the claim"""

    edit_detail: ClaimEdits | None
    """Errors which cause the claim to be denied, rejected, suspended, or returned to the provider"""

    pricer_result: str
    """Pricer return details"""

    services: list[Service]
    """ricing for each service line on the claim"""

    edit_error: ResponseError | None
    """An error that occurred during some step of the pricing process"""


class LineEdits(BaseModel):
    """LineEdits contains errors which cause the line item to be unable to be priced."""

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

    line_number: str
    """Number of the service line item (copied from input)"""

    provider_detail: ProviderDetail | None
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

    edit_detail: LineEdits | None
    """Errors which cause the line item to be unable to be priced"""
