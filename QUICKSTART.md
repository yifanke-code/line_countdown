# Quick Start Guide - Countdown Web App

## For QNAP NAS Users (Like Your Setup)

### 1. Initial Setup

```bash
# SSH into your NAS
ssh admin@<your-nas-ip>

# Navigate to your working directory
cd /volume1/aria2  # or wherever you have the countdown files

# Install dependencies
pip3 install -r requirements-web.txt

# Set your LINE channel access token
export LINE_CHANNEL_ACCESS_TOKEN="your_line_token_here"
```

### 2. Start the Application

**Option A: Using the startup script (Recommended)**
```bash
chmod +x start_web.sh
./start_web.sh start
```

**Option B: Test first (to see actual errors)**
```bash
chmod +x test_run.sh
./test_run.sh
```
This runs the app in foreground so you can see any error messages directly.

**Option C: Simple background command**
```bash
nohup python3 countdown_web.py > countdown_web.log 2>&1 &
```

### 3. Access the Web Interface

Open your browser and go to:
```
http://<your-nas-ip>:5000
```

Example: `http://192.168.1.100:5000`

### 4. Using the Web Interface

1. **Timezone**: Select from dropdown (e.g., UTC-5, Asia/Taipei, CST, etc.)
2. **DateTime**: Enter 10-digit format (YYMMDDHHMI)
   - Example: `2609092225` = Sept 22, 2026 at 22:25
3. **Message**: Optional (e.g., "Airtags", "Meeting")
4. **Recipients**: Check who should receive notifications (Evan, Cheryl, etc.)
5. **Click**: "Start Countdown" button
6. **Monitor**: Watch the log in real-time

### 5. Stop the Application

**Using startup script:**
```bash
./start_web.sh stop
```

**Manual stop:**
```bash
ps aux | grep countdown_web  # Find the PID
kill <PID>
```

## Common Tasks

### View Application Logs
```bash
./start_web.sh logs
# or
tail -f countdown_web.log
```

### View Countdown Execution Log
Access through web UI (auto-refreshes every 2 seconds)

Or via command line:
```bash
tail -f run_countdown.log
```

### Restart Application
```bash
./start_web.sh restart
```

### Change Port (if 5000 is busy)
Edit `countdown_web.py`, line 108:
```python
app.run(debug=False, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

Then restart.

## DateTime Format Reference

Format: **YYMMDDHHMI** (10 digits)

| Component | Range | Example |
|-----------|-------|---------|
| YY (Year) | 00-99 | 26 = 2026 |
| MM (Month) | 01-12 | 09 = September |
| DD (Day) | 01-31 | 22 = 22nd |
| HH (Hour) | 00-23 | 14 = 2:00 PM |
| MI (Minute) | 00-59 | 30 = :30 |

**Examples:**
- `2609092225` → 2026/09/22 22:25
- `2612312359` → 2026/12/31 23:59
- `2605201722` → 2026/05/20 17:22
- `2603011000` → 2026/03/01 10:00

## Timezone Quick Reference

### Common Abbreviations
- **EST/EDT**: Eastern (New York)
- **CST/CDT**: Central (Chicago)
- **MST/MDT**: Mountain (Denver)
- **PST/PDT**: Pacific (Los Angeles)
- **GMT/BST**: London
- **CET/CEST**: Paris
- **JST**: Tokyo
- **HKT**: Hong Kong
- **SGT**: Singapore
- **AEST/AEDT**: Sydney

### UTC Offsets
- `UTC` (UTC+0)
- `UTC+8` (Beijing, Singapore, Hong Kong)
- `UTC-5` (Eastern US)
- `UTC-8` (Pacific US)

### IANA Format
- `Asia/Taipei`
- `America/New_York`
- `Europe/London`
- `Australia/Sydney`

## Troubleshooting

### "Permission denied: '/dev/shm/...'" Error
✅ **Fixed in current version** - app runs in production mode

### "Cannot connect to web interface"
- Check if app is running: `./start_web.sh status`
- Check firewall - port 5000 must be open
- Try localhost first: `http://localhost:5000`
- Check NAS IP: `ifconfig` or check NAS admin panel

### "No log data yet"
- Wait a few seconds for the countdown to start
- Check that `countdown_linux.py` exists in same directory
- Verify `LINE_CHANNEL_ACCESS_TOKEN` is set

### Countdown won't send notifications
- Verify `LINE_CHANNEL_ACCESS_TOKEN` is correct
- Check recipient names are exactly: "Evan", "Cheryl", or "Group Chat 1"
- View logs for error messages: `./start_web.sh logs`

## Files Overview

| File | Purpose |
|------|---------|
| `countdown_web.py` | Flask web application |
| `countdown_linux.py` | CLI countdown script with LINE integration |
| `templates/index.html` | Web UI interface |
| `start_web.sh` | Linux/NAS startup script |
| `start_web.bat` | Windows startup script |
| `requirements-web.txt` | Python dependencies |
| `run_countdown.log` | Countdown execution log (auto-generated) |
| `countdown_web.log` | Web app logs (auto-generated) |

## For More Details

See `WEB_APP_GUIDE.md` for comprehensive documentation.
