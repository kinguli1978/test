"""Main client for interacting with Amazon Seller Central SP-API."""

from datetime import datetime, timedelta, timezone
from typing import Any

from sp_api.api import Orders, CatalogItems, Inventories, Reports, Finances
from sp_api.base import Marketplaces, SellingApiException

from amazon_seller_central.config import SellerConfig


def _get_marketplace(config: SellerConfig) -> Marketplaces:
    """Map config marketplace string to SP-API Marketplaces enum."""
    mapping = {
        "US": Marketplaces.US,
        "CA": Marketplaces.CA,
        "MX": Marketplaces.MX,
        "BR": Marketplaces.BR,
        "ES": Marketplaces.ES,
        "UK": Marketplaces.UK,
        "FR": Marketplaces.FR,
        "NL": Marketplaces.NL,
        "DE": Marketplaces.DE,
        "IT": Marketplaces.IT,
        "SE": Marketplaces.SE,
        "PL": Marketplaces.PL,
        "TR": Marketplaces.TR,
        "SA": Marketplaces.SA,
        "AE": Marketplaces.AE,
        "IN": Marketplaces.IN,
        "SG": Marketplaces.SG,
        "AU": Marketplaces.AU,
        "JP": Marketplaces.JP,
    }
    return mapping.get(config.marketplace, Marketplaces.US)


class SellerCentralClient:
    """Client to interact with Amazon Seller Central via SP-API.

    Usage:
        config = SellerConfig.from_env()
        client = SellerCentralClient(config)
        orders = client.get_orders(days=7)
    """

    def __init__(self, config: SellerConfig):
        self.config = config
        self.credentials = {
            "refresh_token": config.refresh_token,
            "lwa_app_id": config.lwa_app_id,
            "lwa_client_secret": config.lwa_client_secret,
            "aws_access_key": config.aws_access_key,
            "aws_secret_key": config.aws_secret_key,
        }
        self.marketplace = _get_marketplace(config)

    # ---- Orders ----

    def get_orders(self, days: int = 7) -> list[dict[str, Any]]:
        """Fetch orders from the last N days."""
        after = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        try:
            response = Orders(credentials=self.credentials, marketplace=self.marketplace)
            result = response.get_orders(CreatedAfter=after)
            return result.payload.get("Orders", [])
        except SellingApiException as e:
            raise RuntimeError(f"Failed to fetch orders: {e}") from e

    def get_order(self, order_id: str) -> dict[str, Any]:
        """Fetch a single order by ID."""
        try:
            response = Orders(credentials=self.credentials, marketplace=self.marketplace)
            result = response.get_order(order_id)
            return result.payload
        except SellingApiException as e:
            raise RuntimeError(f"Failed to fetch order {order_id}: {e}") from e

    def get_order_items(self, order_id: str) -> list[dict[str, Any]]:
        """Fetch line items for a specific order."""
        try:
            response = Orders(credentials=self.credentials, marketplace=self.marketplace)
            result = response.get_order_items(order_id)
            return result.payload.get("OrderItems", [])
        except SellingApiException as e:
            raise RuntimeError(f"Failed to fetch items for order {order_id}: {e}") from e

    # ---- Inventory ----

    def get_inventory(self, skus: list[str] | None = None) -> list[dict[str, Any]]:
        """Fetch FBA inventory summaries. Optionally filter by SKUs."""
        try:
            inv = Inventories(credentials=self.credentials, marketplace=self.marketplace)
            params: dict[str, Any] = {
                "details": True,
                "granularityType": "Marketplace",
                "granularityId": self.config.marketplace_id,
            }
            if skus:
                params["sellerSkus"] = skus
            result = inv.get_inventory_summary_marketplace(**params)
            return result.payload.get("inventorySummaries", [])
        except SellingApiException as e:
            raise RuntimeError(f"Failed to fetch inventory: {e}") from e

    # ---- Catalog ----

    def search_catalog(self, keywords: str) -> list[dict[str, Any]]:
        """Search the Amazon catalog by keywords."""
        try:
            catalog = CatalogItems(credentials=self.credentials, marketplace=self.marketplace)
            result = catalog.search_catalog_items(
                keywords=keywords,
                marketplaceIds=[self.config.marketplace_id],
            )
            return result.payload.get("items", [])
        except SellingApiException as e:
            raise RuntimeError(f"Catalog search failed: {e}") from e

    def get_catalog_item(self, asin: str) -> dict[str, Any]:
        """Get catalog details for a single ASIN."""
        try:
            catalog = CatalogItems(credentials=self.credentials, marketplace=self.marketplace)
            result = catalog.get_catalog_item(
                asin=asin,
                marketplaceIds=[self.config.marketplace_id],
            )
            return result.payload
        except SellingApiException as e:
            raise RuntimeError(f"Failed to get catalog item {asin}: {e}") from e

    # ---- Financial Events ----

    def get_financial_events(self, order_id: str) -> dict[str, Any]:
        """Get financial events (fees, charges) for an order."""
        try:
            fin = Finances(credentials=self.credentials, marketplace=self.marketplace)
            result = fin.get_financial_events_for_order(order_id)
            return result.payload
        except SellingApiException as e:
            raise RuntimeError(f"Failed to get financials for {order_id}: {e}") from e

    # ---- Reports ----

    def request_report(self, report_type: str) -> str:
        """Request a report and return the report ID.

        Common report types:
          - GET_FLAT_FILE_OPEN_LISTINGS_DATA
          - GET_MERCHANT_LISTINGS_ALL_DATA
          - GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA
          - GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL
        """
        try:
            reports = Reports(credentials=self.credentials, marketplace=self.marketplace)
            result = reports.create_report(
                reportType=report_type,
                marketplaceIds=[self.config.marketplace_id],
            )
            return result.payload["reportId"]
        except SellingApiException as e:
            raise RuntimeError(f"Failed to request report: {e}") from e

    def get_report(self, report_id: str) -> dict[str, Any]:
        """Check report status and retrieve it when ready."""
        try:
            reports = Reports(credentials=self.credentials, marketplace=self.marketplace)
            result = reports.get_report(report_id)
            return result.payload
        except SellingApiException as e:
            raise RuntimeError(f"Failed to get report {report_id}: {e}") from e
