pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'h2mm_gui'
gnome = import('gnome')

gnome.compile_resources('h2mm-gui',
  'h2mm-gui.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'h2mm-gui.in',
  output: 'h2mm-gui',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

h2mm_gui_sources = [
  '__init__.py',
  'main.py',
  'window.py',
]

install_data(h2mm_gui_sources, install_dir: moduledir)
