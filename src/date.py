from pydantic import BaseModel


class Date(BaseModel):
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
