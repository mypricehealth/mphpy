from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, Field

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
    CriticalAccessHospital = "CAH pricer"
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

    claim_overall_disposition: Optional[str] = None              # Overall explanation of why the claim edit failed
    claim_rejection_disposition: Optional[str] = None            # Explanation of why the claim was rejected
    claim_denial_disposition: Optional[str] = None               # Explanation of why the claim was denied
    claim_return_to_provider_disposition: Optional[str] = None   # Explanation of why the claim should be returned to provider
    claim_suspension_disposition: Optional[str] = None           # Explanation of why the claim was suspended
    line_item_rejection_disposition: Optional[str] = None        # Explanation of why the line item was rejected
    line_item_denial_disposition: Optional[str] = None           # Explanation of why the line item was denied
    claim_rejection_reasons: Optional[list[str]] = None          # Detailed reason(s) describing why the claim was rejected
    claim_denial_reasons: Optional[list[str]] = None             # Detailed reason(s) describing why the claim was denied
    claim_return_to_provider_reasons: Optional[list[str]] = None # Detailed reason(s) describing why the claim should be returned to provider
    claim_suspension_reasons: Optional[list[str]] = None         # Detailed reason(s) describing why the claim was suspended
    line_item_rejection_reasons: Optional[list[str]] = None      # Detailed reason(s) describing why the line item was rejected
    line_item_denial_reasons: Optional[list[str]] = None         # Detailed reason(s) describing why the line item was denied


class LineEdits(BaseModel):
    """LineEdits contains errors which cause the line item to be unable to be priced."""

    model_config = camel_case_model_config

    denial_or_rejection_text: Optional[str] = None # The overall explanation for why this line item was denied or rejected by the claim editor
    procedure_edits: Optional[list[str]] = None    # Detailed description of each procedure code edit error (from outpatient editor)
    modifier1_edits: Optional[list[str]] = None    # Detailed description of each edit error for the first procedure code modifier (from outpatient editor)
    modifier2_edits: Optional[list[str]] = None    # Detailed description of each edit error for the second procedure code modifier (from outpatient editor)
    modifier3_edits: Optional[list[str]] = None    # Detailed description of each edit error for the third procedure code modifier (from outpatient editor)
    modifier4_edits: Optional[list[str]] = None    # Detailed description of each edit error for the fourth procedure code modifier (from outpatient editor)
    modifier5_edits: Optional[list[str]] = None    # Detailed description of each edit error for the fifth procedure code modifier (from outpatient editor)
    data_edits: Optional[list[str]] = None         # Detailed description of each data edit error (from outpatient editor)
    revenue_edits: Optional[list[str]] = None      # Detailed description of each revenue code edit error (from outpatient editor)
    professional_edits: Optional[list[str]] = None # Detailed description of each professional claim edit error


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

    allowed_repricing_code: Optional[LineRepricingCode] = None
    """Explains the methodology used to calculate allowed amount"""

    allowed_repricing_note: Optional[str] = None
    """Note explaining approach for pricing or reason for error"""

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

    services: list[PricedService] = Field(min_length=1)
    """Pricing for each service line on the claim"""

    edit_error: Optional[ResponseError] = None
    """An error that occurred during some step of the pricing process"""
