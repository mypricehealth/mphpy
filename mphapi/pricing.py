from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, Field

from .client import PriceConfig
from .fields import camel_case_model_config, field_name
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
    MEDICARE_PERCENT = "MPT"
    MEDICARE_NO_OUTLIER = "MNO"
    SYNTHETIC_MEDICARE = "SYN"
    BILLED_PERCENT = "BIL"
    FEE_SCHEDULE = "FSC"
    PER_DIEM = "PDM"
    FLAT_RATE = "FLT"
    COST_PERCENT = "CST"
    LIMITED_TO_BILLED = "LTB"

    # line-level zero dollar repricing explanations
    NOT_REPRICED_PER_REQUEST = "NRP"
    NOT_ALLOWED_BY_MEDICARE = "NAM"
    PACKAGED = "PKG"
    NEEDS_MORE_INFO = "IFO"
    PROCEDURE_CODE_PROBLEM = "CPB"


class HospitalType(str, Enum):
    ACUTE_CARE = "Acute Care Hospitals"
    CRITICAL_ACCESS = "Critical Access Hospitals"
    CHILDRENS = "Childrens"
    PSYCHIATRIC = "Psychiatric"
    ACUTE_CARE_DOD = "Acute Care - Department of Defense"


class RuralIndicator(str, Enum):
    RURAL = "R"
    SUPER_RURAL = "B"
    URBAN = ""


class MedicareSource(str, Enum):
    Ambulance = "AmbulanceFS"
    Anesthesia = "AnesthesiaFS"
    ASC = "ASC pricer"
    CriticalAccessHospital = "CAH pricer"
    DMEFS = "DMEFS"
    Drugs = "DrugsFS"
    EditError = "Claim editor"
    EstimateByCodeOnly = "CodeOnly"
    EstimateByLocalityCode = "LocalityCode"
    EstimateByLocalityOnly = "LocalityOnly"
    EstimateByNational = "National"
    EstimateByStateCode = "StateCode"
    EstimateByStateOnly = "StateOnly"
    EstimateByUnknown = "Unknown"
    Inpatient = "IPPS"
    Labs = "LabsFS"
    MPFS = "MPFS"
    Outpatient = "Outpatient pricer"
    ManualPricing = "Manual Pricing"
    SNF = "SNF PPS"
    Synthetic = "Synthetic Medicare"


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

    wage_index: Optional[float] = None
    """Wage index used for geographic adjustment"""


class OutpatientPriceDetail(BaseModel):
    """OutpatientPriceDetail contains pricing details for an outpatient claim"""

    model_config = camel_case_model_config

    outlier_amount: Optional[float] = None
    """Additional amount paid for high cost cases"""

    first_passthrough_drug_offset_amount: Optional[float] = None
    """Amount built into the APC payment for certain drugs"""

    second_passthrough_drug_offset_amount: Optional[float] = None
    """Amount built into the APC payment for certain drugs"""

    third_passthrough_drug_offset_amount: Optional[float] = None
    """Amount built into the APC payment for certain drugs"""

    first_device_offset_amount: Optional[float] = None
    """Amount built into the APC payment for certain devices"""

    second_device_offset_amount: Optional[float] = None
    """Amount built into the APC payment for certain devices"""

    full_or_partial_device_credit_offset_amount: Optional[float] = None
    """Credit for devices that are supplied for free or at a reduced cost"""

    terminated_device_procedure_offset_amount: Optional[float] = None
    """Credit for devices that are not used due to a terminated procedure"""

    wage_index: Optional[float] = None
    """Wage index used for geographic adjustment"""


class AllowedRepricingFormula(BaseModel):
    """The formula used to calculate the allowed amount"""

    medicare_percent: Optional[float] = None
    """Percentage of the Medicare amount used to calculate the allowed amount"""

    billed_percent: Optional[float] = None
    """Percentage of the billed amount used to calculate the allowed amount"""

    fee_schedule: Optional[float] = None
    """Fee schedule amount used as the allowed amount"""

    fixed_amount: Optional[float] = None
    """Fixed amount used as the allowed amount"""

    per_diem: Optional[float] = None
    """Per diem rate used to calculate the allowed amount"""


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

    geographic_cbsa: Annotated[Optional[int], field_name("geographicCBSA")] = None
    """Core-Based Statistical Area (CBSA) number for provider ZIP"""

    state_cbsa: Annotated[Optional[int], field_name("stateCBSA")] = None
    """State Core-Based Statistical Area (CBSA) number"""

    rural_indicator: Optional[RuralIndicator] = None
    """Indicates whether provider is Rural (R), Super Rural (B), or Urban (blank)"""

    specialty_type: Optional[str] = None
    """Medicare provider specialty type"""

    hospital_type: Optional[HospitalType] = None
    """Type of hospital"""


class ClaimEdits(BaseModel):
    """ClaimEdits contains errors which cause the claim to be denied, rejected, suspended, or returned to the provider."""

    model_config = camel_case_model_config

    hcp_deny_code: Optional[str] = None
    """The deny code that will be placed into the HCP13 data element for EDI 837 claims"""

    claim_overall_disposition: Optional[str] = None
    """Overall explanation of why the claim edit failed"""

    claim_rejection_disposition: Optional[str] = None
    """Explanation of why the claim was rejected"""

    claim_denial_disposition: Optional[str] = None
    """Explanation of why the claim was denied"""

    claim_return_to_provider_disposition: Optional[str] = None
    """Explanation of why the claim should be returned to provider"""

    claim_suspension_disposition: Optional[str] = None
    """Explanation of why the claim was suspended"""

    line_item_rejection_disposition: Optional[str] = None
    """Explanation of why the line item was rejected"""

    line_item_denial_disposition: Optional[str] = None
    """Explanation of why the line item was denied"""

    claim_rejection_reasons: Optional[list[str]] = None
    """Detailed reason(s) describing why the claim was rejected"""

    claim_denial_reasons: Optional[list[str]] = None
    """Detailed reason(s) describing why the claim was denied"""

    claim_return_to_provider_reasons: Optional[list[str]] = None
    """Detailed reason(s) describing why the claim should be returned to provider"""

    claim_suspension_reasons: Optional[list[str]] = None
    """Detailed reason(s) describing why the claim was suspended"""

    line_item_rejection_reasons: Optional[list[str]] = None
    """Detailed reason(s) describing why the line item was rejected"""

    line_item_denial_reasons: Optional[list[str]] = None
    """Detailed reason(s) describing why the line item was denied"""


class LineEdits(BaseModel):
    """LineEdits contains errors which cause the line item to be unable to be priced."""

    model_config = camel_case_model_config

    procedure_edits: Optional[list[str]] = None
    """Detailed description of each procedure code edit error (from outpatient editor)"""

    modifier1_edits: Optional[list[str]] = None
    """Detailed description of each edit error for the first procedure code modifier (from outpatient editor)"""

    modifier2_edits: Optional[list[str]] = None
    """Detailed description of each edit error for the second procedure code modifier (from outpatient editor)"""

    modifier3_edits: Optional[list[str]] = None
    """Detailed description of each edit error for the third procedure code modifier (from outpatient editor)"""

    modifier4_edits: Optional[list[str]] = None
    """Detailed description of each edit error for the fourth procedure code modifier (from outpatient editor)"""

    modifier5_edits: Optional[list[str]] = None
    """Detailed description of each edit error for the fifth procedure code modifier (from outpatient editor)"""

    data_edits: Optional[list[str]] = None
    """Detailed description of each data edit error (from outpatient editor)"""

    revenue_edits: Optional[list[str]] = None
    """Detailed description of each revenue code edit error (from outpatient editor)"""


class PricedService(BaseModel):
    """PricedService contains the results of a pricing request for a single service line"""

    model_config = camel_case_model_config

    line_number: Optional[str] = None
    """Number of the service line item (copied from input)"""

    provider_detail: Optional[ProviderDetail] = None
    """Provider Details used when pricing the service if different than the claim"""

    medicare_amount: Optional[float] = None
    """Amount Medicare would pay for the service"""

    allowed_amount: Optional[float] = None
    """Allowed amount based on a contract or RBP pricing"""

    medicare_repricing_code: Optional[LineRepricingCode] = None
    """Explains the methodology used to calculate Medicare"""

    medicare_repricing_note: Optional[str] = None
    """Note explaining approach for pricing or reason for error"""

    network_code: Optional[str] = None
    """Code describing the network used for allowed amount pricing"""

    allowed_repricing_code: Optional[LineRepricingCode] = None
    """Explains the methodology used to calculate allowed amount"""

    allowed_repricing_note: Optional[str] = None
    """Note explaining approach for pricing or reason for error"""

    allowed_repricing_formula: Optional[AllowedRepricingFormula] = None
    """Formula used to calculate the allowed amount"""

    technical_component_amount: Optional[float] = None
    """Amount Medicare would pay for the technical component"""

    professional_component_amount: Optional[float] = None
    """Amount Medicare would pay for the professional component"""

    medicare_std_dev: Optional[float] = None
    """Standard deviation of the estimated Medicare amount (estimates service only)"""

    medicare_source: Optional[MedicareSource] = None
    """Source of the Medicare amount (e.g. physician fee schedule, OPPS, etc.)"""

    pricer_result: Optional[str] = None
    """Pricing service return details"""

    status_indicator: Optional[str] = None
    """Code which gives more detail about how Medicare pays for the service"""

    payment_indicator: Optional[str] = None
    """Text which explains the type of payment for Medicare"""

    discount_formula: Optional[str] = None
    """The multi-procedure discount formula used to calculate the allowed amount (outpatient only)"""

    line_item_denial_or_rejection_flag: Optional[str] = None
    """Identifies how a line item was denied or rejected and how the rejection can be overridden (outpatient only)"""

    packaging_flag: Optional[str] = None
    """Indicates if the service is packaged and the reason for packaging (outpatient only)"""

    payment_adjustment_flag: Optional[str] = None
    """Identifies special adjustments made to the payment (outpatient only)"""

    payment_adjustment_flag2: Optional[str] = None
    """Identifies special adjustments made to the payment (outpatient only)"""

    payment_method_flag: Optional[str] = None
    """The method used to calculate the allowed amount (outpatient only)"""

    composite_adjustment_flag: Optional[str] = None
    """Assists in composite APC determination (outpatient only)"""

    hcpcs_apc: Annotated[Optional[str], field_name("hcpcsAPC")] = None
    """Ambulatory Payment Classification code of the line item HCPCS (outpatient only)"""

    payment_apc: Annotated[Optional[str], field_name("paymentAPC")] = None
    """Ambulatory Payment Classification"""

    edit_detail: Optional[LineEdits] = None
    """Errors which cause the line item to be unable to be priced"""


class Pricing(BaseModel):
    """Pricing contains the results of a pricing request"""

    model_config = camel_case_model_config

    claim_id: Annotated[Optional[str], field_name(alias="claimID")] = None
    """The unique identifier for the claim (copied from input)"""

    medicare_amount: Optional[float] = None
    """The amount Medicare would pay for the service"""

    allowed_amount: Optional[float] = None
    """The allowed amount based on a contract or RBP pricing"""

    medicare_repricing_code: Optional[ClaimRepricingCode] = None
    """Explains the methodology used to calculate Medicare (MED or IFO)"""

    medicare_repricing_note: Optional[str] = None
    """Note explaining approach for pricing or reason for error"""

    network_code: Optional[str] = None
    """Code describing the network used for allowed amount pricing"""

    allowed_repricing_code: Optional[ClaimRepricingCode] = None
    """Explains the methodology used to calculate allowed amount (CON, RBP, SCA, or IFO)"""

    allowed_repricing_note: Optional[str] = None
    """Note explaining approach for pricing or reason for error"""

    medicare_std_dev: Optional[float] = None
    """The standard deviation of the estimated Medicare amount (estimates service only)"""

    medicare_source: Optional[MedicareSource] = None
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

    price_config: Optional[PriceConfig] = None
    """The configuration used for pricing the claim"""

    services: list[PricedService] = Field(min_length=1)
    """Pricing for each service line on the claim"""

    edit_error: Optional[ResponseError] = None
    """An error that occurred during some step of the pricing process"""


class Step(str, Enum):
    new = "New"
    received = "Received"
    pending = "Pending"
    held = "Held"
    error = "Error"
    input_validated = "Input Validated"
    provider_matched = "Provider Matched"
    edit_complete = "Edit Complete"
    medicare_priced = "Medicare Priced"
    primary_allowed_priced = "Primary Allowed Priced"
    network_allowed_priced = "Network Allowed Priced"
    out_of_network = "Out of Network"
    request_more_info = "Request More Info"
    priced = "Priced"
    returned = "Returned"


class Status(str, Enum):
    pending_claim_input_validation = "Claim Input Validation"
    pending_claim_edit_review = "Claim Edit Review"
    pending_provider_matching = "Provider Matching"
    pending_medicare_review = "Medicare Review"
    pending_medicare_calculation = "Medicare Calculation"
    pending_primary_allowed_review = "Primary Allowed Review"
    pending_network_allowed_review = "Network Allowed Review"
    pending_primary_allowed_determination = "Primary Allowed Determination"
    pending_network_allowed_determination = "Network Allowed Determination"


class StepAndStatus(BaseModel):
    model_config = camel_case_model_config

    step: Step
    status: Optional[Status] = None


class ClaimStatus(StepAndStatus):
    model_config = camel_case_model_config

    pricing: Optional[Pricing] = None
    error: Optional[ResponseError] = None


status_new = StepAndStatus(step=Step.new)
"""created by TPA. We use the transaction date as a proxy for this date"""

status_received = StepAndStatus(step=Step.received)
"""received and ready for processing. This is modified date of the file we get from SFTP"""

status_held = StepAndStatus(step=Step.held)
"""held for various reasons"""

status_error = StepAndStatus(step=Step.error)
"""claim encountered an error during processing"""

status_input_validated = StepAndStatus(step=Step.input_validated)
"""claim input has been validated"""

status_provider_matched = StepAndStatus(step=Step.provider_matched)
"""providers in the claim have been matched to the provider system of record"""

status_edit_complete = StepAndStatus(step=Step.edit_complete)
"""claim has been edited and is ready for pricing"""

status_medicare_priced = StepAndStatus(step=Step.medicare_priced)
"""claim has been priced according to Medicare"""

status_primary_allowed_priced = StepAndStatus(step=Step.primary_allowed_priced)
"""claim has been priced according to the primary allowed amount (e.g. contract, RBP, etc.)"""

status_network_allowed_priced = StepAndStatus(step=Step.network_allowed_priced)
"""claim has been priced according to the allowed amount of the network"""

status_out_of_network = StepAndStatus(step=Step.out_of_network)
"""is out of network"""

status_request_more_info = StepAndStatus(step=Step.request_more_info)
"""return claim to trading partner for more information to enable correct processing"""

status_priced = StepAndStatus(step=Step.priced)
"""done pricing"""

status_returned = StepAndStatus(step=Step.returned)
"""returned to TPA"""

status_pending_claim_input_validation = StepAndStatus(
    step=Step.pending, status=Status.pending_claim_input_validation
)
"""waiting for claim input validation"""

status_pending_claim_edit_review = StepAndStatus(
    step=Step.pending, status=Status.pending_claim_edit_review
)
"""waiting for claim edit review"""

status_pending_provider_matching = StepAndStatus(
    step=Step.pending, status=Status.pending_provider_matching
)
"""waiting for provider matching"""

status_pending_medicare_review = StepAndStatus(
    step=Step.pending, status=Status.pending_medicare_review
)
"""waiting for Medicare amount review"""

status_pending_medicare_calculation = StepAndStatus(
    step=Step.pending, status=Status.pending_medicare_calculation
)
"""waiting for Medicare amount calculation"""

status_pending_primary_allowed_review = StepAndStatus(
    step=Step.pending, status=Status.pending_primary_allowed_review
)
"""waiting for primary allowed amount review"""

status_pending_network_allowed_review = StepAndStatus(
    step=Step.pending, status=Status.pending_network_allowed_review
)
"""waiting for network allowed amount review"""

status_pending_primary_allowed_determination = StepAndStatus(
    step=Step.pending, status=Status.pending_primary_allowed_determination
)
"""waiting for the primary allowed amount (e.g. contract, RBP rate, etc.) to be determined"""

status_pending_network_allowed_determination = StepAndStatus(
    step=Step.pending, status=Status.pending_network_allowed_determination
)
"""waiting for allowed amount from the network"""
