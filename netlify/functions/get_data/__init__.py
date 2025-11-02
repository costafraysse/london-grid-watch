"""
Netlify serverless function to fetch Octopus prices and carbon data.
This runs on-demand when the frontend requests data.
"""

import json
import requests
from datetime import datetime, timedelta, timezone


def handler(event, context=None):
    """
    Netlify function handler - called when frontend hits the API.
    Returns JSON with prices and carbon data.
    """
    
    # Handle both dict and object-style events
    if event is None:
        event = {}
    
    # Get parameters from query string (default to London)
    if isinstance(event, dict):
        params = event.get('queryStringParameters') or {}
    else:
        params = getattr(event, 'queryStringParameters', None) or {}
    
    region = params.get('region', 'C') if isinstance(params, dict) else 'C'
    days_back = 1
    days_forward = 2
    
    try:
        # Fetch Octopus prices
        prices = fetch_octopus_prices(region, days_back, days_forward)
        
        # Fetch carbon intensity
        carbon = fetch_carbon_intensity(days_back, days_forward)
        
        # Return JSON response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'prices': prices,
                'carbon': carbon,
                'region': region,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        }
    
    except Exception as e:
        import traceback
        error_details = {
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(error_details)
        }


def fetch_octopus_prices(region, days_back, days_forward):
    """Fetch Octopus Agile prices."""
    product_code = "AGILE-24-10-01"
    tariff_code = f"E-1R-{product_code}-{region}"
    
    now_utc = datetime.now(timezone.utc)
    start_utc = now_utc - timedelta(days=days_back)
    end_utc = now_utc + timedelta(days=days_forward)
    
    url = f"https://api.octopus.energy/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates/"
    
    params = {
        "period_from": start_utc.isoformat().replace("+00:00", "Z"),
        "period_to": end_utc.isoformat().replace("+00:00", "Z"),
        "page_size": 2500,
    }
    
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    
    return resp.json().get('results', [])


def fetch_carbon_intensity(days_back, days_forward):
    """Fetch London carbon intensity."""
    now_utc = datetime.now(timezone.utc)
    start_utc = now_utc - timedelta(days=days_back)
    end_utc = now_utc + timedelta(days=days_forward)
    
    start_str = start_utc.strftime("%Y-%m-%dT%H:%MZ")
    end_str = end_utc.strftime("%Y-%m-%dT%H:%MZ")
    
    url = f"https://api.carbonintensity.org.uk/regional/intensity/{start_str}/{end_str}/regionid/13"
    
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    
    data = resp.json()
    return data.get('data', {}).get('data', [])

