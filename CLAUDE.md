# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WhatsApp countdown timer application with two implementations:
- **countdown.html**: Web-based countdown timer using vanilla JavaScript
- **countdown.py**: Desktop application using PyQt6 with WhatsApp Web integration via Selenium

The desktop version sends scheduled notifications to WhatsApp contacts at specific intervals: 10 minutes before target time, at target time, and every 15 minutes for 2 hours after.

## Architecture

### Desktop Application (countdown.py)
- **UI Framework**: PyQt6 widgets for cross-platform GUI
- **Core Components**:
  - `CountdownWindow`: Main application window managing UI state, timer, and notification scheduling
  - Timezone selection dropdown with 12 preset timezones (Asia/Pacific/Europe/Americas)
  - Date/time picker using QComboBox dropdowns
  - Phone number selection via radio buttons (currently hardcoded to two numbers)
  - QTimer for 100ms update interval driving countdown display and notification logic

- **Notification System**:
  - Starts at target time, then repeats every 10 minutes for a total of 15 notifications (2 hours 20 minutes duration)
  - Selenium WebDriver automates WhatsApp Web message sending in separate daemon threads
  - Chrome user data directory persisted locally in `whatsapp_data/` for session management
  - Message URL encoding via `urllib.parse.quote()` for WhatsApp Web `send?phone=` endpoint
  - Each message includes notification count (e.g., "第 1/15 次", "第 5/15 次")

- **Threading**:
  - Daemon threads execute WhatsApp sends to prevent UI blocking
  - `send_whatsapp_initial_thread()` and `send_whatsapp_thread()` handle driver lifecycle
  - Multiple element location strategies in fallback chain (XPATH, CSS selector, button data-testid)

### Web Application (countdown.html)
- Simple client-side countdown to user-selected datetime-local input
- Displays in format: `DD天 HH:MM:SS` (days + time)
- No backend/notification features; local browser only

## Running the Desktop Application

```bash
# Install dependencies (Python 3.8+)
pip install PyQt6 selenium

# Run the application
python countdown.py
```

The application requires:
- Chrome/Chromium browser installed and accessible to Selenium
- Active WhatsApp Web session in the `whatsapp_data/` profile (user must scan QR code on first run)

## Key Files and State

- **countdown.py**: Main application; 426 lines
- **countdown.html**: Web fallback; 107 lines
- **whatsapp_data/**: Chrome user profile directory (created at runtime; contains session/cookies)
- **whatsapp_profile/**: Legacy browser profile directory (not actively used)

## Technical Notes

- Timezone conversion uses `zoneinfo.ZoneInfo` (Python 3.9+) for IANA timezone support
- Notification times calculated from `datetime.timestamp() * 1000` (milliseconds) for cross-timezone accuracy
- Countdown display updates every 100ms; notifications trigger at millisecond granularity
- WhatsApp Web automation relies on element selectors that may break if WhatsApp Web UI changes
  - Fallback chain includes XPATH, CSS selector, and button data-testid matching
  - 5-second and 10-second waits between driver operations to allow page rendering
- Message text is URL-encoded and passed via WhatsApp Web's `send?phone=&text=` deep link
- Notifications fire 15 times: at target time + every 10 minutes thereafter = 2 hours 20 minutes total duration

## Known Limitations

- Hardcoded phone numbers (+886 area code); requires code change to use different contacts
- Relies on volatile WhatsApp Web selectors; updates to WhatsApp UI may require selector adjustments
- No error recovery; failed Selenium operations silently continue without retry
- No persistence; countdown state is lost if application closes
