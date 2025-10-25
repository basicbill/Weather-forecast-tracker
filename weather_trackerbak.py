import requests
import json
from datetime import datetime, timedelta
import os

# Configuration
LOCATIONS = {
    "KBIS": {"lat": 46.7728, "lon": -100.7458, "name": "Bismarck, ND"},
    "KBOS": {"lat": 42.3656, "lon": -71.0096, "name": "Boston Logan"},
    "KDFW": {"lat": 32.8998, "lon": -97.0403, "name": "Dallas/Fort Worth"},
    "KDEN": {"lat": 39.8561, "lon": -104.6737, "name": "Denver International"},
    "KLAX": {"lat": 33.9416, "lon": -118.4085, "name": "Los Angeles International"},
    "KMIA": {"lat": 25.7959, "lon": -80.2870, "name": "Miami International"},
    "KOMA": {"lat": 41.3032, "lon": -95.8941, "name": "Omaha Eppley"},
    "KORD": {"lat": 41.9742, "lon": -87.9073, "name": "Chicago O'Hare"},
    "KPDX": {"lat": 45.5898, "lon": -122.5951, "name": "Portland International"},
    "KPHX": {"lat": 33.4352, "lon": -112.0101, "name": "Phoenix Sky Harbor"}
}

TOLERANCES = {
    "temp_high": 3,  # degrees F
    "temp_low": 3,   # degrees F
    "precip": 0.1    # inches
}

NWS_GRID_CACHE_FILE = "data/nws_grid_cache.json"

def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs("data/forecasts", exist_ok=True)
    os.makedirs("data", exist_ok=True)

def load_nws_grid_cache():
    """Load cached NWS grid points"""
    if os.path.exists(NWS_GRID_CACHE_FILE):
        with open(NWS_GRID_CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_nws_grid_cache(cache):
    """Save NWS grid points to cache"""
    with open(NWS_GRID_CACHE_FILE, 'w') as f:
        json.dump(cache, indent=2, fp=f)

def fetch_nws_grid_point(lat, lon):
    """Fetch NWS grid point data for a location"""
    url = f"https://api.weather.gov/points/{lat},{lon}"
    headers = {"User-Agent": "WeatherForecastTracker/1.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        properties = data.get("properties", {})
        return {
            "gridId": properties.get("gridId"),
            "gridX": properties.get("gridX"),
            "gridY": properties.get("gridY"),
            "forecast_url": properties.get("forecast")
        }
    except Exception as e:
        print(f"Error fetching NWS grid point for {lat},{lon}: {e}")
        return None

def get_nws_grid_point(location_code, lat, lon):
    """Get NWS grid point from cache or fetch if not cached"""
    cache = load_nws_grid_cache()
    
    if location_code in cache:
        return cache[location_code]
    
    print(f"Fetching NWS grid point for {location_code}...")
    grid_data = fetch_nws_grid_point(lat, lon)
    
    if grid_data:
        cache[location_code] = grid_data
        save_nws_grid_cache(cache)
        print(f"Cached NWS grid point for {location_code}")
    
    return grid_data

def fetch_nws_forecast(grid_data):
    """Fetch NWS 7-day forecast using grid point data"""
    if not grid_data or not grid_data.get("forecast_url"):
        return None
    
    headers = {"User-Agent": "WeatherForecastTracker/1.0"}
    
    try:
        response = requests.get(grid_data["forecast_url"], headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract periods (NWS gives day/night periods)
        periods = data.get("properties", {}).get("periods", [])
        
        # Store raw NWS data - we'll parse it later for scoring
        forecast_data = []
        for period in periods:
            forecast_data.append({
                "name": period.get("name"),
                "temperature": period.get("temperature"),
                "temperatureUnit": period.get("temperatureUnit"),
                "temperatureTrend": period.get("temperatureTrend"),
                "probabilityOfPrecipitation": period.get("probabilityOfPrecipitation", {}).get("value"),
                "dewpoint": period.get("dewpoint", {}).get("value"),
                "relativeHumidity": period.get("relativeHumidity", {}).get("value"),
                "windSpeed": period.get("windSpeed"),
                "windDirection": period.get("windDirection"),
                "shortForecast": period.get("shortForecast"),
                "detailedForecast": period.get("detailedForecast"),
                "isDaytime": period.get("isDaytime"),
                "startTime": period.get("startTime"),
                "endTime": period.get("endTime")
            })
        
        return forecast_data
    except Exception as e:
        print(f"Error fetching NWS forecast: {e}")
        return None

def fetch_open_meteo_forecast(lat, lon, days_ahead):
    """Fetch forecast from Open-Meteo API"""
    target_date = datetime.now() + timedelta(days=days_ahead)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
        "timezone": "America/Chicago",
        "start_date": target_date.strftime("%Y-%m-%d"),
        "end_date": target_date.strftime("%Y-%m-%d")
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "temp_high": data["daily"]["temperature_2m_max"][0],
            "temp_low": data["daily"]["temperature_2m_min"][0],
            "precip": data["daily"]["precipitation_sum"][0]
        }
    except Exception as e:
        print(f"Error fetching Open-Meteo forecast: {e}")
        return None

def fetch_open_meteo_actual(lat, lon, date):
    """Fetch actual weather from Open-Meteo Historical API"""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date,
        "end_date": date,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
        "timezone": "America/Chicago"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "temp_high": data["daily"]["temperature_2m_max"][0],
            "temp_low": data["daily"]["temperature_2m_min"][0],
            "precip": data["daily"]["precipitation_sum"][0]
        }
    except Exception as e:
        print(f"Error fetching actual weather: {e}")
        return None

def save_forecast(location, date, lead_time, open_meteo_data, nws_data):
    """Save forecast data with both Open-Meteo and NWS data"""
    filename = f"data/forecasts/{location}_{date}_{lead_time}day.json"
    forecast_data = {
        "location": location,
        "forecast_date": datetime.now().strftime("%Y-%m-%d"),
        "target_date": date,
        "lead_time_days": lead_time,
        "open_meteo": open_meteo_data,
        "nws": nws_data
    }
    
    with open(filename, 'w') as f:
        json.dump(forecast_data, f, indent=2)
    
    print(f"Saved forecast: {filename}")

def check_and_score_forecasts():
    """Check for forecasts ready to score and calculate accuracy"""
    today = datetime.now().strftime("%Y-%m-%d")
    results_file = "data/results.json"
    
    # Load existing results
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            results = json.load(f)
    else:
        results = {"scores": []}
    
    # Check each forecast file
    for filename in os.listdir("data/forecasts"):
        if not filename.endswith(".json"):
            continue
        
        with open(f"data/forecasts/{filename}", 'r') as f:
            forecast = json.load(f)
        
        # Check if this forecast is for today (ready to score)
        if forecast["target_date"] == today:
            # Check if already scored
            already_scored = any(
                s["location"] == forecast["location"] and 
                s["target_date"] == today and 
                s["lead_time_days"] == forecast["lead_time_days"]
                for s in results["scores"]
            )
            
            if already_scored:
                continue
            
            # Fetch actual weather
            location_data = LOCATIONS[forecast["location"]]
            actual = fetch_open_meteo_actual(
                location_data["lat"], 
                location_data["lon"], 
                today
            )
            
            if not actual or not forecast.get("open_meteo"):
                continue
            
            # Score Open-Meteo forecast only (NWS scoring comes later)
            open_meteo_forecast = forecast["open_meteo"]
            score = {
                "location": forecast["location"],
                "forecast_date": forecast["forecast_date"],
                "target_date": today,
                "lead_time_days": forecast["lead_time_days"],
                "forecasted": open_meteo_forecast,
                "actual": actual,
                "accuracy": {
                    "temp_high": abs(open_meteo_forecast["temp_high"] - actual["temp_high"]) <= TOLERANCES["temp_high"],
                    "temp_low": abs(open_meteo_forecast["temp_low"] - actual["temp_low"]) <= TOLERANCES["temp_low"],
                    "precip": (open_meteo_forecast["precip"] >= TOLERANCES["precip"]) == (actual["precip"] >= TOLERANCES["precip"])
                }
            }
            
            results["scores"].append(score)
            print(f"Scored forecast: {forecast['location']} {forecast['lead_time_days']}-day")
    
    # Save updated results
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

def main():
    """Main function to run daily"""
    print("Starting weather forecast tracker...")
    ensure_directories()
    
    # Fetch forecasts for multiple lead times
    lead_times = [1, 3, 7, 15]  # days ahead
    
    for location_code, location_data in LOCATIONS.items():
        print(f"\nProcessing {location_code} - {location_data['name']}")
        
        # Get NWS grid point (cached after first fetch)
        nws_grid = get_nws_grid_point(location_code, location_data["lat"], location_data["lon"])
        
        # Fetch NWS forecast once for this location
        nws_forecast = fetch_nws_forecast(nws_grid) if nws_grid else None
        
        for days_ahead in lead_times:
            target_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            
            # Fetch Open-Meteo forecast
            open_meteo_forecast = fetch_open_meteo_forecast(
                location_data["lat"],
                location_data["lon"],
                days_ahead
            )
            
            # Save both forecasts
            save_forecast(
                location_code,
                target_date,
                days_ahead,
                open_meteo_forecast,
                nws_forecast
            )
    
    # Check and score any forecasts that are ready
    print("\nChecking for forecasts ready to score...")
    check_and_score_forecasts()
    
    print("\nDone!")

if __name__ == "__main__":
    main()
