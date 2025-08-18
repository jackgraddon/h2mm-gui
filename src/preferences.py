# preferences.py
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

from gi.repository import Adw, Gtk, Gio

@Gtk.Template(resource_path='/com/jackgraddon/h2mmgui/gtk/preferences.ui')
class H2mmPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'H2mmPreferencesWindow'

    cli_source_row = Gtk.Template.Child()
    custom_cli_path_row = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings.new('com.jackgraddon.h2mmgui')

        # Bind GSettings
        self.settings.bind('cli-source', self.cli_source_row, 'selected', Gio.SettingsBindFlags.DEFAULT)

        # Custom binding for path row subtitle
        self.settings.bind('custom-cli-path', self.custom_cli_path_row, 'subtitle', Gio.SettingsBindFlags.DEFAULT)

        # Connect signals
        self.cli_source_row.connect('notify::selected', self._on_cli_source_changed)
        self.custom_cli_path_row.connect('activated', self._on_select_cli_path_clicked)

        # Initial state
        self._on_cli_source_changed()

    def _on_cli_source_changed(self, *args):
        """Show/hide the custom path row based on the selected source."""
        is_custom = self.cli_source_row.get_selected() == 1
        self.custom_cli_path_row.set_sensitive(is_custom)

    def _on_select_cli_path_clicked(self, *args):
        """Handle the 'Select File' action row activation."""
        dialog = Gtk.FileChooserDialog(
            title="Select h2mm-cli Executable",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.OK,
        )
        dialog.connect("response", self._on_file_chooser_response)
        dialog.present()

    def _on_file_chooser_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_file().get_path()
            self.settings.set_string('custom-cli-path', file_path)
        dialog.destroy()
