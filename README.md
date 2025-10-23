# 15-Day Weather Forecast Accuracy Tracker

Automatically tracks the accuracy of 15-day weather forecasts by comparing predictions to actual weather.

## How It Works

1. **Every day at 8 AM UTC**, GitHub Actions runs the tracker
2. It fetches the **day-15 forecast** for your locations and saves it
3. It checks if there's a forecast from **15 days ago** to score
4. If yes, it fetches the actual weather and compares it
5. Results are saved and the dashboard updates automatically

## Setup Instructions

### 1. Create a New GitHub Repository

1. Go to https://github.com/new
2. Name it something like `weather-forecast-tracker`
3. Make it **Public** (required for free GitHub Actions)
4. Don't add README, .gitignore, or license (we'll add our files)
5. Click **Create repository**

### 2. Upload Your Files

You have two options:

**Option A: Using GitHub's Web Interface**

1. On your new repo page, click **uploading an existing file**
2. Drag these files:
   - `weather_tracker.py`
   - `index.html`
   - Create folder structure by clicking "Create new file" and typing `.github/workflows/daily-weather.yml`
3. Commit the files

**Option B: Using Git (if you have it installed)**

```bash
# In your project folder
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/weather-forecast-tracker.git
git push -u origin main
```

### 3. Create the Data Folder Structure

GitHub Actions needs these folders to exist:

1. In your repo, click **Add file** → **Create new file**
2. Type: `data/forecasts/.gitkeep` and commit
3. Repeat for: `data/.gitkeep`

(The `.gitkeep` files are just placeholder files so Git tracks the empty folders)

### 4. Enable GitHub Actions

1. Go to your repo's **Settings** tab
2. Click **Actions** → **General** (left sidebar)
3. Under "Workflow permissions", select **Read and write permissions**
4. Click **Save**

This lets GitHub Actions commit the weather data back to your repo.

### 5. Connect to Netlify

1. Go to https://app.netlify.com
2. Click **Add new site** → **Import an existing project**
3. Choose **GitHub** and authorize Netlify
4. Select your `weather-forecast-tracker` repo
5. Build settings:
   - Build command: (leave blank)
   - Publish directory: `/` (the root)
6. Click **Deploy site**

Your dashboard will be live at something like `https://your-site-name.netlify.app`

### 6. Test It!

Don't wait for the scheduled run - test it manually:

1. Go to your repo on GitHub
2. Click the **Actions** tab
3. Click **Daily Weather Forecast Tracker** (left sidebar)
4. Click **Run workflow** → **Run workflow**
5. Wait ~30 seconds for it to complete
6. Check your Netlify site - it should show "No Data Yet" (which is correct!)

### 7. Customize Your Locations

The script is already configured with 10 major US airports for comprehensive coverage across all climate zones:

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

If you want to change these, edit `weather_tracker.py` (around line 11):

```python
LOCATIONS = {
    "KORD": {"lat": 41.9742, "lon": -87.9073, "name": "Chicago O'Hare"},
    # Add more...
}
```

Use airport codes for consistency. Find coordinates at https://www.latlong.net/

### 8. Adjust the Run Time (Optional)

The script runs at 8:00 AM UTC by default. To change this, edit `.github/workflows/daily-weather.yml`:

```yaml
- cron: '0 8 * * *'  # 8 AM UTC
```

Cron format: `minute hour * * *`
- `0 14 * * *` = 2 PM UTC (9 AM Central / 7 AM Arizona)
- `0 15 * * *` = 3 PM UTC (10 AM Central / 8 AM Arizona)

Use https://crontab.guru/ to help with the format.

## How Long Until I See Results?

- **Day 1-14:** The tracker is collecting forecasts. Dashboard says "No Data Yet"
- **Day 15:** First score appears! 🎉
- **Ongoing:** New scores added daily

## Tolerance Settings

Edit these in `weather_tracker.py` (around line 18):

```python
TOLERANCES = {
    "temp_high": 3,  # degrees F
    "temp_low": 3,   # degrees F
    "precip": 0.1    # inches
}
```

Current settings:
- Temperature within ±3°F = accurate
- Precipitation: >0.1" = "yes", <0.1" = "no"

## File Structure

```
weather-forecast-tracker/
├── .github/
│   └── workflows/
│       └── daily-weather.yml    # GitHub Actions config
├── data/
│   ├── forecasts/              # Daily forecast files (auto-created)
│   └── results.json            # Accuracy scores (auto-created)
├── weather_tracker.py          # Main Python script
├── index.html                  # Dashboard
└── README.md                   # This file
```

## Troubleshooting

**Actions tab shows "no workflows"**
- Make sure `.github/workflows/daily-weather.yml` is in the right folder
- Check that the repo is public

**Workflow fails with permission error**
- Go to Settings → Actions → General
- Enable "Read and write permissions"

**Dashboard shows error**
- Check that `data/results.json` exists in your repo
- Wait 15 days for first scores to appear

**Want to see what's happening?**
- Go to Actions tab
- Click on a workflow run to see detailed logs

## Questions?

The script logs everything it does. Check the Actions tab for any runs and look at the logs if something seems wrong.

## Credits

Uses the free Open-Meteo API for weather data:
- Forecast API: https://open-meteo.com/
- Historical API: https://open-meteo.com/en/docs/historical-weather-api
