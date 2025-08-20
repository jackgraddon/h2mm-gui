desktop_file = i18n.merge_file(
        input: 'com.jackgraddon.h2mmgui.desktop.in',
       output: 'com.jackgraddon.h2mmgui.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'applications'
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
        input: 'com.jackgraddon.h2mmgui.metainfo.xml.in',
       output: 'com.jackgraddon.h2mmgui.metainfo.xml',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

appstreamcli = find_program('appstreamcli', required: false, disabler: true)
test('Validate appstream file', appstreamcli,
     args: ['validate', '--no-net', '--explain', appstream_file])

gschemas_dir = get_option('datadir') / 'glib-2.0' / 'schemas'
install_data('com.jackgraddon.h2mmgui.gschema.xml', install_dir: gschemas_dir)



service_conf = configuration_data()
service_conf.set('bindir', get_option('prefix') / get_option('bindir'))
configure_file(
  input: 'com.jackgraddon.h2mmgui.service.in',
  output: 'com.jackgraddon.h2mmgui.service',
  configuration: service_conf,
  install_dir: get_option('datadir') / 'dbus-1' / 'services'
)

subdir('icons')
