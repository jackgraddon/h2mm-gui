# H2MM-CLI Bundling Documentation

## Overview

This repository has been configured to bundle the h2mm-cli binary within the Flatpak application, eliminating the need for users to install h2mm-cli separately.

## Changes Made

### 1. Flatpak Manifest Updates

Updated `com.jackgraddon.h2mmgui.json`:
- Added h2mm-cli as a separate module that builds before h2mm-gui
- Added necessary permissions:
  - `--talk-name=org.freedesktop.Flatpak` for potential host system access
  - `--filesystem=home:ro` for accessing user files
- The h2mm-cli binary is installed to `/app/bin/h2mm-cli` within the Flatpak sandbox

### 2. Application Logic Updates

Updated `src/window.py`:
- Enhanced `_get_base_command()` method to check for bundled binary first
- When running in Flatpak (detected via `FLATPAK_ID` environment variable):
  1. First tries to use bundled binary at `/app/bin/h2mm-cli`
  2. Falls back to host-installed version via `flatpak-spawn --host h2mm-cli` if bundled version not found
- Maintains backward compatibility with custom CLI path settings

### 3. Build Configuration

The Flatpak build process now:
1. Downloads and builds h2mm-cli from the official repository
2. Installs it to the standard binary location within the Flatpak
3. Builds the h2mm-gui application
4. Users get a self-contained package with both GUI and CLI

## For Development

### Using Mock CLI

For testing purposes, a mock h2mm-cli binary is provided:
- Located at the project root as `h2mm-cli`
- Simulates all the expected commands (list, install, uninstall, enable, disable)
- Added to `.gitignore` to prevent committing binary files

### Production Setup

For production releases:
1. Update `com.jackgraddon.h2mmgui.production.json` with the correct:
   - Download URL for the latest h2mm-cli release
   - SHA256 hash of the release archive
2. Replace the current local file source with the archive source

## User Experience

With this implementation:
- Users install just the h2mm-gui Flatpak
- h2mm-cli is automatically included and available
- No additional setup required
- The GUI automatically detects and uses the bundled CLI
- Still supports custom CLI installations if users prefer

## Architecture

The application follows the bundled binary approach outlined in the Technical Blueprint:
- Simplest and most reliable approach for end users
- Binary always available in predictable location
- Executes bundled binary using subprocess module
- Maintains professional and secure application design

## Future Enhancements

The current implementation provides a foundation for:
- Automatic updates of the bundled CLI when h2mm-cli releases new versions
- Fallback mechanisms for different execution environments
- Integration with CI/CD pipelines for automated builds