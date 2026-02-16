"""Configuration for Amazon SP-API credentials and marketplace settings."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv


# Marketplace endpoint mappings
MARKETPLACE_IDS = {
    "US": "ATVPDKIKX0DER",
    "CA": "A2EUQ1WTGCTBG2",
    "MX": "A1AM78C64UM0Y8",
    "BR": "A2Q3Y263D00KWC",
    "ES": "A1RKKUPIHCS9HS",
    "UK": "A1F83G8C2ARO7P",
    "FR": "A13V1IB3VIYZZH",
    "BE": "AMEN7PMS3EDWL",
    "NL": "A1805IZSGTT6HS",
    "DE": "A1PA6795UKMFR9",
    "IT": "APJ6JRA9NG5V4",
    "SE": "A2NODRKZP88ZB9",
    "ZA": "AE08WJ6YKNBMC",
    "PL": "A1C3SOZNH6SQ4A",
    "EG": "ARBP9OOSHTCHU",
    "TR": "A33AVAJ2PDY3EV",
    "SA": "A17E79C6D8DWNP",
    "AE": "A2VIGQ35RCS4UG",
    "IN": "A21TJRUUN4KGV",
    "SG": "A19VAU5U5O7RUS",
    "AU": "A39IBJ37TRP1C6",
    "JP": "A1VC38T7YXB528",
}

MARKETPLACE_REGIONS = {
    "US": "na", "CA": "na", "MX": "na", "BR": "na",
    "ES": "eu", "UK": "eu", "FR": "eu", "BE": "eu",
    "NL": "eu", "DE": "eu", "IT": "eu", "SE": "eu",
    "ZA": "eu", "PL": "eu", "EG": "eu", "TR": "eu",
    "SA": "eu", "AE": "eu", "IN": "eu",
    "SG": "fe", "AU": "fe", "JP": "fe",
}


@dataclass
class SellerConfig:
    """Holds Amazon SP-API configuration."""

    refresh_token: str
    lwa_app_id: str
    lwa_client_secret: str
    aws_access_key: str
    aws_secret_key: str
    marketplace: str = "US"
    seller_id: str = ""

    @property
    def marketplace_id(self) -> str:
        return MARKETPLACE_IDS.get(self.marketplace, MARKETPLACE_IDS["US"])

    @property
    def region(self) -> str:
        return MARKETPLACE_REGIONS.get(self.marketplace, "na")

    @classmethod
    def from_env(cls, env_path: str = ".env") -> "SellerConfig":
        """Load configuration from environment variables / .env file."""
        load_dotenv(env_path)
        return cls(
            refresh_token=os.environ["SP_API_REFRESH_TOKEN"],
            lwa_app_id=os.environ["LWA_APP_ID"],
            lwa_client_secret=os.environ["LWA_CLIENT_SECRET"],
            aws_access_key=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            marketplace=os.getenv("MARKETPLACE", "US"),
            seller_id=os.getenv("SELLER_ID", ""),
        )
