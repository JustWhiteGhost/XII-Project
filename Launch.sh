#!/bin/bash

# ========================================
# Fog-Shrouded Chronicles - Launcher
# ========================================

clear

echo "======================================"
echo "   FOG-SHROUDED CHRONICLES"
echo "   AI-Powered Virtual D&D"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "Please install Python 3.8 or higher:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Python found:"
python3 --version
echo ""

# Check if setup has been run
if [ ! -f "config.json" ]; then
    echo "First time setup required..."
    echo ""
    echo "Running setup script..."
    echo ""
    python3 setup.py
    echo ""
    echo "Setup complete! Please run this launcher again."
    read -p "Press Enter to exit..."
    exit 0
fi

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import pandas, groq, sentence_transformers, networkx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Some dependencies are missing!"
    echo ""
    read -p "Would you like to run setup now? (y/n) " choice
    
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        echo ""
        echo "Running setup..."
        python3 setup.py
        read -p "Press Enter to exit..."
        exit 0
    else
        echo ""
        echo "Cannot start game without dependencies."
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "Dependencies OK"
echo ""

# Check API key
if grep -q "YOUR_API_KEY_HERE" config.json; then
    echo ""
    echo "========================================"
    echo "WARNING: API Key Not Configured!"
    echo "========================================"
    echo ""
    echo "Please edit config.json and add your Groq API key"
    echo "Get a free key at: https://console.groq.com/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# All checks passed - launch game
echo "Starting game..."
echo ""
echo "======================================"
echo ""

python3 Main.py

echo ""
echo "======================================"
echo "Game closed"
echo "======================================"
echo ""
read -p "Press Enter to exit..."