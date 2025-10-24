# Weather Forecast Accuracy Tracker

Automatically tracks the accuracy of weather forecasts by comparing predictions to actual weather. Now collecting data from **two sources**: Open-Meteo and the National Weather Service (NWS).

## What It Does

- **Dual Data Collection**: Fetches forecasts from both Open-Meteo API and NWS API
- Every day at 8 AM UTC, GitHub Actions runs the tracker
- Fetches forecasts for 4 different lead times: 1-day, 3-day, 7-day, and 15-day ahead
- Saves all forecasts (Open-Meteo + NWS) for later comparison
- Currently scores Open-Meteo forecasts against actual weather (NWS scoring coming soon!)
- Results saved and dashboard updates automatically
- Beautiful gradient dashboard using sky blue and green color scheme

This gives you the **accuracy degradation curve**: See how forecast accuracy drops as you predict further into the future.

## Features

✅ **Open-Meteo Scoring**: Active accuracy tracking with ±3°F temperature tolerance  
✅ **NWS Data Collection**: Full raw data capture for future scoring  
✅ **Smart Caching**: NWS grid points cached after first fetch  
✅ **10 US Locations**: Major airports across all climate zones  
✅ **Automated**: Runs daily via GitHub Actions  
✅ **Free Hosting**: Dashboard hosted on Netlify

---

## Quick Start

### Step 1: Create a GitHub Repository

- Go to [https://github.com/new](https://github.com/new)
- Name it something like `weather-forecast-tracker`
- Make it **Public** (required for free GitHub Actions)
- Don't add README, .gitignore, or license (we'll add our files)
- Click **Create repository**

### Step 2: Upload Your Files

**Option A: Using GitHub's Web Interface**
- On your new repo page, click **uploading an existing file**
- Drag these files:
  - `weather_tracker.py`
  - `index.html`
- Create folder structure by clicking **"Create new file"** and typing `.github/workflows/daily-weather.yml`
- Commit the files

**Option B: Using Git (if you have it installed)**
```bash
# In your project folder
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/weather-forecast-tracker.git
git push -u origin main
```

### Step 3: Create Data Folders

GitHub Actions needs these folders to exist:
- In your repo, click **Add file** → **Create new file**
- Type: `data/forecasts/.gitkeep` and commit
- Repeat for: `data/.gitkeep`

(The `.gitkeep` files are just placeholder files so Git tracks the empty folders)

### Step 4: Enable GitHub Actions Permissions

- Go to your repo's **Settings** tab
- Click **Actions** → **General** (left sidebar)
- Under "Workflow permissions", select **Read and write permissions**
- Click **Save**

This lets GitHub Actions commit the weather data back to your repo.

### Step 5: Deploy to Netlify

- Go to [https://app.netlify.com](https://app.netlify.com)
- Click **Add new site** → **Import an existing project**
- Choose **GitHub** and authorize Netlify
- Select your `weather-forecast-tracker` repo
- Build settings:
  - Build command: (leave blank)
  - Publish directory: `/` (the root)
- Click **Deploy site**

Your dashboard will be live at something like `https://your-site-name.netlify.app`

### Step 6: Test It!

Don't wait for the scheduled run - test it manually:
- Go to your repo on GitHub
- Click the **Actions** tab
- Click **Daily Weather Forecast Tracker** (left sidebar)
- Click **Run workflow** → **Run workflow**
- Wait ~30 seconds for it to complete
- Check your Netlify site - it should show "No Data Yet" (which is correct!)

---

## Configuration

### Locations

The script tracks 10 major US airports for comprehensive coverage:
- **KBIS** - Bismarck, ND
- **KBOS** - Boston Logan
- **KDFW** - Dallas/Fort Worth
- **KDEN** - Denver International
- **KLAX** - Los Angeles International
- **KMIA** - Miami International
- **KOMA** - Omaha Eppley
- **KORD** - Chicago O'Hare
- **KPDX** - Portland International
- **KPHX** - Phoenix Sky Harbor

This gives excellent geographic diversity: Northeast, Southeast, South Central, Midwest, Central Plains, Mountain, Desert, Pacific Coast, and Pacific Northwest.

**To change locations:** Edit `weather_tracker.py` (around line 8):
```python
LOCATIONS = {
    "KORD": {"lat": 41.9742, "lon": -87.9073, "name": "Chicago O'Hare"},
    # Add more...
}
```

Use airport codes for consistency. Find coordinates at [https://www.latlong.net/](https://www.latlong.net/)

### Schedule

The script runs at **8:00 AM UTC** by default. To change this, edit `.github/workflows/daily-weather.yml`:

```yaml
- cron: '0 8 * * *'  # 8 AM UTC
```

Cron format: `minute hour * * *`
- `0 14 * * *` = 2 PM UTC (9 AM Central / 7 AM Arizona)
- `0 15 * * *` = 3 PM UTC (10 AM Central / 8 AM Arizona)

Use [https://crontab.guru/](https://crontab.guru/) to help with the format.

### Accuracy Tolerances

Edit these in `weather_tracker.py` (around line 18):

```python
TOLERANCES = {
    "temp_high": 3,  # degrees F
    "temp_low": 3,   # degrees F
    "precip": 0.1    # inches
}
```

Current settings:
- Temperature within **±3°F** = accurate
- Precipitation: **>0.1"** = "yes", **<0.1"** = "no"

---

## Timeline

- **Day 1** (tomorrow): First 1-day forecast scored! 🎉
- **Day 3**: First 3-day forecast scored
- **Day 7**: First 7-day forecast scored
- **Day 15**: First 15-day forecast scored
- **Ongoing**: New scores added daily for all lead times

You'll start seeing results immediately (tomorrow!) and build up a comprehensive accuracy degradation curve over the first 15 days.

---

## Data Sources

### Open-Meteo API (Currently Scored)
- **Forecast API**: [https://open-meteo.com/](https://open-meteo.com/)
- **Historical API**: [https://open-meteo.com/en/docs/historical-weather-api](https://open-meteo.com/en/docs/historical-weather-api)
- Free, no API key required
- Provides: High/low temps, precipitation forecasts and actuals

### National Weather Service API (Data Collection Only)
- **NWS API**: [https://www.weather.gov/documentation/services-web-api](https://www.weather.gov/documentation/services-web-api)
- Free, no API key required
- **Grid Point Caching**: Automatically caches location grid points after first fetch
- Provides: Full 7-day forecast periods with detailed data
- **Raw Data Stored**: Temperature ranges, precipitation probability, wind, humidity, detailed forecasts
- **Future Enhancement**: NWS scoring will be added in a future update

---

## Project Structure

```
weather-forecast-tracker/
├── .github/
│   └── workflows/
│       └── daily-weather.yml      # GitHub Actions config
├── data/
│   ├── forecasts/                 # Daily forecast files (auto-created)
│   ├── results.json               # Accuracy scores (auto-created)
│   └── nws_grid_cache.json        # Cached NWS grid points (auto-created)
├── weather_tracker.py             # Main Python script
├── index.html                     # Dashboard with gradient background
└── README.md                      # This file
```

---

## Troubleshooting

### Actions tab shows "no workflows"
- Make sure `.github/workflows/daily-weather.yml` is in the right folder
- Check that the repo is public

### Workflow fails with permission error
- Go to **Settings** → **Actions** → **General**
- Enable "Read and write permissions"

### Dashboard shows error
- Check that `data/results.json` exists in your repo
- Wait 15 days for first scores to appear

### NWS data not appearing
- Check Actions logs for any NWS API errors
- Grid points are cached on first run - check for `data/nws_grid_cache.json`
- NWS API occasionally has rate limits - the script will retry on next run

### Want to see what's happening?
- Go to **Actions** tab
- Click on a workflow run to see detailed logs

The script logs everything it does. Check the Actions tab for any runs and look at the logs if something seems wrong.

---

## Color Scheme

The dashboard uses a fresh gradient background:
- **Sky Blue** (`#4FC3F7`) → **Medium Green** (`#81C784`)
- Black text (`#000000`) for high contrast
- Green gradient bars (`#66BB6A` → `#81C784`) for accuracy indicators

---

## Future Enhancements

🔜 **NWS Forecast Scoring**: Compare NWS accuracy against Open-Meteo  
🔜 **Side-by-Side Comparison**: Dashboard showing both sources  
🔜 **Temperature Range Handling**: Smart parsing of NWS temperature ranges  

---

## License

Open source - feel free to use and modify!

---

**Questions or Issues?** Open an issue on GitHub or check the Actions logs for detailed debugging information.
