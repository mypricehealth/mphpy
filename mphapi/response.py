from pydantic import BaseModel, RootModel
from pydantic.dataclasses import dataclass


class APIError(Exception):
    message: str

    def __init__(self, message: str):
        super().__init__(message)


@dataclass
class ResponseError(APIError):
    title: str
    detail: str

    def __post_init__(self):
        super().__init__(self.__str__())

    def __str__(self) -> str:
        return f"{self.title}: {self.detail}"


class ResponseSuccess[Result: BaseModel](BaseModel):
    result: Result
    status: int


class ResponseFailure(BaseModel):
    error: ResponseError
    status: int


@dataclass
class GatewayError(APIError):
    message: str
    code: int

    def __post_init__(self):
        super().__init__(self.message)


class Response[Result: BaseModel](
    RootModel[ResponseSuccess[Result] | ResponseFailure | GatewayError]
):
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

    def result(
        self,
    ) -> Result:
        """Returns the result if it's successful, otherwise throws

        Returns
        -------
        Result
            The successful result.

        Raises
        ------
        ResponseError
            The request's error response.
        """

        if isinstance(self.root, ResponseSuccess):
            return self.root.result
        elif isinstance(self.root, ResponseFailure):
            raise self.root.error
        else:
            raise self.root


class ResponsesSuccess[Result: BaseModel](BaseModel):
    results: list[Result]
    success_count: int
    error_count: int
    status_code: int


class Responses[Result: BaseModel](
    RootModel[ResponsesSuccess[Result] | ResponseFailure]
):
    def results(
        self,
    ) -> list[Result]:
        """Returns the result if it's successful, otherwise throws

        Returns
        -------
        list[Result]
            The results, although some may still have encountered errors.

        Raises
        ------
        ResponseError
            The request's error response.
        """

        if isinstance(self.root, ResponsesSuccess):
            return self.root.results
        else:
            raise self.root.error
