#!/usr/bin/env python3
"""Flask web dashboard for Amazon Seller Central."""

import os
from datetime import datetime, timezone

from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

# --- Helpers ---

def _get_client():
    """Create a SellerCentralClient from env, or return None if not configured."""
    from amazon_seller_central import SellerConfig, SellerCentralClient
    try:
        config = SellerConfig.from_env()
        return SellerCentralClient(config)
    except (KeyError, Exception):
        return None


def _credentials_configured() -> bool:
    """Check if the minimum SP-API credentials are set."""
    required = ["SP_API_REFRESH_TOKEN", "LWA_APP_ID", "LWA_CLIENT_SECRET",
                "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    return all(os.getenv(k) and os.getenv(k) != f"your_{k.lower()}_here" for k in required)


# --- Routes ---

@app.route("/")
def dashboard():
    """Main dashboard page."""
    configured = _credentials_configured()
    marketplace = os.getenv("MARKETPLACE", "US")
    seller_id = os.getenv("SELLER_ID", "Not set")
    return render_template("dashboard.html",
                           configured=configured,
                           marketplace=marketplace,
                           seller_id=seller_id,
                           now=datetime.now(timezone.utc))


@app.route("/orders")
def orders():
    """Orders page."""
    days = request.args.get("days", 7, type=int)
    client = _get_client()
    order_list = []
    error = None

    if client:
        try:
            order_list = client.get_orders(days=days)
        except Exception as e:
            error = str(e)
    else:
        error = "SP-API credentials not configured. Please update your .env file."

    return render_template("orders.html", orders=order_list, days=days, error=error)


@app.route("/orders/<order_id>")
def order_detail(order_id):
    """Single order detail page."""
    client = _get_client()
    order = {}
    items = []
    error = None

    if client:
        try:
            order = client.get_order(order_id)
            items = client.get_order_items(order_id)
        except Exception as e:
            error = str(e)
    else:
        error = "SP-API credentials not configured."

    return render_template("order_detail.html", order=order, items=items,
                           order_id=order_id, error=error)


@app.route("/inventory")
def inventory():
    """Inventory page."""
    sku_filter = request.args.get("sku", "").strip()
    client = _get_client()
    inv_list = []
    error = None

    if client:
        try:
            skus = [sku_filter] if sku_filter else None
            inv_list = client.get_inventory(skus=skus)
        except Exception as e:
            error = str(e)
    else:
        error = "SP-API credentials not configured."

    return render_template("inventory.html", inventory=inv_list,
                           sku_filter=sku_filter, error=error)


@app.route("/catalog")
def catalog():
    """Catalog search page."""
    keywords = request.args.get("q", "").strip()
    client = _get_client()
    results = []
    error = None

    if client and keywords:
        try:
            results = client.search_catalog(keywords=keywords)
        except Exception as e:
            error = str(e)
    elif not client and keywords:
        error = "SP-API credentials not configured."

    return render_template("catalog.html", results=results,
                           keywords=keywords, error=error)


@app.route("/reports", methods=["GET", "POST"])
def reports():
    """Reports page - request and check reports."""
    client = _get_client()
    error = None
    report_info = None

    if request.method == "POST" and client:
        report_type = request.form.get("report_type", "")
        action = request.form.get("action", "")

        try:
            if action == "request":
                report_id = client.request_report(report_type)
                flash(f"Report requested! ID: {report_id}", "success")
            elif action == "check":
                report_id = request.form.get("report_id", "")
                report_info = client.get_report(report_id)
        except Exception as e:
            error = str(e)
    elif request.method == "POST" and not client:
        error = "SP-API credentials not configured."

    report_types = [
        ("GET_FLAT_FILE_OPEN_LISTINGS_DATA", "Active Listings"),
        ("GET_MERCHANT_LISTINGS_ALL_DATA", "All Listings"),
        ("GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA", "FBA Inventory"),
        ("GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL", "All Orders"),
    ]

    return render_template("reports.html", report_types=report_types,
                           report_info=report_info, error=error)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
