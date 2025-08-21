pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'h2mm_gui'

gnome.compile_resources('h2mm-gui',
  'h2mm-gui.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir
)

python_module = import('python')
py_install = python_module.find_installation('python3')

conf = configuration_data()
conf.set('PYTHON', py_install.full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'h2mm-gui.in',
  output: 'h2mm-gui',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

install_data(
  [
    '__init__.py',
    'main.py',
    'window.py',
    'oobe.py',
  ],
  install_dir: moduledir
)
