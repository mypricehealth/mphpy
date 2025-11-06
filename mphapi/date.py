from abc import abstractmethod
from datetime import datetime as dt
from datetime import tzinfo
from typing import Any, ClassVar, Self, SupportsIndex

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class AbstractDateTime:
    format: ClassVar[str]
    secondary_formats: ClassVar[list[str]] = []
    datetime: dt

    @classmethod
    @abstractmethod
    def from_datetime(cls, datetime: dt) -> Self:
        pass

    def __str__(self):
        return self.datetime.strftime(self.format)

    # Based off of this: https://docs.pydantic.dev/2.1/usage/types/custom/#handling-third-party-types
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        def to_datetime_cls(value: str) -> Self:
            datetime: dt | None = None

            if len(cls.secondary_formats) == 0:
                datetime = dt.strptime(value, cls.format)
            else:
                formats = [cls.format, *cls.secondary_formats]
                for format in formats:
                    try:
                        datetime = dt.strptime(value, format)
                    except ValueError:
                        continue

                if datetime is None:
                    raise ValueError(
                        f"Could not parse date {repr(value)} with format {repr(cls.format)} or {repr(cls.secondary_formats)}"
                    )

            return cls.from_datetime(datetime)

        from_str = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(to_datetime_cls),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(cls),
                    from_str,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda date: str(date)
            ),
        )


class Date(AbstractDateTime):
    """Date is a custom type for representing dates in the format YYYYMMDD"""

    format = "%Y%m%d"

    year: int
    month: int
    day: int

    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day
        self.datetime = dt(year, month, day)

    @classmethod
    def from_datetime(cls, datetime: dt):
        return cls(datetime.year, datetime.month, datetime.day)


class DateTime(AbstractDateTime):
    """DateTime is a custom type for representing dates"""

    # `%f` is padded to 6 characters but should be 9 overall.
    format = "%Y-%m-%d %H:%M:%S.000%f%z"

    # Same constructor as datetime has.
    def __init__(
        self,
        year: SupportsIndex,
        month: SupportsIndex,
        day: SupportsIndex,
        hour: SupportsIndex = 0,
        minute: SupportsIndex = 0,
        second: SupportsIndex = 0,
        microsecond: SupportsIndex = 0,
        tzinfo: tzinfo | None = None,
        *,
        fold: int = 0,
    ):
        self.datetime = dt(
            year, month, day, hour, minute, second, microsecond, tzinfo, fold=fold
        )

    @classmethod
    def from_datetime(cls, datetime: dt):
        return cls(
            datetime.year,
            datetime.month,
            datetime.day,
            datetime.hour,
            datetime.minute,
            datetime.second,
            datetime.microsecond,
            datetime.tzinfo,
            fold=datetime.fold,
        )
