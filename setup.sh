#!/bin/bash
# Voice Typer Setup Script

echo "Creating Python Virtual Environment..."
python3 -m venv venv

echo "Activating Virtual Environment and installing dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "================================================="
echo "Setup Complete!"
echo "To run Voice Typer, use the following command:"
echo "sudo ./venv/bin/python main.py"
echo "(Note: sudo is required for global hotkeys on Linux)"
echo "================================================="
