# h2mm-gui

A native GNOME graphical user interface for the h2mm-cli mod manager. Designed for use on Linux with Steam Proton.

## Features

- **Bundled CLI**: h2mm-cli is automatically included in the Flatpak package
- **Native GNOME Integration**: Built with GTK4 and libadwaita
- **Mod Management**: Install, uninstall, enable, and disable mods
- **User-Friendly Interface**: Clean, intuitive design following GNOME HIG

## Installation

The Flatpak package includes both the GUI application and the h2mm-cli tool, so no additional setup is required.

### From Flathub (when available)
```bash
flatpak install flathub com.jackgraddon.h2mmgui
```

### Manual Build
```bash
flatpak-builder build com.jackgraddon.h2mmgui.json --install --force-clean
```

## h2mm-cli Bundling

This application bundles h2mm-cli automatically:
- No need to install h2mm-cli separately
- Always uses compatible version
- Fallback to host-installed version if needed
- See [BUNDLING.md](BUNDLING.md) for technical details

## Development

See the [Technical Blueprint](Technical%20Blueprint%20for%20h2mm-gui.md) for detailed architectural information.
