project('h2mm-gui', 'c',
        version: '0.1.0',
        meson_version: '>= 0.59.0')

# Check for required dependencies
py_mod = import('python')
py3 = py_mod.find_installation('python3')
py3_dep = py3.dependency()

# Check for PyGObject
py3 = py_mod.find_installation('python3', modules: ['gi'], required: false)
if not py3.found()
    warning('PyGObject not found - application will not run without it')
    warning('Consider using system Python or installing PyGObject dependencies')
endif

# Try to find PyGObject path to hint the user
if py3.found()
    pygi_path_cmd = run_command(py3, '-c', 'import os, sys; print(os.path.join(sys.prefix, "lib", "python" + ".".join(map(str, sys.version_info[:2])), "site-packages"))', check: false)
    if pygi_path_cmd.returncode() == 0
        message('Suggested PyGObject path: ' + pygi_path_cmd.stdout().strip())
    endif
endif

# Create launcher script with additional logic for finding gi
launcher_conf = configuration_data()
launcher_conf.set('BUILD_ROOT', meson.project_build_root())
launcher_conf.set('SOURCE_ROOT', meson.project_source_root())
launcher_conf.set('PROJECT_NAME', meson.project_name())
launcher_conf.set('SYSTEM_PYTHON', '/usr/bin/python3')  # Fall back to system Python if needed

configure_file(
    input: 'build-aux/meson/enhanced-devenv.py.in',
    output: meson.project_name() + '-dev',
    configuration: launcher_conf,
    install: false,
)

# Make the development launcher executable
run_command('chmod', '+x',
  join_paths(meson.project_build_root(), meson.project_name() + '-dev'),
  check: true
)

i18n = import('i18n')
gnome = import('gnome')

subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)
