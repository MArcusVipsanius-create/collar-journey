
# TELLUM ULTIMUM™ v5

**Veni. Vidi. Perfeci.**

This version adds:

- Branded dashboard
- DEXA forecasting anchor
- Fat loss velocity and goal date forecast
- FatSecret daily text paste parser
- JPEG/PNG screenshot vault for Oura, FatSecret, Strong, workouts, and DEXA
- Oura quick entry
- Workout quick entry
- DEXA quick entry with prefilled June 19, 2025 DEXAFIT values

## Run

```powershell
cd "$HOME\Desktop\Programs\tellum_ultimum_v5"
pip install -r requirements.txt
python -m streamlit run app.py
```


## v6 Adaptive Deficit Coach

Adds:
- Daily Mission Rebalance
- Projected end-of-day total steps
- Projected total daily burn
- Workout burn correction
- Snack recommendation to return to the target 500-calorie deficit
- Workout-specific burn learning
- Weekly weight-trend calibration against predicted deficit
- Adaptive maintenance adjustment for better future forecasts


## v7 Import Hub

Adds a tabbed import screen:
- FatSecret Paste
- FatSecret JPG
- Oura JPG
- Strong / Workout JPG
- DEXA JPG
- Apple Health XML
- Import History

The app stores prior imports in SQLite, so when you restart the app, history and trends remain available. Use imports only for new updates.


## v8 Persistent Storage Fix

This version fixes:
- `NameError: name sqlite3 is not defined`
- Central persistent storage across app versions
- Uploads saved into source-specific folders

Data is now stored here:

`C:\Users\salim\Desktop\Programs\TellumUltimumData\tellum_ultimum.sqlite3`

Uploads are stored here:

`C:\Users\salim\Desktop\Programs\TellumUltimumData\TU Uploads\DEXA`
`C:\Users\salim\Desktop\Programs\TellumUltimumData\TU Uploads\FatSecret`
`C:\Users\salim\Desktop\Programs\TellumUltimumData\TU Uploads\Oura`
`C:\Users\salim\Desktop\Programs\TellumUltimumData\TU Uploads\Workouts`

Important: the old `tellum_ultimum.db` folder can stay there, but it is not used by v8.


## v9 Auto Inbox Scanner

Adds:
- Central Auto Inbox folder
- Folder scanner at startup/session
- File hash registry so the same document is not imported twice
- Automatic classification by filename and extension
- Auto-copy to source-specific archive folders
- Works with a locally synced Google Drive folder

Default inbox:

`C:\Users\salim\Desktop\Programs\TellumUltimumData\TU Inbox`

For Google Drive:
1. Install Google Drive for Desktop.
2. Sync the health data folder locally.
3. Put that local synced folder path into the Auto Inbox tab.
4. Click Scan inbox for new files.

The current version stores and registers files. Full OCR extraction from screenshots is the next upgrade.


## v10 OCR Import Queue

Adds:
- OCR attempt for JPG/PNG/WebP screenshots
- Content-based source classification
- Pending confirmation queue
- Confirm-before-import workflow
- Manual correction fields for FatSecret, Oura, Workout, and DEXA
- File hash duplicate prevention remains active

OCR notes:
- OCR uses `pytesseract` when available.
- On Windows, install the Tesseract OCR engine if you want OCR extraction.
- If OCR is not installed, files are still stored and queued for manual entry/confirmation.
- HEIC files are stored and archived, but automatic OCR may require conversion to JPG/PNG first unless HEIC support is added locally.

Recommended daily workflow:
1. Drop all screenshots/exports into the Health Data folder.
2. Open TELLUM ULTIMUM.
3. Go to Auto Inbox.
4. Click Scan inbox for new files.
5. Review OCR confirmation queue.
6. Confirm imports.


## v11 Mountain Pass Dashboard

Adds:
- Mountain Pass hero graphic.
- Days to Victory visual.
- Momentum based uphill, flat, or downhill road.
- Goal date drift messaging.
- Startup celebration / mission briefing.
- Goal date history tracking.
- Premium black and gold visual treatment.

## v12 Victory Dashboard

Fixes:
- Removes raw SVG code from the visible UI by rendering the visual in an HTML component.
- Removes raw JSON forecast blocks from the main Trajectory experience.
- Adds a polished Road to Victory dashboard card.
- Shows days to victory, goal date, momentum, fat remaining, current BF, goal BF, and target weight in a cleaner layout.


## v13 Light Victory Dashboard

Updates:
- Bright cream/navy/gold dashboard theme.
- Same preferred layout as the dark concept but with a clean daytime palette.
- Integrated Road to Victory graphic with days remaining as the road axis.
- Removed visible technical file paths from the landing page.
- Removed separate redundant road and days visuals.


## v14 Polished Light Layout

Fixes and upgrades:
- Renders the Road to Victory graphic closer to the preferred bright reference.
- Uses a true light cream, navy, gold, and blue palette.
- Improves the mountain graphic so it no longer looks like abstract blue shapes.
- Keeps the logo/tagline layout direction from the preferred design.
- Removes visible technical data paths from the main landing page.
- Uses unique Plotly keys to avoid duplicate chart errors.


## v15 Fixed

Fixes the Streamlit duplicate Plotly chart key error.
Also hides redundant technical path text from the main dashboard.


## v16 Manual Overrides

Change:
- Sidebar manual Current Weight and Current Body Fat now override imported/calculated values for the dashboard and forecast.
- Forecast recalculates fat mass, lean mass, target weight, fat remaining, days remaining, and goal date from the manual override values.


## v17 Clean Road to Victory

Updates:
- Removes Weight Trajectory chart.
- Removes Goal Date Momentum chart.
- Removes duplicate metric cards from the primary Command Center.
- Keeps a fixed original journey axis so the Road to Victory shows the full journey over time.
- Moves today's circle along the same original road toward the goal instead of resetting the axis each day.
- Keeps manual sidebar overrides as authoritative inputs for dashboard forecasting.
