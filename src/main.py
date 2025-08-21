import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw

class H2mmGuiApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self, **kwargs):
        super().__init__(application_id='com.jackgraddon.h2mmgui', **kwargs)

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_default_size(800, 600)
        window.set_title("H2MM GUI")
        window.show()

def main():
    """The application's entry point."""
    app = H2mmGuiApplication()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())
