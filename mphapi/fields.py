from typing import Any

from pydantic import AliasGenerator, ConfigDict, Field
from pydantic.alias_generators import to_camel

camel_case_model_config = ConfigDict(
    alias_generator=AliasGenerator(
        validation_alias=to_camel, serialization_alias=to_camel
    ),
    populate_by_name=True,
)


# The return value of Field itself is typed as Any even though it's technically always of type `FieldInfo`.
# For once this unsoundness is desired, as it's meant to be assignable to any field type.
def field_name(alias: str) -> Any:
    return Field(validation_alias=alias, serialization_alias=alias)
