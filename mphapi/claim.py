from enum import Enum, IntEnum
from typing import Optional

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .date import Date

camel_case_model_config = ConfigDict(
    alias_generator=AliasGenerator(
        validation_alias=to_camel, serialization_alias=to_camel
    ),
    populate_by_name=True,
)


class FormType(str, Enum):
    """Type of form used to submit the claim. Can be HCFA or UB-04 (from CLM05_02)"""

    HCFA = "HCFA"
    UB_04 = "UB-04"


class BillTypeSequence(str, Enum):
    """Where the claim is at in its billing lifecycle (e.g. 0: Non-Pay, 1: Admit Through
    Discharge, 7: Replacement, etc.) (from CLM05_03)
    """

    NON_PAY = "G"
    ADMIT_THROUGH_DISCHARGE = "H"
    FIRST_INTERIM = "I"
    CONTINUING_INTERIM = "J"
    LAST_INTERIM = "K"
    LATE_CHARGE = "M"
    FIRST_INTERIM_DEPRECATED = "P"
    REPLACEMENT = "Q"
    VOID_OR_CANCEL = "0"
    FINAL_CLAIM = "1"
    CWF_ADJUSTMENT = "2"
    CMS_ADJUSTMENT = "3"
    INTERMEDIARY_ADJUSTMENT = "4"
    OTHER_ADJUSTMENT = "5"
    OIG_ADJUSTMENT = "6"
    MSP_ADJUSTMENT = "7"
    QIO_ADJUSTMENT = "8"
    PROVIDER_ADJUSTMENT = "9"


class SexType(IntEnum):
    """Biological sex of the patient for clinical purposes"""

    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


class Provider(BaseModel):
    model_config = camel_case_model_config

    npi: str
    """National Provider Identifier of the provider (from NM109, required)"""

    provider_tax_id: Optional[str] = None
    """City of the provider (from N401, highly recommended)"""

    provider_phones: Optional[list[str]] = None
    """Address line 1 of the provider (from N301, highly recommended)"""

    provider_faxes: Optional[list[str]] = None
    """Commercial number of the provider used by some payers (from REF G2, optional)"""

    provider_emails: Optional[list[str]] = None
    """State license number of the provider (from REF 0B, optional)"""

    provider_license_number: Optional[str] = None
    """Last name of the provider (from NM103, highly recommended)"""

    provider_commercial_number: Optional[str] = None
    """Email addresses of the provider (from PER, optional)"""

    provider_taxonomy: Optional[str] = None
    """State of the provider (from N402, highly recommended)"""

    provider_first_name: Optional[str] = None
    """Taxonomy code of the provider (from PRV03, highly recommended)"""

    provider_last_name: Optional[str] = None
    """First name of the provider (NM104, highly recommended)"""

    provider_org_name: Optional[str] = None
    """Organization name of the provider (from NM103, highly recommended)"""

    provider_address1: Optional[str] = None
    """Tax ID of the provider (from REF highly recommended)"""

    provider_address2: Optional[str] = None
    """Phone numbers of the provider (from PER, optional)"""

    provider_city: Optional[str] = None
    """Fax numbers of the provider (from PER, optional)"""

    provider_state: Optional[str] = None
    """Address line 2 of the provider (from N302, optional)"""

    provider_zip: str
    """ZIP code of the provider (from N403, required)"""


class ValueCode(BaseModel):
    """Code indicating the type of value provided (from HIxx_02)"""

    model_config = camel_case_model_config

    code: str

    """Amount associated with the value code (from HIxx_05)"""
    amount: float


class Diagnosis(BaseModel):
    """Principal ICD diagnosis for the patient (from HI ABK or BK)"""

    model_config = camel_case_model_config

    code: str
    """ICD code for the diagnosis"""

    description: Optional[str] = None
    """Description of the diagnosis"""


class Service(BaseModel):
    model_config = camel_case_model_config

    provider: Optional[Provider] = None
    """Additional provider information specific to this service item"""

    line_number: Optional[str] = None
    """Unique line number for the service item (from LX01)"""

    rev_code: Optional[str] = None
    """Revenue code (from SV2_01)"""

    procedure_code: Optional[str] = None
    """Procedure code (from SV101_02 / SV202_02)"""

    procedure_modifiers: Optional[str] = None
    """Procedure modifiers (from SV101_03, 4, 5, 6 / SV202_03, 4, 5, 6)"""

    drug_code: Optional[str] = None
    """National Drug Code (from LIN03)"""

    date_from: Optional[Date] = None
    """Begin date of service (from DTP 472)"""

    date_through: Optional[Date] = None
    """End date of service (from DTP 472)"""

    billed_amount: Optional[float] = None
    """Billed charge for the service (from SV102 / SV203)"""

    allowed_amount: Optional[float] = None
    """Plan allowed amount for the service (non-EDI)"""

    paid_amount: Optional[float] = None
    """Plan paid amount for the service (non-EDI)"""

    quantity: Optional[float] = None
    """Quantity of the service (from SV104 / SV205)"""

    units: Optional[str] = None
    """Units connected to the quantity given (from SV103 / SV204)"""

    place_of_service: Optional[str] = None
    """Place of service code (from SV105)"""

    diagnosis_pointers: Optional[list[int]] = None
    """Diagnosis pointers (from SV107)"""

    ambulance_pickup_zip: Optional[str] = None
    """ZIP code where ambulance picked up patient. Supplied if different than claim-level value (from NM1 PW)"""


class Claim(Provider, BaseModel):
    model_config = camel_case_model_config

    claim_id: Optional[str] = None
    """Unique identifier for the claim (from REF D9)"""

    plan_code: Optional[str] = None
    """Identifies the subscriber's plan (from SBR03)"""

    patient_sex: Optional[SexType] = None
    """Biological sex of the patient for clinical purposes (from DMG02). 0:Unknown, 1:Male,
    2:Female
    """

    patient_date_of_birth: Optional[Date] = None
    """Patient date of birth (from DMG03)"""

    patient_height_in_cm: Optional[float] = None
    """Patient height in centimeters (from HI value A9, MEA value HT)"""

    patient_weight_in_kg: Optional[float] = None
    """Patient weight in kilograms (from HI value A8, PAT08, CR102 [ambulance only])"""

    ambulance_pickup_zip: Optional[str] = None
    """Location where patient was picked up in ambulance (from HI with HIxx_01=BE and HIxx_02=A0
    or NM1 loop with NM1 PW)
    """

    form_type: Optional[FormType] = None
    """Type of form used to submit the claim. Can be HCFA or UB-04 (from CLM05_02)"""

    bill_type_or_pos: Optional[str] = None
    """Describes type of facility where services were rendered (from CLM05_01)"""

    bill_type_sequence: Optional[BillTypeSequence] = None
    """Where the claim is at in its billing lifecycle (e.g. 0: Non-Pay, 1: Admit Through
    Discharge, 7: Replacement, etc.) (from CLM05_03)
    """

    billed_amount: Optional[float] = None
    """Billed amount from provider (from CLM02)"""

    allowed_amount: Optional[float] = None
    """Amount allowed by the plan for payment. Both member and plan responsibility (non-EDI)"""

    paid_amount: Optional[float] = None
    """Amount paid by the plan for the claim (non-EDI)"""

    date_from: Optional[Date] = None
    """Earliest service date among services, or statement date if not found"""

    date_through: Optional[Date] = None
    """Latest service date among services, or statement date if not found"""

    discharge_status: Optional[str] = None
    """Status of the patient at time of discharge (from CL103)"""

    admit_diagnosis: Optional[str] = None
    """ICD diagnosis at the time the patient was admitted (from HI ABJ or BJ)"""

    principal_diagnosis: Optional[Diagnosis] = None
    """Principal ICD diagnosis for the patient (from HI ABK or BK)"""

    other_diagnoses: Optional[list[Diagnosis]] = None
    """Other ICD diagnoses that apply to the patient (from HI ABF or BF)"""

    principal_procedure: Optional[str] = None
    """Principal ICD procedure for the patient (from HI BBR or BR)"""

    other_procedures: Optional[list[str]] = None
    """Other ICD procedures that apply to the patient (from HI BBQ or BQ)"""

    condition_codes: Optional[list[str]] = None
    """Special conditions that may affect payment or other processing (from HI BG)"""

    value_codes: Optional[list[ValueCode]] = None
    """Numeric values related to the patient or claim (HI BE)"""

    occurrence_codes: Optional[list[str]] = None
    """Date related occurrences related to the patient or claim (from HI BH)"""

    drg: Optional[str] = None
    """Diagnosis Related Group for inpatient services (from HI DR)"""

    services: list[Service] = Field(min_length=1)
    """One or more services provided to the patient (from LX loop)"""


class RateSheetService(BaseModel):
    model_config = camel_case_model_config

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
    """Type of form used to submit the claim. Can be HCFA or UB-04 (from CLM05_02)"""

    bill_type_or_pos: str
    """Describes type of facility where services were rendered (from CLM05_01)"""

    drg: str
    """Diagnosis Related Group for inpatient services (from HI DR)"""

    billed_amount: float
    """Billed amount from provider (from CLM02)"""

    allowed_amount: float
    """Amount allowed by the plan for payment. Both member and plan responsibility (non-EDI)"""

    paid_amount: float
    """Amount paid by the plan for the claim (non-EDI)"""

    services: list[RateSheetService]
    """One or more services provided to the patient (from LX loop)"""
