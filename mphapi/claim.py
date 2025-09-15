import decimal
from enum import Enum, IntEnum
from typing import Annotated, Any, Optional

from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from .date import Date
from .fields import camel_case_model_config, field_name


class FormType(str, Enum):
    """Type of form used to submit the claim. Can be HCFA or UB-04 (from CLM05_02)"""

    UB_04 = "UB-04"
    HCFA = "HCFA"


class BillTypeSequence(str, Enum):
    """Where the claim is at in its billing lifecycle (e.g. 0: Non-Pay, 1: Admit Through
    Discharge, 7: Replacement, etc.) (from CLM05_03)
    """

    NON_PAY = "0"
    ADMIT_THROUGH_DISCHARGE = "1"
    FIRST_INTERIM = "2"
    CONTINUING_INTERIM = "3"
    LAST_INTERIM = "4"
    LATE_CHARGE = "5"
    FIRST_INTERIM_DEPRECATED = "6"
    REPLACEMENT = "7"
    VOID_OR_CANCEL = "8"
    FINAL_CLAIM = "9"
    CWF_ADJUSTMENT = "G"
    CMS_ADJUSTMENT = "H"
    INTERMEDIARY_ADJUSTMENT = "I"
    OTHER_ADJUSTMENT = "J"
    OIG_ADJUSTMENT = "K"
    MSP_ADJUSTMENT = "M"
    QIO_ADJUSTMENT = "P"
    PROVIDER_ADJUSTMENT = "Q"


class SexType(IntEnum):
    """Biological sex of the patient for clinical purposes"""

    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


class Provider(BaseModel):
    """
    Provider represents the service provider that rendered healthcare services on behalf of the patient.
    This can be found in Loop 2000A and/or Loop 2310 NM101-77 at the claim level, and may also be overridden at the service level in the 2400 loop
    """

    model_config = camel_case_model_config

    npi: str
    """National Provider Identifier of the provider (from NM109, required)"""

    ccn: Optional[str] = None
    """CMS Certification Number (optional)"""

    provider_tax_id: Annotated[Optional[str], field_name("providerTaxID")] = None
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

    provider_zip: Annotated[Optional[str], field_name("providerZIP")] = None
    """ZIP code of the provider (from N403, required)"""


class Decimal:
    """
    An arbitrary precision number.
    When deserializing it allows to deserialize from a float, str, or int.
    When serialized it always serializes to a str to prevent loss of precision.
    """

    # Python has an arbitrary precision number built in that this type is just a thin wrapper around.
    value: decimal.Decimal

    def __init__(self, value: decimal.Decimal):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    # Based off of this: https://docs.pydantic.dev/2.1/usage/types/custom/#handling-third-party-types
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        def to_decimal(value: float | int | str | decimal.Decimal) -> Decimal:
            return Decimal(decimal.Decimal(value))

        from_value = core_schema.chain_schema(
            [
                core_schema.union_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.is_instance_schema(decimal.Decimal),
                        core_schema.float_schema(),
                        core_schema.int_schema(),
                    ]
                ),
                core_schema.no_info_plain_validator_function(to_decimal),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_value,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(Decimal),
                    from_value,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda decimal: str(decimal)
            ),
        )


class ValueCode(BaseModel):
    model_config = camel_case_model_config

    code: str
    """Code indicating the type of value provided (from HIxx_02)"""

    amount: Decimal
    """Amount associated with the value code (from HIxx_05)"""


class Diagnosis(BaseModel):
    """Principal, Other Diagnosis, Admitting Diagnosis, External Cause of Injury"""

    model_config = camel_case_model_config

    code: str
    """ICD-10 diagnosis code (from HIxx_02)"""

    present_on_admission: Optional[str] = None
    """Flag indicates whether diagnosis was present at the time of admission (from HIxx_09)"""


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

    procedure_modifiers: Optional[list[str]] = None
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

    ambulance_pickup_zip: Annotated[Optional[str], field_name("ambulancePickupZIP")] = (
        None
    )
    """ZIP code where ambulance picked up patient. Supplied if different than claim-level value (from NM1 PW)"""


class Claim(Provider, BaseModel):
    model_config = camel_case_model_config

    claim_id: Annotated[Optional[str], field_name("claimID")] = None
    """Unique identifier for the claim (from REF D9)"""

    plan_code: Optional[str] = None
    """Identifies the subscriber's plan (from SBR03)"""

    patient_sex: Optional[SexType] = None
    """Biological sex of the patient for clinical purposes (from DMG02). 0:Unknown, 1:Male,
    2:Female
    """

    patient_date_of_birth: Optional[Date] = None
    """Patient date of birth (from DMG03)"""

    patient_height_in_cm: Annotated[
        Optional[float], field_name("patientHeightInCM")
    ] = None
    """Patient height in centimeters (from HI value A9, MEA value HT)"""

    patient_weight_in_kg: Annotated[
        Optional[float], field_name("patientWeightInKG")
    ] = None
    """Patient weight in kilograms (from HI value A8, PAT08, CR102 [ambulance only])"""

    ambulance_pickup_zip: Annotated[Optional[str], field_name("ambulancePickupZIP")] = (
        None
    )
    """Location where patient was picked up in ambulance (from HI with HIxx_01=BE and HIxx_02=A0
    or NM1 loop with NM1 PW)
    """

    form_type: Optional[FormType] = None
    """Type of form used to submit the claim. Can be HCFA or UB-04 (from CLM05_02)"""

    bill_type_or_pos: Annotated[Optional[str], field_name("billTypeOrPOS")] = None
    """Describes type of facility where services were rendered (from CLM05_01)"""

    bill_type_sequence: Optional[BillTypeSequence] = None
    """Where the claim is at in its billing lifecycle (e.g. 0: Non-Pay, 1: Admit Through Discharge, 7: Replacement, etc.) (from CLM05_03)"""

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

    procedure_code: Optional[str] = None
    """Procedure code (from SV101_02 / SV202_02)"""

    procedure_modifiers: Optional[list[str]] = None
    """Procedure modifiers (from SV101_03, 4, 5, 6 / SV202_03, 4, 5, 6)"""


class RateSheet(BaseModel):
    npi: str
    """National Provider Identifier of the provider (from NM109, required)"""

    provider_first_name: Optional[str] = None
    """First name of the provider (NM104, highly recommended)"""

    provider_last_name: Optional[str] = None
    """Last name of the provider (from NM103, highly recommended)"""

    provider_org_name: Optional[str] = None
    """Organization name of the provider (from NM103, highly recommended)"""

    provider_address: Optional[str] = None
    """Address of the provider (from N301, highly recommended)"""

    provider_city: Optional[str] = None
    """City of the provider (from N401, highly recommended)"""

    provider_state: Optional[str] = None
    """State of the provider (from N402, highly recommended)"""

    provider_zip: Annotated[str, field_name("providerZIP")]
    """ZIP code of the provider (from N403, required)"""

    form_type: Optional[FormType] = None
    """Type of form used to submit the claim. Can be HCFA or UB-04 (from CLM05_02)"""

    bill_type_or_pos: Annotated[Optional[str], field_name("billTypeOrPOS")] = None
    """Describes type of facility where services were rendered (from CLM05_01)"""

    drg: Optional[str] = None
    """Diagnosis Related Group for inpatient services (from HI DR)"""

    services: Optional[list[RateSheetService]] = None
    """One or more services provided to the patient (from LX loop)"""
