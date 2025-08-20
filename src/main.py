# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gio, Adw  # noqa: E402
from .window import H2mmGuiWindow  # noqa: E402
from .oobe import H2mmOobeWindow  # noqa: E402


class H2mmGuiApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='com.jackgraddon.h2mmgui',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         resource_base_path='/com/jackgraddon/h2mmgui')
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.win = None
        self.settings = Gio.Settings.new('com.jackgraddon.h2mmgui')

    def do_activate(self):
        """Called when the application is activated."""
        # Show OOBE if it hasn't been completed
        if not self.settings.get_boolean('oobe-complete'):
            oobe = H2mmOobeWindow()
            oobe.connect('oobe-finished', self._show_main_window)
            oobe.present()
        else:
            self._show_main_window()

    def _show_main_window(self, *args):
        """
        Creates and presents the main application window.
        This is called after the OOBE is finished or on normal startup.
        """
        self.win = self.props.active_window
        if not self.win:
            self.win = H2mmGuiWindow(application=self)
        self.win.present()

    def on_about_action(self, action, param):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(
            application_name='h2mm-gui',
            application_icon='com.jackgraddon.h2mmgui',
            developer_name='Jack Graddon',
            version='0.1.0',
            developers=['Jack Graddon'],
            copyright='© 2025 Jack Graddon',
        )
        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        # about.set_translator_credits(_('translator-credits'))
        about.present(self.props.active_window)

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = H2mmGuiApplication()
    return app.run(sys.argv)
