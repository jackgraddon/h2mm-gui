#!/usr/bin/env gjs

imports.gi.versions.Gtk = '4.0';
imports.gi.versions.Adw = '1';

const { GObject, Gtk, Adw, Gio, GLib } = imports.gi;

// Import our custom modules
imports.searchPath.unshift('.');
const CliHandler = imports.src.cliHandler.CliHandler;
const ConfigManager = imports.src.configManager.ConfigManager;

// Main Application Class
const H2mmGuiApplication = GObject.registerClass({
    GTypeName: 'H2mmGuiApplication',
}, class H2mmGuiApplication extends Adw.Application {
    _init() {
        super._init({
            application_id: 'com.jackgraddon.h2mm-gui',
            flags: Gio.ApplicationFlags.DEFAULT_FLAGS,
        });

        this.configManager = new ConfigManager();
        this.cliHandler = new CliHandler();
    }

    vfunc_activate() {
        let window = this.active_window;
        if (!window) {
            window = new H2mmGuiWindow(this);
        }
        window.present();
    }
});

// Main Window Class
const H2mmGuiWindow = GObject.registerClass({
    GTypeName: 'H2mmGuiWindow',
}, class H2mmGuiWindow extends Adw.ApplicationWindow {
    _init(application) {
        super._init({
            application,
            title: 'h2mm-gui',
        });

        this.application = application;
        this.cliHandler = application.cliHandler;
        this.configManager = application.configManager;

        // Set window size from config
        this.set_default_size(
            this.configManager.get('window.width'),
            this.configManager.get('window.height')
        );

        this._buildUIFromFile();
        this._connectSignals();
        this._loadCustomCSS();
        this._checkCliStatus();
    }

    _buildUIFromFile() {
        // Load UI from file
        const builder = new Gtk.Builder();
        try {
            const uiFile = '/home/jack/Projects/h2mm-gui/src/ui/window.ui';
            builder.add_from_file(uiFile);

            // Get the split view directly from the UI file
            const splitView = builder.get_object('split_view');

            // Ensure the split view expands to fill available space
            splitView.set_vexpand(true);
            splitView.set_hexpand(true);

            // Create toast overlay and main window structure
            this.toast_overlay = new Adw.ToastOverlay();
            this.toast_overlay.set_child(splitView);
            this.toast_overlay.set_vexpand(true);

            // Create main header bar (single header for the window)
            const headerBar = new Adw.HeaderBar();
            const menuButton = new Gtk.MenuButton({
                icon_name: 'open-menu-symbolic',
                tooltip_text: 'Main Menu',
            });
            headerBar.pack_end(menuButton);

            // Set up main window layout with proper expansion
            const mainLayout = new Gtk.Box({
                orientation: Gtk.Orientation.VERTICAL,
                vexpand: true,
                hexpand: true,
            });
            mainLayout.append(headerBar);
            mainLayout.append(this.toast_overlay);

            this.set_content(mainLayout);

            // Get references to UI elements
            this.status_row = builder.get_object('status_row');
            this.status_icon = builder.get_object('status_icon');

            // Mod list elements
            this.mod_list = builder.get_object('mod_list');
            this.empty_state_row = builder.get_object('empty_state_row');

            // Installation elements
            this.mod_url_entry = builder.get_object('mod_url_entry');
            this.browse_button = builder.get_object('browse_button');
            this.install_button = builder.get_object('install_button');

            // Action elements
            this.refresh_row = builder.get_object('refresh_row');
            this.update_all_row = builder.get_object('update_all_row');
            this.remove_selected_row = builder.get_object('remove_selected_row');
            this.preferences_row = builder.get_object('preferences_row');
            this.about_row = builder.get_object('about_row');

            // Terminal elements
            this.main_tab_view = builder.get_object('main_tab_view');
            this.terminal_input = builder.get_object('terminal_input');
            this.terminal_send_button = builder.get_object('terminal_send_button');
            this.terminal_clear_button = builder.get_object('terminal_clear_button');
            this.terminal_output = builder.get_object('terminal_output');

            // Initialize terminal
            this._initializeTerminal();

        } catch (error) {
            print(`Error loading UI file: ${error.message}`);
            // Fallback to programmatic UI creation
            this._buildUIFallback();
        }
    }

    _buildUIFallback() {
        // Simplified fallback UI creation using direct AdwNavigationSplitView
        const headerBar = new Adw.HeaderBar();
        const menuButton = new Gtk.MenuButton({
            icon_name: 'open-menu-symbolic',
            tooltip_text: 'Main Menu',
        });
        headerBar.pack_end(menuButton);

        // Create Navigation Split View
        const splitView = new Adw.NavigationSplitView({
            sidebar_width_fraction: 0.32,
            min_sidebar_width: 300,
            max_sidebar_width: 400,
        });

        // Sidebar content without extra headers
        const sidebarScrolled = new Gtk.ScrolledWindow({
            hscrollbar_policy: Gtk.PolicyType.NEVER,
            vscrollbar_policy: Gtk.PolicyType.AUTOMATIC,
        });

        const sidebarContent = new Gtk.Box({
            orientation: Gtk.Orientation.VERTICAL,
            margin_top: 12,
            margin_bottom: 12,
            margin_start: 12,
            margin_end: 12,
            spacing: 18,
        });

        // Install section
        this.mod_url_entry = new Adw.EntryRow({
            title: 'Mod URL or Path',
        });

        const buttonBox = new Gtk.Box({
            orientation: Gtk.Orientation.HORIZONTAL,
            spacing: 8,
            margin_top: 12,
            margin_start: 12,
            margin_end: 12,
            margin_bottom: 6,
        });

        this.browse_button = new Gtk.Button({
            label: 'Browse...',
            hexpand: true,
        });
        this.install_button = new Gtk.Button({
            label: 'Install',
            hexpand: true,
            css_classes: ['suggested-action']
        });

        buttonBox.append(this.browse_button);
        buttonBox.append(this.install_button);

        const installGroup = new Adw.PreferencesGroup({
            title: 'Install New Mod',
        });
        installGroup.add(this.mod_url_entry);
        installGroup.add(buttonBox);

        // Action rows
        this.refresh_row = new Adw.ActionRow({
            title: 'Refresh Mod List',
            subtitle: 'Update the list of installed mods',
            activatable: true,
        });
        const refreshIcon = new Gtk.Image({ icon_name: 'view-refresh-symbolic' });
        this.refresh_row.add_suffix(refreshIcon);

        this.update_all_row = new Adw.ActionRow({
            title: 'Update All Mods',
            subtitle: 'Check for and install mod updates',
            activatable: true,
        });
        const updateIcon = new Gtk.Image({ icon_name: 'software-update-available-symbolic' });
        this.update_all_row.add_suffix(updateIcon);

        this.remove_selected_row = new Adw.ActionRow({
            title: 'Remove Selected Mod',
            subtitle: 'Remove the currently selected mod',
            activatable: true,
            sensitive: false,
        });
        const removeIcon = new Gtk.Image({ icon_name: 'user-trash-symbolic' });
        this.remove_selected_row.add_suffix(removeIcon);

        const actionsGroup = new Adw.PreferencesGroup({
            title: 'Mod Actions',
        });
        actionsGroup.add(this.refresh_row);
        actionsGroup.add(this.update_all_row);
        actionsGroup.add(this.remove_selected_row);

        // Settings section
        this.preferences_row = new Adw.ActionRow({
            title: 'Preferences',
            subtitle: 'Configure application settings',
            activatable: true,
        });
        const prefsIcon = new Gtk.Image({ icon_name: 'preferences-system-symbolic' });
        this.preferences_row.add_suffix(prefsIcon);

        this.about_row = new Adw.ActionRow({
            title: 'About',
            subtitle: 'About H2MM GUI',
            activatable: true,
        });
        const aboutIcon = new Gtk.Image({ icon_name: 'help-about-symbolic' });
        this.about_row.add_suffix(aboutIcon);

        const settingsGroup = new Adw.PreferencesGroup({
            title: 'Settings',
        });
        settingsGroup.add(this.preferences_row);
        settingsGroup.add(this.about_row);

        sidebarContent.append(installGroup);
        sidebarContent.append(actionsGroup);
        sidebarContent.append(settingsGroup);

        sidebarScrolled.set_child(sidebarContent);

        // Create sidebar page
        const sidebarPage = new Adw.NavigationPage({
            title: 'Actions',
        });
        sidebarPage.set_child(sidebarScrolled);

        // Create main content with tab view (including terminal)
        this.main_tab_view = new Adw.TabView({
            vexpand: true,
        });

        // Mods tab
        const modsTabContent = this._createModsTabContent();
        const modsTabPage = this.main_tab_view.append(modsTabContent);
        modsTabPage.set_title('Mods');

        // Terminal tab
        const terminalTabContent = this._createTerminalTabContent();
        const terminalTabPage = this.main_tab_view.append(terminalTabContent);
        terminalTabPage.set_title('Terminal');

        // Create content page
        const contentPage = new Adw.NavigationPage({
            title: 'H2MM Management',
        });
        contentPage.set_child(this.main_tab_view);

        // Set up the split view
        splitView.set_sidebar(sidebarPage);
        splitView.set_content(contentPage);

        this.toast_overlay = new Adw.ToastOverlay();
        this.toast_overlay.set_child(splitView);

        const mainLayout = new Gtk.Box({
            orientation: Gtk.Orientation.VERTICAL,
        });
        mainLayout.append(headerBar);
        mainLayout.append(this.toast_overlay);

        this.set_content(mainLayout);

        // Initialize terminal after UI is created
        this._initializeTerminal();
    }

    _createModsTabContent() {
        const mainContent = new Gtk.Box({
            orientation: Gtk.Orientation.VERTICAL,
            margin_top: 12,
            margin_bottom: 12,
            margin_start: 12,
            margin_end: 12,
            spacing: 18,
        });

        this.status_row = new Adw.ActionRow({
            title: 'Checking h2mm-cli...',
            subtitle: 'Please wait',
        });

        this.status_icon = new Gtk.Image({
            icon_name: 'content-loading-symbolic',
        });
        this.status_row.add_suffix(this.status_icon);

        const statusGroup = new Adw.PreferencesGroup({
            title: 'H2MM CLI Status',
        });
        statusGroup.add(this.status_row);

        this.mod_list = new Gtk.ListBox({
            selection_mode: Gtk.SelectionMode.SINGLE,
            css_classes: ['boxed-list'],
        });

        // Create empty state row
        this.empty_state_row = new Gtk.ListBoxRow({
            selectable: false,
        });

        const emptyStateBox = new Gtk.Box({
            orientation: Gtk.Orientation.VERTICAL,
            spacing: 18,
            margin_top: 60,
            margin_bottom: 60,
            margin_start: 32,
            margin_end: 32,
            halign: Gtk.Align.CENTER,
        });

        const emptyIcon = new Gtk.Image({
            icon_name: 'folder-symbolic',
            pixel_size: 72,
            css_classes: ['dim-label'],
        });

        const emptyTitle = new Gtk.Label({
            label: 'No mods installed',
            halign: Gtk.Align.CENTER,
            css_classes: ['title-1', 'dim-label'],
        });

        const emptySubtitle = new Gtk.Label({
            label: 'Use the sidebar to install your first mod',
            halign: Gtk.Align.CENTER,
            wrap: true,
            justify: Gtk.Justification.CENTER,
            css_classes: ['dim-label'],
        });

        emptyStateBox.append(emptyIcon);
        emptyStateBox.append(emptyTitle);
        emptyStateBox.append(emptySubtitle);
        this.empty_state_row.set_child(emptyStateBox);

        this.mod_list.append(this.empty_state_row);

        const scrolledWindow = new Gtk.ScrolledWindow({
            hscrollbar_policy: Gtk.PolicyType.NEVER,
            vscrollbar_policy: Gtk.PolicyType.AUTOMATIC,
            vexpand: true,
            min_content_height: 400,
        });
        scrolledWindow.set_child(this.mod_list);

        const modListGroup = new Adw.PreferencesGroup({
            title: 'Installed Mods',
            vexpand: true,
        });
        modListGroup.add(scrolledWindow);

        mainContent.append(statusGroup);
        mainContent.append(modListGroup);

        return mainContent;
    }

    _createTerminalTabContent() {
        const terminalContent = new Gtk.Box({
            orientation: Gtk.Orientation.VERTICAL,
            margin_top: 12,
            margin_bottom: 12,
            margin_start: 12,
            margin_end: 12,
            spacing: 12,
        });

        const terminalGroup = new Adw.PreferencesGroup({
            title: 'H2MM CLI Terminal',
            description: 'Direct TTY interface to h2mm commands',
        });

        // Terminal controls
        const terminalControls = new Gtk.Box({
            orientation: Gtk.Orientation.HORIZONTAL,
            spacing: 8,
            margin_bottom: 8,
        });

        this.terminal_input = new Gtk.Entry({
            hexpand: true,
            placeholder_text: 'Enter h2mm command (e.g., list, install, update)...',
        });

        this.terminal_send_button = new Gtk.Button({
            label: 'Send',
            css_classes: ['suggested-action'],
        });

        this.terminal_clear_button = new Gtk.Button({
            label: 'Clear',
        });

        terminalControls.append(this.terminal_input);
        terminalControls.append(this.terminal_send_button);
        terminalControls.append(this.terminal_clear_button);

        // Terminal output
        const terminalOutputScroll = new Gtk.ScrolledWindow({
            hscrollbar_policy: Gtk.PolicyType.AUTOMATIC,
            vscrollbar_policy: Gtk.PolicyType.AUTOMATIC,
            vexpand: true,
            min_content_height: 400,
        });

        this.terminal_output = new Gtk.TextView({
            editable: false,
            cursor_visible: false,
            monospace: true,
            wrap_mode: Gtk.WrapMode.WORD_CHAR,
            margin_start: 12,
            margin_end: 12,
            margin_top: 12,
            margin_bottom: 12,
            css_classes: ['terminal'],
        });

        terminalOutputScroll.set_child(this.terminal_output);

        terminalGroup.add(terminalControls);
        terminalGroup.add(terminalOutputScroll);
        terminalContent.append(terminalGroup);

        return terminalContent;
    }

    _connectSignals() {
        // Connect installation signals
        this.install_button.connect('clicked', () => {
            this._installMod();
        });

        this.browse_button.connect('clicked', () => {
            this._browseForMod();
        });

        // Connect action row signals
        this.refresh_row.connect('activated', () => {
            this._refreshModList();
        });

        this.update_all_row.connect('activated', () => {
            this._updateAllMods();
        });

        this.remove_selected_row.connect('activated', () => {
            this._removeSelectedMod();
        });

        this.preferences_row.connect('activated', () => {
            this._showPreferences();
        });

        this.about_row.connect('activated', () => {
            this._showAbout();
        });

        // Connect mod list selection
        this.mod_list.connect('row-selected', (listbox, row) => {
            // Enable/disable remove button based on selection
            this.remove_selected_row.set_sensitive(row !== null && row !== this.empty_state_row);
        });

        // Connect terminal signals if terminal elements exist
        if (this.terminal_input && this.terminal_send_button && this.terminal_clear_button) {
            this.terminal_send_button.connect('clicked', () => {
                this._sendTerminalCommand();
            });

            this.terminal_clear_button.connect('clicked', () => {
                this._clearTerminal();
            });

            this.terminal_input.connect('activate', () => {
                this._sendTerminalCommand();
            });
        }
    }

    _loadCustomCSS() {
        const cssProvider = new Gtk.CssProvider();
        try {
            const cssFile = Gio.File.new_for_path('/home/jack/Projects/h2mm-gui/src/style.css');
            cssProvider.load_from_file(cssFile);
            Gtk.StyleContext.add_provider_for_display(
                this.get_display(),
                cssProvider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            );
        } catch (error) {
            print(`Error loading CSS: ${error.message}`);
        }
    }

    async _checkCliStatus() {
        const isAvailable = this.cliHandler.checkCliAvailable();

        if (isAvailable) {
            this.status_row.set_title('h2mm-cli found');
            this.status_row.set_subtitle('Ready to use');
            this.status_icon.set_from_icon_name('emblem-ok-symbolic');
            this.status_icon.css_classes = ['success'];
        } else {
            this.status_row.set_title('h2mm-cli not found');
            this.status_row.set_subtitle('Please install h2mm-cli to use this application');
            this.status_icon.set_from_icon_name('dialog-warning-symbolic');
            this.status_icon.css_classes = ['warning'];
        }
    }

    _executeCommand(cmd) {
        this._showToast(`Executing: ${cmd.name}`);

        try {
            this.cliHandler.executeCommand(
                [cmd.command],
                (output) => {
                    print(`Output: ${output}`);
                },
                (error) => {
                    print(`Error: ${error}`);
                    this._showToast(`Error: ${error}`);
                },
                (exitCode) => {
                    if (exitCode === 0) {
                        this._showToast(`${cmd.name} completed successfully`);
                    } else {
                        this._showToast(`${cmd.name} failed with exit code ${exitCode}`);
                    }
                }
            );
        } catch (error) {
            this._showToast(`Failed to execute ${cmd.name}: ${error.message}`);
        }
    }

    _installMod() {
        const modPath = this.mod_url_entry.get_text().trim();
        if (!modPath) {
            this._showToast('Please enter a mod URL or path');
            return;
        }

        this._showToast(`Installing mod: ${modPath}`);

        // Execute h2mm-cli install command
        this.cliHandler.executeCommand(
            ['install', modPath],
            (output) => {
                print(`Install output: ${output}`);
            },
            (error) => {
                // h2mm-cli outputs informational messages to stderr
                // Check if it's actually an error or just informational output
                print(`Install stderr: ${error}`);

                // Don't treat informational messages as errors
                if (error.includes('successfully installed') ||
                    error.includes('installed at') ||
                    error.includes('Mod file')) {
                    // This is informational, not an error
                    return;
                }

                // Only show toast for actual errors
                this._showToast(`Installation failed: ${error}`);
            },
            (exitCode) => {
                if (exitCode === 0) {
                    this._showToast('Mod installed successfully');
                    this.mod_url_entry.set_text('');
                    this._refreshModList();
                } else {
                    this._showToast(`Installation failed with exit code ${exitCode}`);
                }
            }
        );
    }

    _browseForMod() {
        // Create file chooser dialog
        const dialog = new Gtk.FileChooserDialog({
            title: 'Select Mod File',
            transient_for: this,
            action: Gtk.FileChooserAction.OPEN,
        });

        dialog.add_button('Cancel', Gtk.ResponseType.CANCEL);
        dialog.add_button('Open', Gtk.ResponseType.ACCEPT);

        dialog.show();
        dialog.connect('response', (dialog, response) => {
            if (response === Gtk.ResponseType.ACCEPT) {
                const file = dialog.get_file();
                if (file) {
                    this.mod_url_entry.set_text(file.get_path());
                }
            }
            dialog.destroy();
        });
    }

    _refreshModList() {
        this._showToast('Refreshing mod list...');

        // Execute h2mm-cli list command
        this.cliHandler.executeCommand(
            ['list'],
            (output) => {
                this._updateModListDisplay(output);
            },
            (error) => {
                print(`List error: ${error}`);
                this._showToast(`Failed to refresh: ${error}`);
            },
            (exitCode) => {
                if (exitCode === 0) {
                    this._showToast('Mod list refreshed');
                } else {
                    this._showToast('Failed to refresh mod list');
                }
            }
        );
    }

    _updateModListDisplay(modListOutput) {
        // Clear existing mod entries (keep empty state row)
        let child = this.mod_list.get_first_child();
        while (child) {
            const next = child.get_next_sibling();
            if (child !== this.empty_state_row) {
                this.mod_list.remove(child);
            }
            child = next;
        }

        // Parse mod list output and add entries
        if (modListOutput && modListOutput.trim()) {
            const mods = modListOutput.split('\n').filter(line => line.trim());

            if (mods.length > 0) {
                this.empty_state_row.set_visible(false);

                mods.forEach(modName => {
                    const modRow = new Adw.ActionRow({
                        title: modName.trim(),
                        subtitle: 'Installed mod',
                    });

                    const statusIcon = new Gtk.Image({
                        icon_name: 'emblem-ok-symbolic',
                        css_classes: ['success'],
                    });
                    modRow.add_suffix(statusIcon);

                    this.mod_list.append(modRow);
                });
            } else {
                this.empty_state_row.set_visible(true);
            }
        } else {
            this.empty_state_row.set_visible(true);
        }
    }

    _updateAllMods() {
        this._showToast('Updating all mods...');

        this.cliHandler.executeCommand(
            ['update'],
            (output) => {
                print(`Update output: ${output}`);
            },
            (error) => {
                print(`Update error: ${error}`);
                this._showToast(`Update failed: ${error}`);
            },
            (exitCode) => {
                if (exitCode === 0) {
                    this._showToast('All mods updated successfully');
                    this._refreshModList();
                } else {
                    this._showToast(`Update failed with exit code ${exitCode}`);
                }
            }
        );
    }

    _removeSelectedMod() {
        const selectedRow = this.mod_list.get_selected_row();
        if (!selectedRow || selectedRow === this.empty_state_row) {
            this._showToast('No mod selected');
            return;
        }

        const modName = selectedRow.get_title();
        this._showToast(`Removing mod: ${modName}`);

        this.cliHandler.executeCommand(
            ['remove', modName],
            (output) => {
                print(`Remove output: ${output}`);
            },
            (error) => {
                print(`Remove error: ${error}`);
                this._showToast(`Removal failed: ${error}`);
            },
            (exitCode) => {
                if (exitCode === 0) {
                    this._showToast('Mod removed successfully');
                    this._refreshModList();
                } else {
                    this._showToast(`Removal failed with exit code ${exitCode}`);
                }
            }
        );
    }

    _showPreferences() {
        this._showToast('Preferences dialog coming soon...');
    }

    _showAbout() {
        this._showToast('About dialog coming soon...');
    }

    // Terminal functionality methods
    _initializeTerminal() {
        if (!this.terminal_output) return;

        // Get the text buffer and set initial content
        this.terminal_buffer = this.terminal_output.get_buffer();
        this.terminal_buffer.set_text('H2MM CLI Terminal\nType h2mm commands below. Examples: list, help, status\n\n', -1);

        // Scroll to bottom
        this._scrollTerminalToBottom();
    }

    _sendTerminalCommand() {
        if (!this.terminal_input || !this.terminal_buffer) return;

        const command = this.terminal_input.get_text().trim();
        if (!command) return;

        // Clear input
        this.terminal_input.set_text('');

        // Add command to terminal output
        this._appendToTerminal(`$ h2mm ${command}\n`);

        // Execute the command using the bundled h2mm binary
        this._executeTerminalCommand(command);
    }

    _executeTerminalCommand(command) {
        // Parse command arguments
        const args = command.split(/\s+/);

        this.cliHandler.executeCommand(
            args,
            (output) => {
                // Append stdout to terminal
                if (output && output.trim()) {
                    this._appendToTerminal(output + '\n');
                }
            },
            (error) => {
                // Append stderr to terminal (but don't treat as error for h2mm's informational output)
                if (error && error.trim()) {
                    this._appendToTerminal(error + '\n');
                }
            },
            (exitCode) => {
                // Show exit code if non-zero
                if (exitCode !== 0) {
                    this._appendToTerminal(`Command exited with code: ${exitCode}\n`);
                }
                this._appendToTerminal('\n');
                this._scrollTerminalToBottom();
            }
        );
    }

    _appendToTerminal(text) {
        if (!this.terminal_buffer) return;

        // Get end iterator and insert text
        const endIter = this.terminal_buffer.get_end_iter();
        this.terminal_buffer.insert(endIter, text, -1);

        // Auto-scroll to bottom
        this._scrollTerminalToBottom();
    }

    _scrollTerminalToBottom() {
        if (!this.terminal_output) return;

        // Scroll to the bottom of the text view
        const endIter = this.terminal_buffer.get_end_iter();
        const mark = this.terminal_buffer.get_insert();
        this.terminal_buffer.place_cursor(endIter);
        this.terminal_output.scroll_mark_onscreen(mark);
    }

    _clearTerminal() {
        if (!this.terminal_buffer) return;

        this.terminal_buffer.set_text('H2MM CLI Terminal\nType h2mm commands below. Examples: list, help, status\n\n', -1);
        this._scrollTerminalToBottom();
    }
});


// Application entry point
function main(argv) {
    const application = new H2mmGuiApplication();
    return application.run(argv);
}

// Run the application
main(ARGV);
