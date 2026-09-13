#!/bin/bash

# Countdown Web App Startup Script for Linux/NAS
# This script starts the countdown web application in the background

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="countdown_web"
PID_FILE="${APP_NAME}.pid"
LOG_FILE="${APP_NAME}.log"
PORT=${COUNTDOWN_PORT:-5001}  # Changed default from 5000 to 5001 to avoid conflicts

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to print colored output
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

# Check if already running (BusyBox compatible)
check_running() {
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        # Use kill -0 to check if process exists (works with BusyBox)
        if kill -0 "$OLD_PID" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Start the application
start_app() {
    log "Starting ${APP_NAME} on port $PORT..."

    # Check if port is already in use
    if netstat -tlnp 2>/dev/null | grep -q ":$PORT " || ss -tlnp 2>/dev/null | grep -q ":$PORT "; then
        error "Port $PORT is already in use. Try: COUNTDOWN_PORT=5002 ./start_web.sh start"
        return 1
    fi

    # Check dependencies
    if ! python3 -c "import flask" 2>/dev/null; then
        error "Flask not installed. Run: pip3 install -r requirements-web.txt"
        return 1
    fi

    # Try Gunicorn first (production), fall back to Flask if not available
    if python3 -c "import gunicorn" 2>/dev/null; then
        log "Using Gunicorn..."
        nohup gunicorn --bind 0.0.0.0:"$PORT" --workers 2 --timeout 30 --access-logfile "$LOG_FILE" "${APP_NAME}:app" >> "$LOG_FILE" 2>&1 &
    else
        log "Using Flask development server..."
        nohup env COUNTDOWN_PORT="$PORT" python3 "${APP_NAME}.py" >> "$LOG_FILE" 2>&1 &
    fi
    local NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"

    # Give it a moment to start
    sleep 2

    # Verify it's running (BusyBox compatible)
    if kill -0 "$NEW_PID" 2>/dev/null; then
        log "Application started successfully (PID: $NEW_PID)"
        log "Access the web interface at: ${BLUE}http://localhost:${PORT}${NC}"
        log "Log file: ${BLUE}${LOG_FILE}${NC}"
        return 0
    else
        error "Failed to start application. Check ${LOG_FILE} for details."
        cat "$LOG_FILE" | tail -20
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop the application (BusyBox compatible)
stop_app() {
    if ! check_running; then
        log "Application is not running"
        return 0
    fi

    local PID=$(cat "$PID_FILE")
    log "Stopping ${APP_NAME} (PID: $PID)..."

    if kill "$PID" 2>/dev/null; then
        # Wait for process to terminate
        local count=0
        while [ $count -lt 10 ]; do
            if ! kill -0 "$PID" 2>/dev/null; then
                log "Application stopped successfully"
                rm -f "$PID_FILE"
                return 0
            fi
            sleep 1
            count=$((count + 1))
        done

        # Force kill if still running
        if kill -0 "$PID" 2>/dev/null; then
            log "Force killing process..."
            kill -9 "$PID" 2>/dev/null || true
            rm -f "$PID_FILE"
        fi
    else
        error "Failed to stop application"
        return 1
    fi

    return 0
}

# Status check
status_app() {
    if check_running; then
        local PID=$(cat "$PID_FILE")
        log "${APP_NAME} is running (PID: $PID)"
        return 0
    else
        log "${APP_NAME} is not running"
        return 1
    fi
}

# Restart application
restart_app() {
    log "Restarting ${APP_NAME}..."
    stop_app
    sleep 1
    start_app
}

# Show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        log "Showing last 50 lines of ${LOG_FILE}:"
        tail -50 "$LOG_FILE"
    else
        log "No log file found yet"
    fi
}

# Main command handler
case "${1:-start}" in
    start)
        if check_running; then
            error "Application is already running. Use 'restart' to restart."
            exit 1
        fi
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        status_app
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Examples:"
        echo "  $0 start    - Start the web application"
        echo "  $0 stop     - Stop the web application"
        echo "  $0 restart  - Restart the web application"
        echo "  $0 status   - Check application status"
        echo "  $0 logs     - View application logs"
        exit 1
        ;;
esac

exit $?
