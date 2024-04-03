from pydantic import BaseModel


class ResponseError(BaseModel):
    """ResponseError supplies detailed error information when an entire request or an item in a response fails"""

    title: str
    detail: str

    def __str__(self) -> str:
        return f"{self.title}: {self.detail}"


class ResponseSuccess[Result: BaseModel](BaseModel):
    result: Result
    status_code: int


class Response[Result: BaseModel](BaseModel):
    """
    Response contains the standardized API response data used by all My Price Health API's. It is based off of the generalized error handling recommendation found
    in IETF RFC 7807 https://tools.ietf.org/html/rfc7807 and is a simplification of the Spring Boot error response as described at https://www.baeldung.com/rest-api-error-handling-best-practices
    """

    """
    An error response might look like this:
    {
        "error: {
            "title": "Incorrect username or password.",
            "detail": "Authentication failed due to incorrect username or password.",
        }
        "status": 401,
    }

    A successful response with a single result might look like this:
    {
        "result": {
            "procedureCode": "ABC",
            "billedAverage": 15.23
        },
        "status": 200,
    }
    """

    __root__: ResponseSuccess[Result] | ResponseError


class ResponsesSuccess[Result: BaseModel](BaseModel):
    results: list[Result]
    success_count: int
    error_count: int
    status_code: int


class ResponseFailure(BaseModel):
    error: ResponseError
    status_code: int


class Responses[Result: BaseModel](BaseModel):
    __root__: ResponsesSuccess[Result] | ResponseFailure
