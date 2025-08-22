# window.py
#
# Copyright 2025 Jack Graddon
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import os
import pty
import re
from gi.repository import Adw, Gtk, GLib, Gio

@Gtk.Template(resource_path='/com/jackgraddon/h2mmgui/window.ui')
class H2mmGuiWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'H2mmGuiWindow'

    toast_overlay = Gtk.Template.Child()
    install_mod_row = Gtk.Template.Child()
    installed_mods_listbox = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings.new('com.jackgraddon.h2mmgui')
        self._populate_mods_list()
        self.install_mod_row.connect('activated', self._on_install_mod_activated)

    def _get_base_command(self):
        """
        Constructs the base command for h2mm-cli based on user preferences.
        """
        source = self.settings.get_string('cli-source')

        if source == 'custom':
            custom_path = self.settings.get_string('custom-cli-path')
            if not custom_path:
                # This should not happen if OOBE is done correctly, but as a fallback:
                self.toast_overlay.add_toast(Adw.Toast.new("h2mm-cli path not configured!"))
                return None

            if 'FLATPAK_ID' in os.environ:
                return ['flatpak-spawn', '--host', custom_path]
            else:
                return [custom_path]

        # Default to 'bundled'. Check for bundled binary first, then fall back to PATH.
        # In Flatpak, the bundled binary should be in /app/bin/h2mm-cli
        if 'FLATPAK_ID' in os.environ:
            bundled_path = '/app/bin/h2mm-cli'
            if os.path.exists(bundled_path):
                return [bundled_path]
            else:
                # If bundled binary not found, try to use host-installed version
                self.toast_overlay.add_toast(Adw.Toast.new("Bundled h2mm-cli not found, trying host version..."))
                return ['flatpak-spawn', '--host', 'h2mm-cli']
        else:
            # Not in Flatpak, assume it's in the PATH
            return ['h2mm-cli']

    def _on_install_mod_activated(self, *args):
        """Handle the 'Install Mod' action row activation."""
        dialog = Gtk.FileChooserDialog(
            title="Select a Mod Archive to Install",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.ACCEPT,
        )

        filter_zip = Gtk.FileFilter()
        filter_zip.set_name("ZIP archives")
        filter_zip.add_mime_type("application/zip")
        dialog.add_filter(filter_zip)
        filter_rar = Gtk.FileFilter()
        filter_rar.set_name("RAR archives")
        filter_rar.add_mime_type("application/vnd.rar")
        dialog.add_filter(filter_rar)
        filter_7z = Gtk.FileFilter()
        filter_7z.set_name("7z archives")
        filter_7z.add_mime_type("application/x-7z-compressed")
        dialog.add_filter(filter_7z)
        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        dialog.connect("response", self._on_install_dialog_response)
        dialog.present()

    def _on_install_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            try:
                base_command = self._get_base_command()
                if not base_command: return

                mod_path = dialog.get_file().get_path()
                command = base_command + ['install', mod_path]

                result = subprocess.run(
                    command, check=True, capture_output=True, text=True
                )

                toast = Adw.Toast.new(f"Mod installed successfully!")
                self.toast_overlay.add_toast(toast)
                self._populate_mods_list()

            except subprocess.CalledProcessError as e:
                toast = Adw.Toast.new(f"Error installing mod: {e.stderr.strip()}")
                self.toast_overlay.add_toast(toast)
            except Exception as e:
                toast = Adw.Toast.new(f"An unexpected error occurred: {e}")
                self.toast_overlay.add_toast(toast)

        dialog.destroy()

    def _on_uninstall_button_clicked(self, button, mod_name):
        """Handle the click of a mod's uninstall button."""
        try:
            base_command = self._get_base_command()
            if not base_command: return

            command = base_command + ['uninstall', mod_name]
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.toast_overlay.add_toast(Adw.Toast.new(f"Uninstalled '{mod_name}'"))
            self._populate_mods_list()
        except subprocess.CalledProcessError as e:
            self.toast_overlay.add_toast(Adw.Toast.new(f"Error: {e.stderr.strip()}"))
        except Exception as e:
            self.toast_overlay.add_toast(Adw.Toast.new(f"An unexpected error occurred: {e}"))

    def _on_disable_toggled(self, switch, gparam, mod_name):
        """Handle the toggling of a mod's enable/disable switch."""
        is_active = switch.get_active()
        action = 'enable' if is_active else 'disable'
        try:
            base_command = self._get_base_command()
            if not base_command: return

            command = base_command + [action, mod_name]
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.toast_overlay.add_toast(Adw.Toast.new(f"'{mod_name}' has been {action}d."))
        except subprocess.CalledProcessError as e:
            self.toast_overlay.add_toast(Adw.Toast.new(f"Error: {e.stderr.strip()}"))
            switch.set_active(not is_active)
        except Exception as e:
            self.toast_overlay.add_toast(Adw.Toast.new(f"An unexpected error occurred: {e}"))
            switch.set_active(not is_active)

    def _populate_mods_list(self):
        """
        Calls `h2mm-cli list` and populates the listbox with the installed mods.
        """
        while (child := self.installed_mods_listbox.get_row_at_index(0)) is not None:
            self.installed_mods_listbox.remove(child)

        try:
            base_command = self._get_base_command()
            if not base_command:
                # Error is already shown in a toast by _get_base_command
                return

            result = subprocess.run(
                base_command + ['list'],
                capture_output=True,
                text=True,
                check=True
            )

            mods = result.stdout.strip().split('\n')

            if not mods or (len(mods) == 1 and not mods[0]):
                label = Gtk.Label(label="No mods installed.")
                self.installed_mods_listbox.append(label)
                return

            for mod_info in mods:
                if not mod_info:
                    continue

                match = re.match(r'^(.*) \((enabled|disabled)\)$', mod_info)
                if match:
                    mod_name, status = match.groups()
                    is_enabled = (status == 'enabled')
                else:
                    mod_name = mod_info
                    is_enabled = False

                row = Adw.ActionRow(title=mod_name)

                uninstall_button = Gtk.Button(icon_name="user-trash-symbolic")
                uninstall_button.add_css_class('destructive-action')
                uninstall_button.set_valign(Gtk.Align.CENTER)
                uninstall_button.connect('clicked', self._on_uninstall_button_clicked, mod_name)

                toggle_switch = Gtk.Switch(active=is_enabled)
                toggle_switch.set_valign(Gtk.Align.CENTER)
                toggle_switch.connect('notify::active', self._on_disable_toggled, mod_name)

                row.add_suffix(uninstall_button)
                row.add_suffix(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
                row.add_suffix(toggle_switch)

                self.installed_mods_listbox.append(row)

        except FileNotFoundError:
            label = Gtk.Label(label="Error: h2mm-cli not found.\nPlease ensure it is installed and in your PATH.")
            self.installed_mods_listbox.append(label)
        except subprocess.CalledProcessError as e:
            label = Gtk.Label(label=f"Error running h2mm-cli:\n{e.stderr}")
            self.installed_mods_listbox.append(label)
