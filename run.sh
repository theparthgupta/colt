#!/bin/bash

# Website Explorer Quick Start Script

echo " Website Explorer"
echo "==================="
echo ""

# Check if config needs to be updated
echo " Configuration:"
echo "  Base URL: http://localhost:3000"
echo "  Max Pages: 50"
echo "  Max Depth: 5"
echo "  Headless: False"
echo ""

# Check if localhost:3000 is running
echo " Checking if localhost:3000 is accessible..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo " localhost:3000 is running!"
else
    echo " WARNING: localhost:3000 is not accessible"
    echo "   Make sure your web application is running first"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo " Starting exploration..."
echo ""

# Run the explorer
python explorer.py

echo ""
echo " Done! Check the 'output/' directory for results"
echo ""