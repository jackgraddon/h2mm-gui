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
from gi.repository import Adw, Gtk, GLib, Gio

@Gtk.Template(resource_path='/com/jackgraddon/h2mmgui/window.ui')
class H2mmGuiWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'H2mmGuiWindow'

    stack = Gtk.Template.Child()
    installed_mods_listbox = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    install_mod_name_row = Gtk.Template.Child()
    install_file_row = Gtk.Template.Child()
    install_button = Gtk.Template.Child()
    uninstall_stack = Gtk.Template.Child()
    uninstall_mods_listbox = Gtk.Template.Child()
    uninstall_button = Gtk.Template.Child()
    uninstall_output_view = Gtk.Template.Child()
    update_button = Gtk.Template.Child()
    update_output_view = Gtk.Template.Child()

    def _get_base_command(self):
        """
        Constructs the base command for h2mm-cli based on user preferences.
        """
        source = self.settings.get_string('cli-source')

        if source == 'custom':
            custom_path = self.settings.get_string('custom-cli-path')
            if not custom_path:
                # Fallback or error
                return ['h2mm-cli-not-configured']

            # As per the blueprint, use flatpak-spawn if we are in a Flatpak
            # and want to use a command on the host.
            if 'FLATPAK_ID' in os.environ:
                return ['flatpak-spawn', '--host', custom_path]
            else:
                return [custom_path]

        # Default to 'bundled'. The blueprint suggests this would be in a
        # predictable location inside the Flatpak, e.g. /app/bin/.
        # If not in a Flatpak, we can just assume it's in the PATH.
        return ['h2mm-cli']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings.new('com.jackgraddon.h2mmgui')
        self._install_file = None
        self._populate_mods_list()

        # Connect signals for the install page
        self.install_mod_name_row.connect('notify::text', self._validate_install_inputs)
        self.install_file_row.connect('activated', self._on_select_file_clicked)
        self.install_button.connect('clicked', self._on_install_clicked)

        # Connect signals for the uninstall page
        self.uninstall_mods_listbox.connect('row-selected', self._on_uninstall_row_selected)
        self.uninstall_button.connect('clicked', self._on_uninstall_clicked)

        # Connect signals for the update page
        self.update_button.connect('clicked', self._on_update_clicked)

    def _on_uninstall_row_selected(self, listbox, row):
        """Enable the uninstall button only if a mod is selected."""
        self.uninstall_button.set_sensitive(row is not None)

    def _on_uninstall_clicked(self, button):
        """Handle the 'Uninstall' button click."""
        selected_row = self.uninstall_mods_listbox.get_selected_row()
        if not selected_row:
            return

        mod_name = selected_row.get_child().get_title()
        command = self._get_base_command() + ['uninstall', mod_name]

        buffer = self.uninstall_output_view.get_buffer()
        buffer.set_text(f"Attempting to uninstall '{mod_name}'...\n\n")
        self.uninstall_stack.set_visible_child_name('progress')

        self._run_command_with_pty(command, self.uninstall_output_view, self._on_uninstall_done)

    def _on_uninstall_done(self, success):
        """Called when the uninstall process is complete."""
        if success:
            toast = Adw.Toast.new("Mod uninstalled successfully.")
            self._populate_mods_list()
        else:
            toast = Adw.Toast.new("Failed to uninstall mod. See log for details.")

        self.toast_overlay.add_toast(toast)
        self.uninstall_stack.set_visible_child_name('selection')
        self.uninstall_button.set_sensitive(False)

    def _on_update_clicked(self, button):
        """Handle the 'Check for Updates' button click."""
        command = self._get_base_command() + ['update']

        buffer = self.update_output_view.get_buffer()
        buffer.set_text("Checking for updates...\n\n")
        self.update_output_view.set_visible(True)
        self.update_button.set_sensitive(False)

        self._run_command_with_pty(command, self.update_output_view, self._on_update_done)

    def _on_update_done(self, success):
        """Called when the update process is complete."""
        if success:
            toast = Adw.Toast.new("Update check finished.")
            self._populate_mods_list()
        else:
            toast = Adw.Toast.new("Update check failed. See log for details.")

        self.toast_overlay.add_toast(toast)
        self.update_button.set_sensitive(True)

    def _run_command_with_pty(self, command, text_view, on_done_callback):
        """
        Runs a command in a pseudo-terminal to support interactive prompts.
        Streams the output to the provided Gtk.TextView.
        Calls the on_done_callback when the process finishes.
        """
        pid, fd = pty.fork()
        if pid == 0:  # Child process
            try:
                os.execvp(command[0], command)
            except FileNotFoundError:
                # This will be written to the PTY's stderr and caught by the parent
                os.write(2, f"Error: Command not found: {command[0]}\n".encode())
                os._exit(1) # Use _exit in child process after fork
        else:  # Parent process
            GLib.io_add_watch(
                fd,
                GLib.IO_IN | GLib.IO_HUP,
                self._on_pty_output,
                pid,
                fd,
                text_view.get_buffer(),
                on_done_callback
            )

    def _on_pty_output(self, source, condition, pid, fd, buffer, on_done_callback):
        if condition & GLib.IO_HUP:
            os.close(fd)
            _, status = os.waitpid(pid, 0)
            GLib.idle_add(on_done_callback, os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0)
            return GLib.SOURCE_REMOVE

        try:
            output = os.read(fd, 1024).decode()
            buffer.insert_at_cursor(output)
        except OSError:
            pass # This can happen if the process closes quickly

        return GLib.SOURCE_CONTINUE


    def _validate_install_inputs(self, *args):
        """Enable the install button only if both inputs are valid."""
        name_valid = self.install_mod_name_row.get_text().strip() != ""
        file_valid = self._install_file is not None
        self.install_button.set_sensitive(name_valid and file_valid)

    def _on_select_file_clicked(self, *args):
        """Handle the 'Select File' action row activation."""
        dialog = Gtk.FileChooserDialog(
            title="Select a Mod Archive",
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
            self._install_file = dialog.get_file()
            self.install_file_row.set_subtitle(self._install_file.get_basename())
            self._validate_install_inputs()
        dialog.destroy()

    def _on_install_clicked(self, *args):
        """Handle the 'Install' button click."""
        mod_name = self.install_mod_name_row.get_text().strip()
        mod_path = self._install_file.get_path()

        command = self._get_base_command() + ['install', mod_path, '--name', mod_name]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            toast = Adw.Toast.new(f"Successfully installed '{mod_name}'")
            self.toast_overlay.add_toast(toast)
            self._populate_mods_list()
            # Reset form
            self.install_mod_name_row.set_text("")
            self._install_file = None
            self.install_file_row.set_subtitle("No file selected")
            self._validate_install_inputs()

        except subprocess.CalledProcessError as e:
            toast = Adw.Toast.new(f"Error installing mod: {e.stderr.strip()}")
            self.toast_overlay.add_toast(toast)
        except FileNotFoundError:
            toast = Adw.Toast.new("Error: h2mm-cli not found.")
            self.toast_overlay.add_toast(toast)
        except Exception as e:
            toast = Adw.Toast.new(f"An unexpected error occurred: {e}")
            self.toast_overlay.add_toast(toast)

    def _populate_mods_list(self):
        """
        Calls `h2mm-cli list` and populates both mod lists.
        """
        # Clear the listboxes before populating
        for listbox in [self.installed_mods_listbox, self.uninstall_mods_listbox]:
            while (child := listbox.get_row_at_index(0)) is not None:
                listbox.remove(child)

        self.uninstall_button.set_sensitive(False)

        try:
            command = self._get_base_command() + ['list']
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )

            mods = result.stdout.strip().split('\n')

            if not mods or (len(mods) == 1 and not mods[0]):
                label1 = Gtk.Label(label="No mods installed.")
                self.installed_mods_listbox.append(label1)
                label2 = Gtk.Label(label="No mods to uninstall.")
                self.uninstall_mods_listbox.append(label2)
                return

            for mod_name in mods:
                if mod_name:
                    # The list on the "Installed" page is not selectable
                    row1 = Adw.ActionRow(title=mod_name, selectable=False)
                    self.installed_mods_listbox.append(row1)

                    # The list on the "Uninstall" page is selectable
                    row2 = Adw.ActionRow(title=mod_name, activatable=True)
                    self.uninstall_mods_listbox.append(row2)

        except FileNotFoundError:
            label1 = Gtk.Label(label="Error: h2mm-cli not found.\nPlease ensure it is installed and in your PATH.")
            self.installed_mods_listbox.append(label1)
            label2 = Gtk.Label(label="Error: h2mm-cli not found.\nPlease ensure it is installed and in your PATH.")
            self.uninstall_mods_listbox.append(label2)

        except subprocess.CalledProcessError as e:
            label1 = Gtk.Label(label=f"Error running h2mm-cli:\n{e.stderr}")
            self.installed_mods_listbox.append(label1)
            label2 = Gtk.Label(label=f"Error running h2mm-cli:\n{e.stderr}")
            self.uninstall_mods_listbox.append(label2)
