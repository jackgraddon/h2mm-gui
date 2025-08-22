#!/bin/bash
# Development script - run directly from source without building AppImage

cd "$(dirname "$0")"

echo "🔧 Running H2MM GUI from source (development mode)..."
gjs src/main.js
