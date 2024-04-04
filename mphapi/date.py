from datetime import datetime
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class Date:
    """Date is a custom type for representing dates in the format YYYYMMDD"""

    year: int
    month: int
    day: int

    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day

    def __str__(self):
        return f"{self.year}{self.month:02d}{self.day:02d}"

    # Based off of this: https://docs.pydantic.dev/2.1/usage/types/custom/#handling-third-party-types
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        def to_date(value: str) -> Date:
            time = datetime.strptime(value, "%Y%m%d")

            return Date(time.year, time.month, time.day)

        from_str = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(to_date),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(Date),
                    from_str,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda date: str(date)
            ),
        )
