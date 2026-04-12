import os
import requests
import logging
import time
import pandas as pd
from datetime import datetime, timedelta

# Amazon SP-API endpoints (India uses the EU region endpoint)
SP_API_BASE_URL = "https://sellingpartnerapi-eu.amazon.com"
LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"

class SPAPIClient:
    def __init__(self):
        # We will load these from a secure .env file later
        self.client_id = os.environ.get("SP_API_CLIENT_ID")
        self.client_secret = os.environ.get("SP_API_CLIENT_SECRET")
        self.refresh_token = os.environ.get("SP_API_REFRESH_TOKEN")
        
        self.access_token = None
        self.token_expiry = None

    def _refresh_access_token(self):
        """Exchanges the long-lived refresh token for a temporary access token."""
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(LWA_TOKEN_URL, data=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            # Tokens usually expire in 3600 seconds (1 hour)
            self.token_expiry = datetime.now() + timedelta(seconds=data.get("expires_in", 3600) - 60)
            logging.info("Successfully refreshed SP-API access token.")
        else:
            logging.error(f"Failed to refresh token: {response.text}")
            raise Exception("SP-API LWA Authentication Failed")

    def get_headers(self):
        """Ensures we have a valid token before making a request."""
        if not self.access_token or not self.token_expiry or datetime.now() >= self.token_expiry:
            self._refresh_access_token()
            
        return {
            "x-amz-access-token": self.access_token,
            "Content-Type": "application/json"
        }

    # --- LIVE ENDPOINTS ---

    def get_financial_events(self, days=30):
        """Pulls live financial settlement data from Amazon SP-API with pagination and throttling."""
        endpoint = f"{SP_API_BASE_URL}/finances/v0/financialEvents"
        created_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        params = {"PostedAfter": created_after}
        all_events = []
        
        while True:
            headers = self.get_headers()
            response = requests.get(endpoint, headers=headers, params=params)
            
            if response.status_code == 429:
                logging.warning("Amazon API Rate limit hit. Sleeping for 2 seconds...")
                time.sleep(2)
                continue
                
            response.raise_for_status()
            data = response.json()
            payload = data.get("payload", {})
            events_json = payload.get("FinancialEvents", {})
            
            all_events.extend(self._extract_events_from_json(events_json))
            
            next_token = payload.get("NextToken")
            if not next_token:
                break
                
            params = {"NextToken": next_token}
            time.sleep(0.5) # Respect the 0.5 requests/second limit
            
        return pd.DataFrame(all_events)

    def _extract_events_from_json(self, json_data):
        """Safely extracts Amazon FinancialEvents JSON to dictionary rows."""
        rows = []
        
        # 1. Process Orders
        for shipment in json_data.get("ShipmentEventList", []):
            order_id = shipment.get("AmazonOrderId", "UNKNOWN")
            raw_date = shipment.get("PostedDate", "")
            posted_date = raw_date.split("T")[0] if raw_date else "1970-01-01"

            for item in shipment.get("ShipmentItemList", []) or []:
                sku = item.get("SellerSKU", "UNKNOWN")
                quantity = item.get("QuantityShipped", 1)
                metrics = {"product sales": 0.0, "fba fees": 0.0, "selling fees": 0.0}
                for charge in item.get("ItemChargeList", []):
                    if charge.get("ChargeType") == "Principal":
                        metrics["product sales"] += float(charge.get("ChargeAmount", {}).get("CurrencyAmount", 0))
                for fee in item.get("ItemFeeList", []):
                    amount = float(fee.get("FeeAmount", {}).get("CurrencyAmount", 0))
                    if "FBA" in fee.get("FeeType", ""): metrics["fba fees"] += amount
                    else: metrics["selling fees"] += amount

                rows.append({
                    "order_id": order_id,
                    "date": posted_date,
                    "sku": sku,
                    "type": "Order",
                    "quantity": quantity,
                    "product sales": metrics["product sales"],
                    "fba fees": metrics["fba fees"],
                    "selling fees": metrics["selling fees"],
                    "total": metrics["product sales"] + metrics["fba fees"] + metrics["selling fees"]
                })
                
        # 2. Process Refunds
        for refund in json_data.get("RefundEventList", []):
            order_id = refund.get("AmazonOrderId", "UNKNOWN")
            raw_date = refund.get("PostedDate", "")
            posted_date = raw_date.split("T")[0] if raw_date else "1970-01-01"

            for item in refund.get("ShipmentItemAdjustmentList", []) or []:
                sku = item.get("SellerSKU", "UNKNOWN")
                quantity = item.get("QuantityShipped", 1)
                metrics = {"product sales": 0.0, "fba fees": 0.0, "selling fees": 0.0}
                
                for charge in item.get("ItemChargeAdjustmentList", []):
                    if charge.get("ChargeType") == "Principal":
                        metrics["product sales"] += float(charge.get("ChargeAmount", {}).get("CurrencyAmount", 0))
                for fee in item.get("ItemFeeAdjustmentList", []):
                    amount = float(fee.get("FeeAmount", {}).get("CurrencyAmount", 0))
                    if "FBA" in fee.get("FeeType", ""): metrics["fba fees"] += amount
                    else: metrics["selling fees"] += amount

                rows.append({
                    "order_id": f"{order_id}-REF", # Suffix ensures it doesn't get blocked by the deduplication check
                    "date": posted_date,
                    "sku": sku,
                    "type": "Refund",
                    "quantity": quantity,
                    "product sales": metrics["product sales"],
                    "fba fees": metrics["fba fees"],
                    "selling fees": metrics["selling fees"],
                    "total": metrics["product sales"] + metrics["fba fees"] + metrics["selling fees"]
                })
                
        return rows

    def get_fba_inventory(self):
        """Pulls live FBA stock levels for India (A21TJRUUN4KGV)."""
        headers = self.get_headers()
        endpoint = f"{SP_API_BASE_URL}/fba/inventory/v1/summaries"
        params = {
            "details": "true",
            "granularityType": "Marketplace",
            "granularityId": "A21TJRUUN4KGV",
            "marketplaceIds": "A21TJRUUN4KGV"
        }
        response = requests.get(endpoint, headers=headers, params=params)
        
        if not response.ok:
            # Log the full Amazon error body so we can see the actual reason
            logging.error(f"FBA Inventory API error {response.status_code}: {response.text}")
            response.raise_for_status()
            
        inventory_list = response.json().get("payload", {}).get("inventorySummaries", [])

        return [{"sku": item.get("sellerSku"), "fba_stock": item.get("inventoryDetails", {}).get("fulfillableQuantity", 0)} for item in inventory_list]

class AmazonAdsClient:
    """TODO: Implement actual ad spend fetching. Incomplete stub."""
    def __init__(self):
        raise NotImplementedError("AmazonAdsClient is not yet implemented.")
        self.client_id = os.environ.get("ADS_API_CLIENT_ID")
        self.client_secret = os.environ.get("ADS_API_CLIENT_SECRET")
        self.refresh_token = os.environ.get("ADS_API_REFRESH_TOKEN")
        self.profile_id = os.environ.get("ADS_PROFILE_ID") # Specific to her ad account
        
        # Ads use the same LWA token endpoint, but different API base URLs
        self.base_url = "https://advertising-api-eu.amazon.com" 
        self.access_token = None
        self.token_expiry = None

    def _refresh_access_token(self):
        """Exchanges the long-lived refresh token for a temporary access token."""
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(LWA_TOKEN_URL, data=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.token_expiry = datetime.now() + timedelta(seconds=data.get("expires_in", 3600) - 60)
            logging.info("Successfully refreshed Amazon Ads access token.")
        else:
            logging.error(f"Failed to refresh ads token: {response.text}")
            raise Exception("Amazon Ads LWA Authentication Failed")

    def get_headers(self):
        """Ensures we have a valid token and includes necessary ads headers."""
        if not self.access_token or not self.token_expiry or datetime.now() >= self.token_expiry:
            self._refresh_access_token()
            
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Amazon-Advertising-API-ClientId": self.client_id,
            "Amazon-Advertising-API-Scope": self.profile_id,
            "Content-Type": "application/json"
        }
