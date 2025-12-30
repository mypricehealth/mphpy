import base64
import binascii
import getpass
import json
import os
import time
from pathlib import Path
from typing import Any

import requests
from pydantic import BaseModel, Field, RootModel

from .fields import camel_case_model_config


class RawCredentials(BaseModel):
    model_config = camel_case_model_config

    email: str
    id_token: str
    refresh_token: str
    expires_at: float

    def store(
        self, api_key: str, referer: str, credentials_path: Path
    ) -> "Credentials":
        stored_credentials = StoredCredentials(
            api_key=api_key,
            referer=referer,
            email=self.email,
            id_token=self.id_token,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )

        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)

        with credentials_path.open("w+") as f:
            json.dump(
                stored_credentials.model_dump(
                    mode="json", by_alias=True, exclude_none=True
                ),
                f,
            )

        return Credentials(
            referer=referer,
            credentials_path=credentials_path,
            api_key=api_key,
            email=stored_credentials.email,
            id_token=stored_credentials.id_token,
            refresh_token=stored_credentials.refresh_token,
            expires_at=stored_credentials.expires_at,
        )


class StoredCredentials(RawCredentials):
    api_key: str
    referer: str


class Credentials(StoredCredentials):
    credentials_path: Path = Field(..., exclude=True)

    def refresh_if_needed(self) -> "Credentials | None":
        # # There's more than 5 minutes until the credentials need refreshing. Don't bother.
        if self.expires_at > time.time() + 5 * 60:
            return None

        new_credentials = refresh_token(self.api_key, self.referer, self.refresh_token)
        return new_credentials.store(self.api_key, self.referer, self.credentials_path)


class GoogleException(Exception):
    def __init__(self, message: str):
        self.message = message


class GoogleError(BaseModel):
    code: int
    message: str
    # errors omitted as unused


class GoogleResponseError(BaseModel):
    model_config = camel_case_model_config

    error: GoogleError

    def to_exception(self) -> GoogleException:
        return GoogleException(self.error.message)


class GoogleResponse[Result: BaseModel](RootModel[Result | GoogleResponseError]):
    pass


class SignInResult(BaseModel):
    """
    The result of signing in.
    See https://docs.cloud.google.com/identity-platform/docs/reference/rest/v1/accounts/signInWithPassword
    """

    model_config = camel_case_model_config

    email: str
    """The email of the authenticated user. Always present in the response."""

    id_token: str
    """An Identity Platform ID token for the authenticated user."""

    refresh_token: str
    """An Identity Platform refresh token for the authenticated user."""

    expires_in: int
    """The number of seconds until the Identity Platform ID token expires."""


class RefreshTokenResult(BaseModel):
    """
    The result of refreshing a refresh_token.
    See https://cloud.google.com/identity-platform/docs/use-rest-api#section-refresh-token
    """

    # NOT camelCase

    expires_in: int
    """The number of seconds in which the ID token expires."""

    token_type: str
    """The type of the refresh token, always "Bearer"."""

    refresh_token: str
    """The Identity Platform refresh token provided in the request or a new refresh token."""

    id_token: str
    """An Identity Platform ID token."""

    user_id: str
    """The uid corresponding to the provided ID token."""

    project_id: str
    """Your Google Cloud project ID."""


class Token(BaseModel):
    """
    The decoded ID token from SignInResult or RefreshTokenResult.
    """

    issuer: str
    email: str
    subject: str
    audience: str
    authorized_party: str
    expiration: int
    issued_at: int
    login_id: str  # not to be confused with the user_id claim, the firebase id
    roles: list[str]
    login_name: str  # not to be confused with the name claim, the name in firebase


def get_credentials(api_key: str, referer: str) -> Credentials:
    credentials_path = get_credentials_path()

    credentials = get_stored_credentials(credentials_path)
    if credentials is not None:
        try:
            credentials.refresh_if_needed()
        except GoogleException as e:
            # `INVALID_ID_TOKEN` means the user must login again.
            if e.message != "INVALID_ID_TOKEN":
                raise e

        return credentials

    email = input("Email: ")
    login_credentials: RawCredentials | None = None

    while True:
        try:
            password = getpass.getpass("Password: ")
            login_credentials = sign_in(api_key, email, password)
            break
        except GoogleException as e:
            if e.message == "INVALID_PASSWORD":
                continue

            raise e

    return login_credentials.store(api_key, referer, credentials_path)


def get_credentials_path() -> Path:
    home = Path.home()
    return home.joinpath(".mph", "credentials.json")


def get_stored_credentials(credentials_path: Path) -> Credentials | None:
    try:
        with credentials_path.open() as f:
            credentials_json = json.load(f)
            stored_credentials = StoredCredentials.model_validate(credentials_json)
    except FileNotFoundError:
        return None

    credentials = Credentials(
        email=stored_credentials.email,
        id_token=stored_credentials.id_token,
        refresh_token=stored_credentials.refresh_token,
        expires_at=stored_credentials.expires_at,
        api_key=stored_credentials.api_key,
        referer=stored_credentials.referer,
        credentials_path=credentials_path,
    )

    return credentials


def refresh_token(api_key: str, referer: str, refresh_token: str) -> RawCredentials:
    response = requests.post(
        "https://securetoken.googleapis.com/v1/token",
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        params={
            "key": api_key,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": referer,
        },
    )

    result = (
        GoogleResponse[RefreshTokenResult].model_validate_json(response.content).root
    )

    if isinstance(result, GoogleResponseError):
        raise result.to_exception()

    return RawCredentials(
        email="",
        id_token=result.id_token,
        refresh_token=result.refresh_token,
        expires_at=time.time() + result.expires_in,
    )


def sign_in(api_key: str, email: str, password: str) -> RawCredentials:
    response = requests.post(
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword",
        json={
            "email": email,
            "password": password,
            "returnSecureToken": "true",
        },
        params={
            "key": api_key,
        },
        headers={"Referer": "http://myprice.health"},
    )

    result = GoogleResponse[SignInResult].model_validate_json(response.content).root

    if isinstance(result, GoogleResponseError):
        raise result.to_exception()

    sign_in_result = result

    credentials = RawCredentials(
        email=sign_in_result.email,
        id_token=sign_in_result.id_token,
        refresh_token=sign_in_result.refresh_token,
        expires_at=time.time() + sign_in_result.expires_in,
    )

    return credentials


# decode_jwt will parse a JWT payload without verifying that it is cryptographically valid.
# Code is simplified from https://github.com/jpadilla/pyjwt
def decode_jwt(jwt: str) -> Token:
    try:
        signing_input, _ = jwt.rsplit(".", 1)
        _, payload_segment = signing_input.split(".", 1)
    except Exception as err:
        raise Exception("Expected token with 3 segments") from err

    try:
        payload_decoded = base64url_decode(payload_segment)
    except (TypeError, binascii.Error) as err:
        raise Exception("Invalid payload padding") from err

    try:
        payload: dict[str, Any] = json.loads(payload_decoded)
    except ValueError as e:
        raise Exception(f"Invalid payload string: {e}") from e

    return Token(
        issuer=payload.get("iss", ""),
        email=payload.get("email", ""),
        subject=payload.get("sub", ""),
        audience=payload.get("aud", ""),
        authorized_party=payload.get("azp", ""),
        expiration=payload.get("exp", 0),
        issued_at=payload.get("iat", 0),
        login_id=payload.get("login_id", ""),
        roles=payload.get("roles", []),
        login_name=payload.get("login_name", ""),
    )


def base64url_decode(input: str) -> bytes:
    input_bytes = input.encode("utf-8")

    rem = len(input_bytes) % 4

    if rem > 0:
        input_bytes += b"=" * (4 - rem)

    return base64.urlsafe_b64decode(input_bytes)
