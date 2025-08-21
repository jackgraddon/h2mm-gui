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

from .window import H2mmGuiWindow

class H2mmGuiApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self, **kwargs):
        super().__init__(application_id='com.jackgraddon.h2mmgui', **kwargs)

    def do_activate(self):
        window = self.props.active_window
        if not window:
            window = H2mmGuiWindow(application=self)
        window.present()

def main():
    """The application's entry point."""
    app = H2mmGuiApplication()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())
