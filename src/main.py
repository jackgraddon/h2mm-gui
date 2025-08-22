import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio
import os

# Register the GResource file if we're in development mode
resource_dir = os.path.join(os.path.dirname(__file__), '..', 'builddir', 'src')
resource_path = os.path.join(resource_dir, 'h2mm-gui.gresource')
if os.path.exists(resource_path):
    resource = Gio.Resource.load(resource_path)
    Gio.resources_register(resource)

try:
    from .window import H2mmGuiWindow
    from .oobe import H2mmOobeWindow
except ImportError:
    # For when running as a script
    from window import H2mmGuiWindow
    from oobe import H2mmOobeWindow

class H2mmGuiApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self, **kwargs):
        super().__init__(application_id='com.jackgraddon.h2mmgui', **kwargs)
        self.settings = Gio.Settings.new('com.jackgraddon.h2mmgui')
        self.main_window = None

    def do_activate(self):
        window = self.props.active_window
        if not window:
            # Check if OOBE should be shown
            # For development, always show OOBE if FORCE_OOBE env var is set
            force_oobe = os.environ.get('FORCE_OOBE', '').lower() in ('1', 'true', 'yes')
            oobe_complete = self.settings.get_boolean('oobe-complete')
            
            if force_oobe or not oobe_complete:
                # Show OOBE window
                oobe_window = H2mmOobeWindow(application=self)
                oobe_window.connect('oobe-finished', self._on_oobe_finished)
                oobe_window.present()
            else:
                # Show main window
                self._show_main_window()
        else:
            window.present()

    def _on_oobe_finished(self, oobe_window):
        """Called when OOBE is finished."""
        oobe_window.destroy()
        self._show_main_window()

    def _show_main_window(self):
        """Show the main application window."""
        if not self.main_window:
            self.main_window = H2mmGuiWindow(application=self)
        self.main_window.present()

def main(version=None):
    """The application's entry point."""
    app = H2mmGuiApplication()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())
