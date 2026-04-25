#!/bin/bash
# Install Jarvis background services as macOS LaunchAgents.
# Run once after cloning or after pulling new services.
# Usage: bash infra/install_services.sh

set -e

PLIST_DIR="$(cd "$(dirname "$0")/launchagents" && pwd)"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

install_service() {
    local name="$1"
    local plist="$PLIST_DIR/$name.plist"

    if [ ! -f "$plist" ]; then
        echo "ERROR: $plist not found" && return 1
    fi

    cp "$plist" "$LAUNCH_AGENTS/$name.plist"

    # Unload first if already running (ignore errors if not loaded)
    launchctl unload "$LAUNCH_AGENTS/$name.plist" 2>/dev/null || true
    launchctl load "$LAUNCH_AGENTS/$name.plist"

    echo "  installed + started: $name"
}

echo "Installing Jarvis background services..."
install_service "com.jarvis.secondbrain.watcher"
install_service "com.jarvis.dashboard"
echo ""
echo "Done. Check status with:"
echo "  launchctl list | grep jarvis"
echo "  tail -f ~/jarvis/logs/watcher.log"
echo "  tail -f ~/jarvis/logs/dashboard.log"
echo ""
echo "Dashboard: http://localhost:8501"
