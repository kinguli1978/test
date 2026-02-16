#!/usr/bin/env python3
"""Example: Connect to Amazon Seller Central and fetch data."""

from amazon_seller_central import SellerConfig, SellerCentralClient


def main():
    # Load credentials from .env file
    config = SellerConfig.from_env()
    client = SellerCentralClient(config)

    # --- Fetch recent orders ---
    print("=== Recent Orders (last 7 days) ===")
    orders = client.get_orders(days=7)
    for order in orders[:5]:  # show first 5
        print(f"  Order: {order.get('AmazonOrderId')}")
        print(f"  Status: {order.get('OrderStatus')}")
        print(f"  Total: {order.get('OrderTotal', {}).get('Amount', 'N/A')}")
        print()

    # --- Fetch FBA inventory ---
    print("=== FBA Inventory ===")
    inventory = client.get_inventory()
    for item in inventory[:5]:  # show first 5
        print(f"  SKU: {item.get('sellerSku')}")
        print(f"  ASIN: {item.get('asin')}")
        print(f"  Fulfillable: {item.get('fulfillableQuantity', 0)}")
        print()

    # --- Search catalog ---
    print("=== Catalog Search ===")
    results = client.search_catalog(keywords="your product keyword")
    for item in results[:3]:
        print(f"  ASIN: {item.get('asin')}")
        print()

    # --- Request a report ---
    print("=== Request Listings Report ===")
    report_id = client.request_report("GET_MERCHANT_LISTINGS_ALL_DATA")
    print(f"  Report requested, ID: {report_id}")
    print("  Use client.get_report(report_id) to check status.")


if __name__ == "__main__":
    main()
