#!/usr/bin/env python3
"""
Weather Forecast Accuracy Tracker
Fetches 15-day forecasts daily and compares them to actual weather
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.error

# Configuration
LOCATIONS = {
    "KBIS": {"lat": 46.7727, "lon": -100.7467, "name": "Bismarck"},
    "KBOS": {"lat": 42.3656, "lon": -71.0096, "name": "Boston Logan"},
    "KDFW": {"lat": 32.8998, "lon": -97.0403, "name": "Dallas/Fort Worth"},
    "KDEN": {"lat": 39.8561, "lon": -104.6737, "name": "Denver Intl"},
    "KLAX": {"lat": 33.9416, "lon": -118.4085, "name": "Los Angeles Intl"},
    "KMIA": {"lat": 25.7959, "lon": -80.2870, "name": "Miami Intl"},
    "KOMA": {"lat": 41.3032, "lon": -95.8941, "name": "Omaha Eppley"},
    "KORD": {"lat": 41.9742, "lon": -87.9073, "name": "Chicago O'Hare"},
    "KPDX": {"lat": 45.5898, "lon": -122.5951, "name": "Portland Intl"},
    "KPHX": {"lat": 33.4342, "lon": -112.0080, "name": "Phoenix Sky Harbor"}
}

TOLERANCES = {
    "temp_high": 3,  # degrees F
    "temp_low": 3,   # degrees F
    "precip": 0.1    # inches (for yes/no determination)
}

# Lead times to track (days ahead to forecast)
LEAD_TIMES = [1, 3, 7, 15]

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
FORECASTS_DIR = DATA_DIR / "forecasts"
RESULTS_FILE = DATA_DIR / "results.json"


def ensure_directories():
    """Create necessary directories if they don't exist"""
    FORECASTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_weather_data(lat, lon):
    """Fetch 15-day forecast from Open-Meteo API"""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
        f"&temperature_unit=fahrenheit&precipitation_unit=inch"
        f"&timezone=auto&forecast_days=16"
    )
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Error fetching weather data: {e}")
        return None


def get_weather_condition(weather_code):
    """Convert weather code to simple condition category"""
    if weather_code is None:
        return "unknown"
    
    # WMO Weather interpretation codes
    if weather_code == 0:
        return "clear"
    elif weather_code in [1, 2]:
        return "partly_cloudy"
    elif weather_code == 3:
        return "cloudy"
    elif weather_code in [45, 48]:
        return "foggy"
    elif weather_code in [51, 53, 55, 56, 57]:
        return "drizzle"
    elif weather_code in [61, 63, 65, 66, 67, 80, 81, 82]:
        return "rainy"
    elif weather_code in [71, 73, 75, 77, 85, 86]:
        return "snowy"
    elif weather_code in [95, 96, 99]:
        return "stormy"
    else:
        return "unknown"


def save_daily_forecasts():
    """Fetch and save forecasts for multiple lead times for all locations"""
    today = datetime.now().date()
    
    print(f"\n📅 Today: {today}")
    print(f"🔮 Fetching forecasts for lead times: {LEAD_TIMES} days")
    
    # Structure: { lead_time: { date_made, forecast_for, locations: {...} } }
    forecasts_by_lead_time = {}
    
    for lead_time in LEAD_TIMES:
        forecast_date = today + timedelta(days=lead_time)
        forecasts_by_lead_time[lead_time] = {
            "lead_time": lead_time,
            "date_made": str(today),
            "forecast_for": str(forecast_date),
            "locations": {}
        }
    
    # Fetch weather data once per location (it includes all days)
    for location_name, coords in LOCATIONS.items():
        print(f"\n📍 Fetching {location_name}...")
        
        data = fetch_weather_data(coords["lat"], coords["lon"])
        if not data or "daily" not in data:
            print(f"  ❌ Failed to fetch data for {location_name}")
            continue
        
        daily = data["daily"]
        if len(daily["time"]) < max(LEAD_TIMES) + 1:
            print(f"  ⚠️  Not enough forecast data for {location_name}")
            continue
        
        # Extract forecasts for each lead time
        for lead_time in LEAD_TIMES:
            forecast_index = lead_time
            
            forecast_info = {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "temp_high": daily["temperature_2m_max"][forecast_index],
                "temp_low": daily["temperature_2m_min"][forecast_index],
                "precipitation": daily["precipitation_sum"][forecast_index],
                "weather_code": daily["weather_code"][forecast_index],
                "condition": get_weather_condition(daily["weather_code"][forecast_index])
            }
            
            forecasts_by_lead_time[lead_time]["locations"][location_name] = forecast_info
        
        # Print summary for this location
        print(f"  ✅ Saved forecasts for {len(LEAD_TIMES)} lead times")
    
    # Save each lead time to a separate file
    for lead_time, forecast_data in forecasts_by_lead_time.items():
        filename = FORECASTS_DIR / f"{today}_lead{lead_time}.json"
        with open(filename, 'w') as f:
            json.dump(forecast_data, f, indent=2)
        print(f"\n💾 Saved {lead_time}-day forecast to: {filename}")
    
    return forecasts_by_lead_time


def fetch_actual_weather(lat, lon, date):
    """Fetch actual weather for a specific date using historical data"""
    # Open-Meteo historical API
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={date}&end_date={date}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
        f"&temperature_unit=fahrenheit&precipitation_unit=inch"
        f"&timezone=auto"
    )
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if "daily" in data and len(data["daily"]["time"]) > 0:
                return {
                    "temp_high": data["daily"]["temperature_2m_max"][0],
                    "temp_low": data["daily"]["temperature_2m_min"][0],
                    "precipitation": data["daily"]["precipitation_sum"][0],
                    "weather_code": data["daily"]["weather_code"][0],
                    "condition": get_weather_condition(data["daily"]["weather_code"][0])
                }
    except urllib.error.URLError as e:
        print(f"Error fetching actual weather: {e}")
    
    return None


def score_forecast(forecast, actual, location_name):
    """Compare forecast to actual weather and calculate score"""
    scores = {}
    
    # Temperature High
    temp_high_diff = abs(forecast["temp_high"] - actual["temp_high"])
    scores["temp_high"] = {
        "forecast": forecast["temp_high"],
        "actual": actual["temp_high"],
        "diff": round(temp_high_diff, 1),
        "accurate": temp_high_diff <= TOLERANCES["temp_high"]
    }
    
    # Temperature Low
    temp_low_diff = abs(forecast["temp_low"] - actual["temp_low"])
    scores["temp_low"] = {
        "forecast": forecast["temp_low"],
        "actual": actual["temp_low"],
        "diff": round(temp_low_diff, 1),
        "accurate": temp_low_diff <= TOLERANCES["temp_low"]
    }
    
    # Precipitation (yes/no)
    forecast_precip = forecast["precipitation"] > TOLERANCES["precip"]
    actual_precip = actual["precipitation"] > TOLERANCES["precip"]
    scores["precipitation"] = {
        "forecast": "yes" if forecast_precip else "no",
        "actual": "yes" if actual_precip else "no",
        "forecast_amount": round(forecast["precipitation"], 2),
        "actual_amount": round(actual["precipitation"], 2),
        "accurate": forecast_precip == actual_precip
    }
    
    # Weather Condition
    scores["condition"] = {
        "forecast": forecast["condition"],
        "actual": actual["condition"],
        "accurate": forecast["condition"] == actual["condition"]
    }
    
    # Overall accuracy
    accurate_count = sum(1 for s in scores.values() if s["accurate"])
    total_count = len(scores)
    scores["overall"] = {
        "accurate_count": accurate_count,
        "total_count": total_count,
        "percentage": round((accurate_count / total_count) * 100, 1)
    }
    
    return scores


def check_and_score_old_forecasts():
    """Check for forecasts at each lead time and score them"""
    today = datetime.now().date()
    
    # Load existing results
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE, 'r') as f:
            all_results = json.load(f)
    else:
        all_results = {"scores": [], "by_lead_time": {str(lt): [] for lt in LEAD_TIMES}}
    
    scored_anything = False
    
    # Check each lead time
    for lead_time in LEAD_TIMES:
        days_ago = today - timedelta(days=lead_time)
        forecast_file = FORECASTS_DIR / f"{days_ago}_lead{lead_time}.json"
        
        if not forecast_file.exists():
            continue
        
        print(f"\n🎯 Found {lead_time}-day forecast from {days_ago} - time to score it!")
        
        # Load the old forecast
        with open(forecast_file, 'r') as f:
            forecast_data = json.load(f)
        
        forecast_for_date = forecast_data["forecast_for"]
        
        # Check if we've already scored this
        already_scored = any(
            r["forecast_for"] == forecast_for_date and r["lead_time"] == lead_time
            for r in all_results["scores"]
        )
        
        if already_scored:
            print(f"  ⚠️  Already scored this {lead_time}-day forecast, skipping")
            continue
        
        print(f"📊 Scoring {lead_time}-day forecast for: {forecast_for_date}")
        
        result_entry = {
            "lead_time": lead_time,
            "date_made": forecast_data["date_made"],
            "forecast_for": forecast_for_date,
            "scored_on": str(today),
            "locations": {}
        }
        
        # Score each location
        for location_name, forecast in forecast_data["locations"].items():
            print(f"\n📍 Scoring {location_name}...")
            
            actual = fetch_actual_weather(
                forecast["lat"], 
                forecast["lon"], 
                forecast_for_date
            )
            
            if actual is None:
                print(f"  ❌ Could not fetch actual weather for {location_name}")
                continue
            
            scores = score_forecast(forecast, actual, location_name)
            result_entry["locations"][location_name] = scores
            
            print(f"  🌡️  Temp High: {scores['temp_high']['forecast']}°F → {scores['temp_high']['actual']}°F "
                  f"({'✅' if scores['temp_high']['accurate'] else '❌'} {scores['temp_high']['diff']}° diff)")
            print(f"  🌡️  Temp Low: {scores['temp_low']['forecast']}°F → {scores['temp_low']['actual']}°F "
                  f"({'✅' if scores['temp_low']['accurate'] else '❌'} {scores['temp_low']['diff']}° diff)")
            print(f"  🌧️  Precip: {scores['precipitation']['forecast']} → {scores['precipitation']['actual']} "
                  f"({'✅' if scores['precipitation']['accurate'] else '❌'})")
            print(f"  ☁️  Condition: {scores['condition']['forecast']} → {scores['condition']['actual']} "
                  f"({'✅' if scores['condition']['accurate'] else '❌'})")
            print(f"  📊 Overall: {scores['overall']['percentage']}% accurate")
        
        # Add to results
        all_results["scores"].append(result_entry)
        
        # Also organize by lead time for easier analysis
        lead_time_key = str(lead_time)
        if lead_time_key not in all_results["by_lead_time"]:
            all_results["by_lead_time"][lead_time_key] = []
        all_results["by_lead_time"][lead_time_key].append(result_entry)
        
        scored_anything = True
        print(f"\n✅ Completed scoring {lead_time}-day forecast")
    
    if scored_anything:
        all_results["last_updated"] = str(today)
        
        with open(RESULTS_FILE, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n💾 Saved results to: {RESULTS_FILE}")
    else:
        print(f"\n📭 No forecasts ready to score yet")



def main():
    """Main execution function"""
    print("=" * 60)
    print("🌤️  Weather Forecast Accuracy Tracker")
    print("=" * 60)
    
    ensure_directories()
    
    # Step 1: Save today's forecasts for all lead times
    save_daily_forecasts()
    
    # Step 2: Check if any forecasts are ready to score and score them
    check_and_score_old_forecasts()
    
    print("\n" + "=" * 60)
    print("✅ Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
