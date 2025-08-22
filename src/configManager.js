// Configuration Manager for H2MM GUI
// Handles application settings and preferences

const { GLib, Gio } = imports.gi;

var ConfigManager = class ConfigManager {
    constructor() {
        this.configDir = GLib.build_filenamev([GLib.get_user_config_dir(), 'h2mm-gui']);
        this.configFile = GLib.build_filenamev([this.configDir, 'config.json']);
        this.defaultConfig = {
            window: {
                width: 800,
                height: 600,
                maximized: false
            },
            h2mm: {
                cliPath: 'h2mm-cli',
                autoUpdate: true,
                confirmActions: true
            },
            ui: {
                theme: 'auto',
                showTooltips: true,
                animationsEnabled: true
            }
        };
        
        this.config = this.loadConfig();
    }

    // Ensure config directory exists
    _ensureConfigDir() {
        const dir = Gio.File.new_for_path(this.configDir);
        if (!dir.query_exists(null)) {
            try {
                dir.make_directory_with_parents(null);
            } catch (error) {
                print(`Error creating config directory: ${error.message}`);
            }
        }
    }

    // Load configuration from file
    loadConfig() {
        try {
            const file = Gio.File.new_for_path(this.configFile);
            if (file.query_exists(null)) {
                const [success, contents] = file.load_contents(null);
                if (success) {
                    const configText = new TextDecoder().decode(contents);
                    const loadedConfig = JSON.parse(configText);
                    return { ...this.defaultConfig, ...loadedConfig };
                }
            }
        } catch (error) {
            print(`Error loading config: ${error.message}`);
        }
        
        return { ...this.defaultConfig };
    }

    // Save configuration to file
    saveConfig() {
        this._ensureConfigDir();
        
        try {
            const file = Gio.File.new_for_path(this.configFile);
            const configText = JSON.stringify(this.config, null, 2);
            const bytes = new TextEncoder().encode(configText);
            
            file.replace_contents(bytes, null, false, Gio.FileCreateFlags.NONE, null);
        } catch (error) {
            print(`Error saving config: ${error.message}`);
        }
    }

    // Get configuration value
    get(path) {
        const keys = path.split('.');
        let value = this.config;
        
        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return undefined;
            }
        }
        
        return value;
    }

    // Set configuration value
    set(path, value) {
        const keys = path.split('.');
        let target = this.config;
        
        for (let i = 0; i < keys.length - 1; i++) {
            const key = keys[i];
            if (!(key in target) || typeof target[key] !== 'object') {
                target[key] = {};
            }
            target = target[key];
        }
        
        target[keys[keys.length - 1]] = value;
        this.saveConfig();
    }
};
