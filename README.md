# Amazon Seller Central Integration

Python integration for Amazon Seller Central using the **Selling Partner API (SP-API)**.

## Features

- **Orders** - Fetch recent orders, order details, and line items
- **Inventory** - Query FBA inventory summaries by SKU
- **Catalog** - Search products and get ASIN details
- **Finances** - Retrieve financial events (fees, charges) per order
- **Reports** - Request and download Seller Central reports

## Setup

### 1. Prerequisites

You need an **Amazon SP-API application** registered in Seller Central:

1. Go to [Seller Central](https://sellercentral.amazon.com) > **Apps & Services** > **Develop Apps**
2. Register as a developer if you haven't already
3. Create a new app and note your **LWA credentials** (App ID + Client Secret)
4. Create an **IAM user** in AWS and attach the SP-API policy
5. Generate a **refresh token** by self-authorizing your app

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

| Variable | Where to find it |
|---|---|
| `SP_API_REFRESH_TOKEN` | Generated when you authorize your app |
| `LWA_APP_ID` | Seller Central > Develop Apps > your app |
| `LWA_CLIENT_SECRET` | Seller Central > Develop Apps > your app |
| `AWS_ACCESS_KEY_ID` | AWS IAM console |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM console |
| `MARKETPLACE` | Your marketplace code (US, UK, DE, etc.) |
| `SELLER_ID` | Seller Central > Settings > Account Info |

### 4. Run the Example

```bash
python example.py
```

## Usage in Code

```python
from amazon_seller_central import SellerConfig, SellerCentralClient

config = SellerConfig.from_env()
client = SellerCentralClient(config)

# Get orders from the last 7 days
orders = client.get_orders(days=7)

# Check inventory
inventory = client.get_inventory(skus=["MY-SKU-001"])

# Search catalog
results = client.search_catalog(keywords="wireless earbuds")

# Get financial details for an order
financials = client.get_financial_events(order_id="123-4567890-1234567")

# Request a report
report_id = client.request_report("GET_MERCHANT_LISTINGS_ALL_DATA")
```

## Supported Marketplaces

US, CA, MX, BR, ES, UK, FR, BE, NL, DE, IT, SE, ZA, PL, EG, TR, SA, AE, IN, SG, AU, JP

## Common Report Types

| Report Type | Description |
|---|---|
| `GET_FLAT_FILE_OPEN_LISTINGS_DATA` | Active listings |
| `GET_MERCHANT_LISTINGS_ALL_DATA` | All listings |
| `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` | FBA inventory |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | All orders |
