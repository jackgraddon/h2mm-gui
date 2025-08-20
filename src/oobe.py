# oobe.py
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

from gi.repository import Adw, Gtk, Gio, GObject


@Gtk.Template(resource_path='/com/jackgraddon/h2mmgui/gtk/oobe.ui')
class H2mmOobeWindow(Adw.Window):
    __gtype_name__ = 'H2mmOobeWindow'

    # Define a custom signal
    __gsignals__ = {
        'oobe-finished': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    bundled_check = Gtk.Template.Child()
    custom_check = Gtk.Template.Child()
    custom_cli_path_row = Gtk.Template.Child()
    finish_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings.new('com.jackgraddon.h2mmgui')

        # Connect signals
        self.bundled_check.connect('toggled', self._on_source_changed)
        self.custom_cli_path_row.connect(
            'activated', self._on_select_cli_path_clicked)
        self.finish_button.connect('clicked', self._on_finish_clicked)

    def _on_source_changed(self, *args):
        """Enable/disable the custom path row based on the selection."""
        is_custom = self.custom_check.get_active()
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
            "_Open", Gtk.ResponseType.ACCEPT,
        )
        dialog.connect("response", self._on_file_chooser_response)
        dialog.present()

    def _on_file_chooser_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_file().get_path()
            self.custom_cli_path_row.set_subtitle(file_path)
        dialog.destroy()

    def _on_finish_clicked(self, *args):
        """Save settings and close the OOBE window."""
        # Save settings
        if self.custom_check.get_active():
            self.settings.set_string('cli-source', 'custom')
            subtitle = self.custom_cli_path_row.get_subtitle()
            self.settings.set_string('custom-cli-path', subtitle)
        else:
            self.settings.set_string('cli-source', 'bundled')
            self.settings.set_string('custom-cli-path', '')

        # Mark OOBE as complete
        self.settings.set_boolean('oobe-complete', True)

        # Emit the signal and close the window
        self.emit('oobe-finished')
        self.close()
