// CLI Handler Module for H2MM GUI
// This module handles interactions with the h2mm-cli tool

const { GLib, Gio } = imports.gi;

var CliHandler = class CliHandler {
    constructor() {
        this.isRunning = false;
        this.currentProcess = null;
    }

    // Check if h2mm-cli is available
    checkCliAvailable() {
        try {
            let [success, stdout, stderr, exitStatus] = GLib.spawn_command_line_sync('which h2mm-cli');
            return success && exitStatus === 0;
        } catch (error) {
            print(`Error checking h2mm-cli availability: ${error.message}`);
            return false;
        }
    }

    // Execute h2mm-cli command asynchronously
    executeCommand(args, onOutput = null, onError = null, onComplete = null) {
        if (this.isRunning) {
            if (onError) onError('A command is already running');
            return;
        }

        this.isRunning = true;
        
        try {
            const command = ['h2mm-cli', ...args];
            
            let proc = new Gio.Subprocess({
                argv: command,
                flags: Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE
            });
            
            proc.init(null);
            this.currentProcess = proc;

            // Read stdout
            if (onOutput) {
                this._readStream(proc.get_stdout_pipe(), onOutput);
            }

            // Read stderr
            if (onError) {
                this._readStream(proc.get_stderr_pipe(), onError);
            }

            // Wait for completion
            proc.wait_async(null, (proc, result) => {
                try {
                    proc.wait_finish(result);
                    const exitCode = proc.get_exit_status();
                    
                    this.isRunning = false;
                    this.currentProcess = null;
                    
                    if (onComplete) {
                        onComplete(exitCode);
                    }
                } catch (error) {
                    this.isRunning = false;
                    this.currentProcess = null;
                    if (onError) {
                        onError(`Process error: ${error.message}`);
                    }
                    if (onComplete) {
                        onComplete(-1);
                    }
                }
            });

        } catch (error) {
            this.isRunning = false;
            this.currentProcess = null;
            if (onError) {
                onError(`Failed to start process: ${error.message}`);
            }
            if (onComplete) {
                onComplete(-1);
            }
        }
    }

    // Helper method to read from streams
    _readStream(stream, callback) {
        const dataInputStream = new Gio.DataInputStream({
            base_stream: stream
        });

        const readLine = () => {
            dataInputStream.read_line_async(GLib.PRIORITY_DEFAULT, null, (stream, result) => {
                try {
                    let [line, length] = dataInputStream.read_line_finish(result);
                    if (line !== null) {
                        // Fix: Use TextDecoder instead of toString() on Uint8Array
                        const decoder = new TextDecoder('utf-8');
                        const lineText = decoder.decode(line);
                        callback(lineText);
                        readLine(); // Continue reading
                    }
                } catch (error) {
                    // Stream ended or error occurred
                }
            });
        };

        readLine();
    }

    // Cancel current operation
    cancel() {
        if (this.currentProcess) {
            this.currentProcess.force_exit();
            this.isRunning = false;
            this.currentProcess = null;
        }
    }

    // Get common h2mm-cli commands
    getAvailableCommands() {
        return [
            { name: 'Install Mod', command: 'install', description: 'Install a new mod' },
            { name: 'List Mods', command: 'list', description: 'List installed mods' },
            { name: 'Remove Mod', command: 'remove', description: 'Remove an installed mod' },
            { name: 'Update Mods', command: 'update', description: 'Update all mods' },
            { name: 'Check Status', command: 'status', description: 'Check mod status' }
        ];
    }
};
