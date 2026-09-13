#!/usr/bin/env python3
import subprocess
import os
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Ensure Flask finds templates directory
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

# Log file path
LOG_FILE = "run_countdown.log"

# Available options
TIMEZONES = [
    # North America
    'EST', 'EDT', 'CST', 'CDT', 'MST', 'MDT', 'PST', 'PDT',
    # Europe
    'GMT', 'BST', 'CET', 'CEST', 'WET', 'WEST', 'EET', 'EEST',
    # Asia-Pacific
    'JST', 'KST', 'SGT', 'HKT', 'IST', 'PKT', 'BDT', 'THA', 'MYT', 'PHT',
    'AEST', 'AEDT', 'AWST', 'ACST', 'NZST', 'NZDT',
    # UTC variants
    'UTC', 'UTC+0', 'UTC+1', 'UTC+2', 'UTC+3', 'UTC+4', 'UTC+5', 'UTC+6',
    'UTC+7', 'UTC+8', 'UTC+9', 'UTC+10', 'UTC+11', 'UTC+12',
    'UTC-1', 'UTC-2', 'UTC-3', 'UTC-4', 'UTC-5', 'UTC-6',
    'UTC-7', 'UTC-8', 'UTC-9', 'UTC-10', 'UTC-11', 'UTC-12',
    # IANA timezones
    'Asia/Taipei', 'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Hong_Kong',
    'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
    'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Australia/Sydney'
]

USERS = ['Evan', 'Cheryl', 'Group Chat 1']

def run_countdown_command(timezone, datetime_str, message, users):
    """Run the countdown command in a background thread"""
    try:
        # Delete previous log file
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)

        # Build user arguments
        user_args = ' '.join([f'-u "{user}"' for user in users])

        # Get script directory and use relative path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        countdown_script = os.path.join(script_dir, 'countdown_linux.py')

        # Build command using sys.executable for portability
        import sys
        cmd = (f'{sys.executable} -u {countdown_script} '
               f'-tz "{timezone}" -dt "{datetime_str}" '
               f'-m "{message}" {user_args} >> {LOG_FILE} 2>&1 &')

        # Execute command
        subprocess.Popen(cmd, shell=True)
        return True
    except Exception as e:
        print(f"Error running countdown: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html', timezones=TIMEZONES, users=USERS)

@app.route('/api/run', methods=['POST'])
def run_countdown():
    try:
        data = request.json
        timezone = data.get('timezone', '').strip()
        datetime_str = data.get('datetime', '').strip()
        message = data.get('message', 'countdown').strip()
        users = data.get('users', [])

        # Validate inputs
        if not timezone:
            return jsonify({'success': False, 'error': 'Timezone is required'}), 400
        if not datetime_str:
            return jsonify({'success': False, 'error': 'DateTime is required'}), 400
        if not users or len(users) == 0:
            return jsonify({'success': False, 'error': 'At least one user is required'}), 400

        # Run in background thread to avoid blocking
        thread = threading.Thread(
            target=run_countdown_command,
            args=(timezone, datetime_str, message, users)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'message': 'Countdown started in background',
            'log_file': LOG_FILE
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/log', methods=['GET'])
def get_log():
    """Get the current log file contents (last 100 lines only for speed)"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            # Only return last 100 lines to reduce payload
            content = ''.join(lines[-100:]) if lines else 'No log data yet'
            return jsonify({'success': True, 'content': content})
        else:
            return jsonify({'success': True, 'content': 'No log file yet'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Fallback for direct execution (use Gunicorn in production)
    port = int(os.getenv('COUNTDOWN_PORT', '5000'))
    # For development only - production uses Gunicorn
    try:
        app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
    except Exception as e:
        print(f"Error: {e}")
        print("Note: For production NAS deployment, use Gunicorn:"
              "\n  gunicorn --bind 0.0.0.0:5000 --workers 2 countdown_web:app")
