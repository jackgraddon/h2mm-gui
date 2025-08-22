#!/bin/bash
# Build and launch script for H2MM GUI

cd "$(dirname "$0")"

echo "🚀 Building and launching H2MM GUI..."

# Run the build script
./build.sh

# Check if build was successful and launch
if [ -f "h2mm-gui-x86_64.AppImage" ]; then
    echo "🎯 Launching h2mm-gui-x86_64.AppImage..."
    ./h2mm-gui-x86_64.AppImage
else
    echo "❌ AppImage not found, falling back to running from source..."
    gjs src/main.js
fi
