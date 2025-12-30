import os

from mphapi import (
    ClaimStatus,
    Client,
    get_credentials,
    status_pending_provider_matching,
)

app_api_key = "AIzaSyDFRvI57W5S5w4XJsQFXpm3znb9PajWu6o"  # Firebase API key (currently hard-coded to the My Price Health Firebase instance)
claim_id = "1234567890"


def main():
    api_key = os.getenv(
        "API_KEY"
    )  # API key for accessing My Price Health API's at https://api.myprice.health
    if api_key is None:
        raise EnvironmentError("API_KEY must be set")

    app_url = os.getenv("APP_URL")  # tenant URL (e.g. https://yourcompany.metl.health)
    if app_url is None:
        raise EnvironmentError("APP_URL must be set")

    app_referer = app_url
    app_credentials = get_credentials(app_api_key, app_referer)

    client = Client(
        api_key,
        api_url=app_url,
        app_url=app_url,
        app_api_key=app_api_key,
        app_referer=app_referer,
        app_credentials=app_credentials,
    )

    status = status_pending_provider_matching  # choose the status you want to set the claim to here
    claimStatus = ClaimStatus(
        step=status.step,
        status=status.status,
    )
    try:
        client.insert_claim_status(claim_id, claimStatus)
    except Exception as e:
        print(f"Error inserting claim status: {e}")


if __name__ == "__main__":
    main()
