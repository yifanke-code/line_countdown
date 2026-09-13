# Countdown Web Application Guide

This is a web-based UI for managing and executing the `countdown_linux.py` script with LINE notifications.

## Features

- 🎨 Clean, intuitive web interface for configuring countdown parameters
- 🌍 Support for multiple timezones (abbreviations, UTC offsets, IANA zones)
- 👥 Multiple recipient selection (Evan, Cheryl, Group Chat 1)
- 📋 Real-time execution log viewer with auto-refresh
- ⚙️ Automatic log file cleanup before each run
- 🔄 Background execution without blocking the UI

## Installation

### Prerequisites
- Python 3.7+
- `countdown_linux.py` in the same directory
- LINE channel access token (set `LINE_CHANNEL_ACCESS_TOKEN` environment variable)

### Setup

1. Install dependencies:
```bash
pip install -r requirements-web.txt
```

2. Set the LINE channel access token:
```bash
export LINE_CHANNEL_ACCESS_TOKEN="your_token_here"
```

3. Run the web application:
```bash
python countdown_web.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```
Or access from another machine:
```
http://<server-ip>:5000
```

### Linux/NAS Deployment

The application runs in production mode (debug disabled) to avoid permission issues with `/dev/shm` on restricted systems like QNAP NAS.

#### Using Startup Script (Recommended)

```bash
# Make script executable
chmod +x start_web.sh

# Start the application
./start_web.sh start

# Stop the application
./start_web.sh stop

# Restart the application
./start_web.sh restart

# Check status
./start_web.sh status

# View logs
./start_web.sh logs
```

#### Manual Start

```bash
# Simple start
python3 countdown_web.py

# Run in background with nohup
nohup python3 countdown_web.py > countdown_web.log 2>&1 &

# Or use screen for persistent session
screen -S countdown
python3 countdown_web.py
# Press Ctrl+A then D to detach from screen
```

### Windows Deployment

**Using Startup Batch File:**

```bash
# Simply double-click: start_web.bat
# Or run from Command Prompt:
start_web.bat
```

**Manual Start:**

```bash
python countdown_web.py
```

## Usage

### Basic Workflow

1. **Select Timezone**: Choose from North America, Europe, Asia-Pacific, UTC offsets, or IANA zones
2. **Enter DateTime**: Use 10-digit format (YYMMDDHHMI)
   - Example: `2609092225` → 2026/09/22 22:25
3. **Add Message** (Optional): Customize the notification subject (e.g., "Airtags", "Meeting")
4. **Select Recipients**: Check one or more users to receive notifications
5. **Click Start Countdown**: Execution begins in the background
6. **Monitor Log**: View real-time execution log and notifications

### DateTime Format

The datetime input uses a 10-digit format: **YYMMDDHHMI**

- `YY`: Year (00-99, interpreted as 20YY)
- `MM`: Month (01-12)
- `DD`: Day (01-31)
- `HH`: Hour (00-23)
- `MI`: Minute (00-59)

**Examples:**
- `2609092225` → September 22, 2026 at 22:25
- `2612312359` → December 31, 2026 at 23:59
- `2605201722` → May 20, 2026 at 17:22

### Timezone Reference

#### North America
- **EST/EDT**: Eastern Time
- **CST/CDT**: Central Time
- **MST/MDT**: Mountain Time
- **PST/PDT**: Pacific Time

#### Europe
- **GMT/BST**: London (UK)
- **CET/CEST**: Paris (France)
- **WET/WEST**: Lisbon (Portugal)
- **EET/EEST**: Athens (Greece)

#### Asia-Pacific
- **JST**: Tokyo (Japan)
- **KST**: Seoul (Korea)
- **SGT**: Singapore
- **HKT**: Hong Kong
- **IST**: India
- **AEST/AEDT**: Sydney (Australia)
- **NZST/NZDT**: Auckland (New Zealand)

#### UTC Offsets
- `UTC`, `UTC+0` through `UTC+12`, `UTC-1` through `UTC-12`

#### IANA Timezones
- Common timezones like `Asia/Taipei`, `America/New_York`, etc.

## Backend Command

When you submit the form, the application executes:

```bash
/usr/local/bin/python3 -u countdown_linux.py -tz {timezone} -dt {datetime} -m "{message}" -u {user1} -u {user2} ... >> run_countdown.log 2>&1 &
```

### Key Points
- Log file (`run_countdown.log`) is automatically deleted before each new execution
- The process runs in the background (the `&` at the end)
- All output is captured in `run_countdown.log`
- The web UI auto-refreshes the log every 2 seconds

## Execution Flow

1. User submits form through web UI
2. Application validates all inputs
3. Deletes previous `run_countdown.log` (if exists)
4. Spawns background process running countdown_linux.py
5. Log viewer auto-refreshes to show execution progress
6. Notifications are sent through LINE at scheduled times:
   - 10 minutes before target
   - At target time
   - Every 10 minutes for a total of 10 notifications

## Log File

- **Default location**: `run_countdown.log` (same directory as countdown_web.py)
- **Format**: Captures all stdout and stderr from countdown_linux.py
- **Auto-refresh**: Web UI refreshes every 2 seconds
- **Auto-cleanup**: Previous log deleted before each new run

## Troubleshooting

### PermissionError on /dev/shm (NAS/Linux Systems)
**Error**: `PermissionError: [Errno 13] Permission denied: '/dev/shm/...'`

**Solution**: The application is configured to run in production mode (debug=False) to avoid this issue. This error should not occur with the current version. If it does:

1. Ensure debug mode is disabled in `countdown_web.py`
2. Run the app with explicit Python path:
   ```bash
   /usr/local/AppCentral/python3 countdown_web.py
   ```

### Port Already in Use
If port 5000 is already in use, modify `countdown_web.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5001)  # Use 5001 instead
```

### LOG File Shows "No log file yet"
- The countdown process may not have started yet
- Check that countdown_linux.py exists in the same directory
- Verify LINE_CHANNEL_ACCESS_TOKEN is set correctly
- Check file permissions in the directory

### Recipients Not Found
Ensure you're selecting from these exact names:
- Evan
- Cheryl
- Group Chat 1

(These are defined in countdown_linux.py's LINE_RECIPIENTS dictionary)

### Cannot Access Web UI from Another Machine
The application now binds to all interfaces (0.0.0.0) by default. Access from another machine using:
```
http://<nas-ip-address>:5000
```

For example:
```
http://192.168.1.100:5000
```

## Environment Variables

```bash
# Required
export LINE_CHANNEL_ACCESS_TOKEN="your_line_channel_access_token"

# Optional (for production deployment)
export FLASK_ENV=production
export FLASK_DEBUG=0
```

## Production Deployment

### Standard Linux Server
For production use, consider using:
- **Gunicorn**: `pip install gunicorn && gunicorn -w 4 countdown_web:app`
- **Nginx**: Configure as reverse proxy
- **Process Manager**: Use systemd, supervisord, or similar

### QNAP NAS Deployment

1. **Via SSH on QNAP**:
```bash
ssh admin@<nas-ip>
cd /volume1/aria2  # or your working directory
python3 countdown_web.py
```

2. **Background Execution (persistent)**:
```bash
nohup python3 countdown_web.py > countdown_web.log 2>&1 &
```

3. **Using Screen** (recommended for testing):
```bash
screen -S countdown
python3 countdown_web.py
# Ctrl+A then D to detach
# screen -r countdown to reattach
```

4. **Check Running Process**:
```bash
ps aux | grep countdown_web
```

5. **View Logs**:
```bash
tail -f countdown_web.log
tail -f run_countdown.log
```

## File Structure

```
line_countdown/
├── countdown_web.py           # Flask application
├── countdown_linux.py         # CLI countdown script
├── requirements-web.txt       # Python dependencies
├── run_countdown.log          # Execution log (auto-generated)
└── templates/
    └── index.html             # Web UI
```
