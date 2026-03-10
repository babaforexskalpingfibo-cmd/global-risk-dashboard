#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Risk Dashboard - Application Flask
Monitoring géopolitique en temps réel avec multiples APIs fiables
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_caching import Cache
from datetime import datetime
import logging
import requests
from typing import Dict, Any, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    SECRET_KEY = 'dev-key-change-in-prod'
    DEBUG = False
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
cache = Cache(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# BASE API CLASS
# ============================================================================

class BaseAPI:
    """Classe de base pour toutes les APIs"""
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                headers={"User-Agent": "GlobalRiskDashboard/1.0"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API Error ({self.base_url}): {str(e)}")
            return {"error": str(e), "data": []}

# ============================================================================
# API IMPLEMENTATIONS
# ============================================================================

class GDACSApi(BaseAPI):
    """Catastrophes naturelles - Pas de clé requise"""
    def __init__(self):
        super().__init__("https://www.gdacs.org/gdacsapi/api")
    
    def get_alerts(self, limit: int = 100):
        data = self.get("/events", params={"limit": limit})
        if "error" in data:
            return []
        
        alerts = []
        for event in data.get("events", []):
            try:
                alerts.append({
                    "id": event.get("eventid"),
                    "type": event.get("eventtype"),
                    "country": event.get("country"),
                    "severity": event.get("alertlevel"),
                    "latitude": float(event.get("latitude", 0)),
                    "longitude": float(event.get("longitude", 0)),
                    "date": event.get("fromdate"),
                    "title": event.get("eventname"),
                })
            except (ValueError, TypeError):
                continue
        return sorted(alerts, key=lambda x: x.get("severity", ""), reverse=True)

class CoinGeckoApi(BaseAPI):
    """Données crypto - Pas de clé requise"""
    def __init__(self):
        super().__init__("https://api.coingecko.com/api/v3")
    
    def get_global_market(self):
        data = self.get("/global")
        if "error" in data:
            return {}
        return {
            "btc_dominance": data.get("data", {}).get("btc_market_cap_percentage", {}).get("btc", 0),
            "market_cap_change_24h": data.get("data", {}).get("market_cap_change_percentage_24h_usd", 0)
        }
    
    def get_top_coins(self, limit: int = 10):
        data = self.get("/coins/markets", params={
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "sparkline": False
        })
        if "error" in data:
            return []
        
        coins = []
        for coin in data:
            coins.append({
                "id": coin.get("id"),
                "name": coin.get("name"),
                "symbol": coin.get("symbol").upper(),
                "price": coin.get("current_price"),
                "market_cap": coin.get("market_cap"),
                "change_24h": coin.get("price_change_percentage_24h")
            })
        return coins

class CountriesApi(BaseAPI):
    """Données pays - Pas de clé requise"""
    def __init__(self):
        super().__init__("https://restcountries.com/v3.1")
    
    def get_all_countries(self):
        data = self.get("/all")
        if "error" in data:
            return []
        
        countries = []
        for country_data in data:
            try:
                latlng = country_data.get("latlng", [0, 0])
                countries.append({
                    "name": country_data.get("name", {}).get("common", ""),
                    "code": country_data.get("cca2", ""),
                    "latitude": latlng[0],
                    "longitude": latlng[1],
                    "region": country_data.get("region", ""),
                    "population": country_data.get("population", 0),
                })
            except (KeyError, IndexError, TypeError):
                continue
        return countries

# ============================================================================
# INITIALISATION DES APIs
# ============================================================================

gdacs_api = GDACSApi()
coingecko_api = CoinGeckoApi()
countries_api = CountriesApi()

# ============================================================================
# ROUTES PRINCIPALES
# ============================================================================

@app.route('/')
def index():
    """Page principale du dashboard"""
    return render_template('dashboard.html')

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/disasters')
@cache.cached(timeout=300)
def get_disasters():
    try:
        alerts = gdacs_api.get_alerts()
        return jsonify({
            "status": "success",
            "count": len(alerts),
            "timestamp": datetime.utcnow().isoformat(),
            "data": alerts
        })
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/crypto-market')
@cache.cached(timeout=300)
def get_crypto_market():
    try:
        global_data = coingecko_api.get_global_market()
        top_coins = coingecko_api.get_top_coins(10)
        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "global": global_data,
            "top_coins": top_coins
        })
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/countries')
@cache.cached(timeout=3600)
def get_countries():
    try:
        countries = countries_api.get_all_countries()
        return jsonify({
            "status": "success",
            "count": len(countries),
            "data": countries
        })
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/dashboard-summary')
@cache.cached(timeout=300)
def get_dashboard_summary():
    try:
        disasters = gdacs_api.get_alerts()
        crypto = coingecko_api.get_global_market()
        countries = countries_api.get_all_countries()
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "disasters": {
                "count": len(disasters),
                "critical": len([d for d in disasters if d.get('severity') == 'Red']),
                "data": disasters[:10]
            },
            "crypto": crypto,
            "countries_count": len(countries),
            "last_updated": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "Resource not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
