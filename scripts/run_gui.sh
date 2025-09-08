#!/bin/bash
# Script to run the PDF search application with GUI support

set -e

echo "Setting up GUI environment for Docker..."

# Check if running on Linux with X11
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux - setting up X11 forwarding"
    
    # Allow Docker containers to connect to X server
    xhost +local:docker 2>/dev/null || {
        echo "Warning: Could not run 'xhost +local:docker'"
        echo "You may need to install xhost or run as a user with X11 access"
    }
    
    # Ensure .Xauthority exists
    if [[ ! -f "$HOME/.Xauthority" ]]; then
        echo "Creating .Xauthority file..."
        touch "$HOME/.Xauthority"
    fi
    
    echo "Starting application with GUI support..."
    docker-compose run --rm \
        -e QT_QPA_PLATFORM= \
        -e DISPLAY="$DISPLAY" \
        app
        
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS - GUI forwarding requires XQuartz"
    echo "Please ensure XQuartz is installed and running"
    echo "Then run: docker-compose run --rm -e DISPLAY=host.docker.internal:0 app"
    
else
    echo "Unsupported OS for GUI forwarding: $OSTYPE"
    echo "Running in headless mode..."
    docker-compose run --rm app
fi

# Cleanup
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Cleaning up X11 permissions..."
    xhost -local:docker 2>/dev/null || true
fi