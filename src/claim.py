from enum import Enum, IntEnum

from pydantic import BaseModel

from .date import Date


# Ask if we really want arbitrary precision in our API or not.
class DECIMALTODO:
    pass


class FormType(str, Enum):
    """Type of form used to submit the claim. Can be HCFA or UB-04 (from CLM05_02)"""

    HCFA = "HCFA"
    UB_04 = "UB-04"


class BillTypeSequence(str, Enum):
    """Where the claim is at in its billing lifecycle (e.g. 0: Non-Pay, 1: Admit Through
    Discharge, 7: Replacement, etc.) (from CLM05_03)
    """

    NonPay = "G"
    AdmitThroughDischarge = "H"
    FirstInterim = "I"
    ContinuingInterim = "J"
    LastInterim = "K"
    LateCharge = "M"
    FirstInterimDeprecated = "P"
    Replacement = "Q"
    VoidOrCancel = "0"
    FinalClaim = "1"
    CWFAdjustment = "2"
    CMSAdjustment = "3"
    IntermediaryAdjustment = "4"
    OtherAdjustment = "5"
    OIGAdjustment = "6"
    MSPAdjustment = "7"
    QIOAdjustment = "8"
    ProviderAdjustment = "9"


class SexType(IntEnum):
    """Biological sex of the patient for clinical purposes"""

    Unknown = 0
    Male = 1
    Female = 2


class Provider(BaseModel):
    npi: str
    """National Provider Identifier of the provider (from NM109, required)"""

    provider_tax_id: str
    """City of the provider (from N401, highly recommended)"""

    provider_phones: list[str]
    """Address line 1 of the provider (from N301, highly recommended)"""

    provider_faxes: list[str]
    """Commercial number of the provider used by some payers (from REF G2, optional)"""

    provider_emails: list[str]
    """State license number of the provider (from REF 0B, optional)"""

    provider_license_number: str
    """Last name of the provider (from NM103, highly recommended)"""

    provider_commercial_number: str
    """Email addresses of the provider (from PER, optional)"""

    provider_taxonomy: str
    """State of the provider (from N402, highly recommended)"""

    provider_first_name: str
    """Taxonomy code of the provider (from PRV03, highly recommended)"""

    provider_last_name: str
    """First name of the provider (NM104, highly recommended)"""

    provider_org_name: str
    """Organization name of the provider (from NM103, highly recommended)"""

    provider_address1: str
    """Tax ID of the provider (from REF highly recommended)"""

    provider_address2: str
    """Phone numbers of the provider (from PER, optional)"""

    provider_city: str
    """Fax numbers of the provider (from PER, optional)"""

    provider_state: str
    """Address line 2 of the provider (from N302, optional)"""

    provider_zip: str
    """ZIP code of the provider (from N403, required)"""


class ValueCode(BaseModel):
    """Code indicating the type of value provided (from HIxx_02)"""

    code: str

    """Amount associated with the value code (from HIxx_05)"""
    amount: DECIMALTODO


class Diagnosis(BaseModel):
    """Principal ICD diagnosis for the patient (from HI ABK or BK)"""

    code: str
    """ICD code for the diagnosis"""

    description: str
    """Description of the diagnosis"""


class Service(Provider, BaseModel):
    line_number: str
    """Unique line number for the service item (from LX01)"""

    rev_code: str
    """Revenue code (from SV2_01)"""

    procedure_code: str
    """Procedure code (from SV101_02 / SV202_02)"""

    procedure_modifiers: str
    """Procedure modifiers (from SV101_03, 4, 5, 6 / SV202_03, 4, 5, 6)"""

    drug_code: str
    """National Drug Code (from LIN03)"""

    date_from: Date
    """Begin date of service (from DTP 472)"""

    date_through: Date
    """End date of service (from DTP 472)"""

    billed_amount: float
    """Billed charge for the service (from SV102 / SV203)"""

    allowed_amount: float
    """Plan allowed amount for the service (non-EDI)"""

    paid_amount: float
    """Plan paid amount for the service (non-EDI)"""

    quantity: float
    """Quantity of the service (from SV104 / SV205)"""

    units: str
    """Units connected to the quantity given (from SV103 / SV204)"""

    place_of_service: str
    """Place of service code (from SV105)"""

    diagnosis_pointers: list[int]
    """Diagnosis pointers (from SV107)"""

    ambulance_pickup_zip: str
    """ZIP code where ambulance picked up patient. Supplied if different than claim-level value (from NM1 PW)"""


class Claim(Provider, BaseModel):
    claim_id: str
    """Unique identifier for the claim (from REF D9)"""

    plan_code: str
    """Identifies the subscriber's plan (from SBR03)"""

    patient_sex: SexType
    """Biological sex of the patient for clinical purposes (from DMG02). 0:Unknown, 1:Male,
    2:Female
    """

    patient_date_of_birth: Date
    """Patient date of birth (from DMG03)"""

    patient_height_in_cm: float
    """Patient height in centimeters (from HI value A9, MEA value HT)"""

    patient_weight_in_kg: float
    """Patient weight in kilograms (from HI value A8, PAT08, CR102 [ambulance only])"""

    ambulance_pickup_zip: str
    """Location where patient was picked up in ambulance (from HI with HIxx_01=BE and HIxx_02=A0
    or NM1 loop with NM1 PW)
    """

    form_type: FormType
    """Type of form used to submit the claim. Can be HCFA or UB-04 (from CLM05_02)"""

    bill_type_or_pos: str
    """Describes type of facility where services were rendered (from CLM05_01)"""

    bill_type_sequence: BillTypeSequence
    """Where the claim is at in its billing lifecycle (e.g. 0: Non-Pay, 1: Admit Through
    Discharge, 7: Replacement, etc.) (from CLM05_03)
    """

    billed_amount: float
    """Billed amount from provider (from CLM02)"""

    allowed_amount: float
    """Amount allowed by the plan for payment. Both member and plan responsibility (non-EDI)"""

    paid_amount: float
    """Amount paid by the plan for the claim (non-EDI)"""

    date_from: Date
    """Earliest service date among services, or statement date if not found"""

    date_through: Date
    """Latest service date among services, or statement date if not found"""

    discharge_status: str
    """Status of the patient at time of discharge (from CL103)"""

    admit_diagnosis: str
    """ICD diagnosis at the time the patient was admitted (from HI ABJ or BJ)"""

    principal_diagnosis: Diagnosis | None
    """Principal ICD diagnosis for the patient (from HI ABK or BK)"""

    other_diagnoses: list[Diagnosis]
    """Other ICD diagnoses that apply to the patient (from HI ABF or BF)"""

    principal_procedure: str
    """Principal ICD procedure for the patient (from HI BBR or BR)"""

    other_procedures: list[str]
    """Other ICD procedures that apply to the patient (from HI BBQ or BQ)"""

    condition_codes: list[str]
    """Special conditions that may affect payment or other processing (from HI BG)"""

    value_codes: list[ValueCode]
    """Numeric values related to the patient or claim (HI BE)"""

    occurrence_codes: list[str]
    """Date related occurrences related to the patient or claim (from HI BH)"""

    drg: str
    """Diagnosis Related Group for inpatient services (from HI DR)"""

    services: list[Service]
    """One or more services provided to the patient (from LX loop)"""


class RateSheetService(BaseModel):
    procedure_code: str
    """Procedure code (from SV101_02 / SV202_02)"""

    procedure_modifiers: list[str]
    """Procedure modifiers (from SV101_03, 4, 5, 6 / SV202_03, 4, 5, 6)"""

    billed_amount: float
    """Billed charge for the service (from SV102 / SV203)"""

    allowed_amount: float
    """Plan allowed amount for the service (non-EDI)"""


class RateSheet(BaseModel):
    npi: str
    """National Provider Identifier of the provider (from NM109, required)"""

    provider_first_name: str
    """First name of the provider (NM104, highly recommended)"""

    provider_last_name: str
    """Last name of the provider (from NM103, highly recommended)"""

    provider_org_name: str
    """Organization name of the provider (from NM103, highly recommended)"""

    provider_address: str
    """Address of the provider (from N301, highly recommended)"""

    provider_city: str
    """City of the provider (from N401, highly recommended)"""

    provider_state: str
    """State of the provider (from N402, highly recommended)"""

    provider_zip: str
    """ZIP code of the provider (from N403, required)"""

    form_type: FormType
    """pe of form used to submit the claim. Can be HCFA or UB-04 (from CLM05_02)"""

    bill_type_or_pos: str
    """Describes type of facility where services were rendered (from CLM05_01)"""

    drg: str
    """Diagnosis Related Group for inpatient services (from HI DR)"""

    billed_amount: float
    """illed amount from provider (from CLM02)"""

    allowed_amount: float
    """mount allowed by the plan for payment. Both member and plan responsibility (non-EDI)"""

    paid_amount: float
    """mount paid by the plan for the claim (non-EDI)"""

    services: list[RateSheetService]
    """One or more services provided to the patient (from LX loop)"""
