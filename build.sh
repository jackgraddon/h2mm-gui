#!/bin/bash
# Build script for H2MM GUI AppImage

set -e  # Exit on any error

cd "$(dirname "$0")"

echo "🔧 Building H2MM GUI AppImage..."

# Create AppDir structure if it doesn't exist
mkdir -p AppDir/usr/share/h2mm-gui
mkdir -p AppDir/usr/share/h2mm-gui/ui
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

echo "📁 Copying source files to AppDir..."

# Copy main application files from src/ to AppDir
cp src/main.js AppDir/usr/share/h2mm-gui/
cp src/cliHandler.js AppDir/usr/share/h2mm-gui/
cp src/configManager.js AppDir/usr/share/h2mm-gui/
cp src/style.css AppDir/usr/share/h2mm-gui/

# Copy UI files
cp src/ui/window.ui AppDir/usr/share/h2mm-gui/ui/
cp src/ui/window.cmb AppDir/usr/share/h2mm-gui/ui/

# Copy desktop file and icon
cp h2mm-gui.desktop AppDir/
cp h2mm-gui.desktop AppDir/usr/share/applications/

# Fix import paths in main.js for AppImage (remove 'src.' prefix)
sed -i 's/imports\.src\.cliHandler\.CliHandler/imports.cliHandler.CliHandler/g' AppDir/usr/share/h2mm-gui/main.js
sed -i 's/imports\.src\.configManager\.ConfigManager/imports.configManager.ConfigManager/g' AppDir/usr/share/h2mm-gui/main.js

echo "🔨 Making sure AppRun is executable..."
chmod +x AppDir/AppRun

echo "🔨 Making sure appimagetool is executable..."
chmod +x appimagetool-x86_64.AppImage

echo "📦 Building AppImage..."
./appimagetool-x86_64.AppImage --no-appstream --comp gzip AppDir h2mm-gui-x86_64.AppImage

if [ $? -eq 0 ]; then
    echo "✅ AppImage built successfully as h2mm-gui-x86_64.AppImage"
    chmod +x h2mm-gui-x86_64.AppImage
else
    echo "❌ AppImage build failed!"
    exit 1
fi
