#!/bin/bash

# Simple test script to run countdown_web.py directly and see errors

echo "Testing countdown_web.py startup..."
echo "======================================"
echo ""

# Check if countdown_web.py exists
if [ ! -f "countdown_web.py" ]; then
    echo "ERROR: countdown_web.py not found in current directory"
    exit 1
fi

# Try to run Python and see what happens
echo "Python version:"
python3 --version
echo ""

echo "Checking Flask installation..."
python3 -c "import flask; print('Flask version:', flask.__version__)" || {
    echo "ERROR: Flask not installed"
    echo "Run: pip3 install -r requirements-web.txt"
    exit 1
}
echo ""

echo "Attempting to start countdown_web.py..."
echo "======================================"
python3 countdown_web.py
