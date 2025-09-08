# GUI Setup for Docker Container

This document explains how to run the PDF Search application with GUI support from within a Docker container.

## Quick Start

### Linux (X11)

The easiest way to run the GUI application on Linux:

```bash
# Run the helper script
./scripts/run_gui.sh
```

Or manually:

```bash
# Allow Docker to connect to X server
xhost +local:docker

# Run with GUI support
docker-compose -f docker-compose.yml -f docker-compose.gui.yml run --rm app

# Cleanup (optional)
xhost -local:docker
```

### Manual Setup

1. **Allow X11 connections:**
   ```bash
   xhost +local:docker
   ```

2. **Run the application:**
   ```bash
   docker-compose run --rm \
     -e QT_QPA_PLATFORM= \
     -e DISPLAY="$DISPLAY" \
     -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
     -v "$HOME/.Xauthority:/root/.Xauthority:ro" \
     app
   ```

3. **Cleanup (when done):**
   ```bash
   xhost -local:docker
   ```

## Configuration Options

### Default Mode (Headless)
The default docker-compose.yml runs in headless mode:
- `QT_QPA_PLATFORM=offscreen`
- No GUI windows displayed
- Suitable for development and testing

### GUI Mode
Use docker-compose.gui.yml for GUI applications:
- `QT_QPA_PLATFORM=` (empty, enables GUI)
- `DISPLAY` environment variable passed through
- X11 socket mounted for window forwarding

## Troubleshooting

### "cannot connect to X server" Error

1. **Check DISPLAY variable:**
   ```bash
   echo $DISPLAY
   ```

2. **Ensure X11 forwarding is enabled:**
   ```bash
   xhost +local:docker
   ```

3. **Verify .Xauthority exists:**
   ```bash
   ls -la ~/.Xauthority
   ```

### Permission Denied Errors

1. **Check X11 socket permissions:**
   ```bash
   ls -la /tmp/.X11-unix/
   ```

2. **Run xhost command:**
   ```bash
   xhost +local:docker
   ```

### GUI Application Crashes

1. **Check container logs:**
   ```bash
   docker-compose logs app
   ```

2. **Test with simple GUI app:**
   ```bash
   docker run --rm -it \
     -e DISPLAY="$DISPLAY" \
     -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
     python:3.11-slim \
     bash -c "apt-get update && apt-get install -y x11-apps && xeyes"
   ```

## Security Considerations

### X11 Security
- `xhost +local:docker` allows local Docker containers to access your display
- This is generally safe for development but avoid in production
- Always run `xhost -local:docker` when done

### Alternative: Xephyr
For better security, use Xephyr (nested X server):

```bash
# Install Xephyr
sudo apt-get install xserver-xephyr

# Start nested X server
Xephyr -ac -screen 1024x768 -br -reset -terminate :2 &

# Run container with nested display
docker-compose run --rm -e DISPLAY=:2 app
```

## macOS Support

GUI forwarding on macOS requires XQuartz:

1. **Install XQuartz:**
   ```bash
   brew install --cask xquartz
   ```

2. **Configure XQuartz:**
   - Start XQuartz
   - Go to Preferences → Security
   - Enable "Allow connections from network clients"

3. **Run container:**
   ```bash
   docker-compose run --rm \
     -e DISPLAY=host.docker.internal:0 \
     app
   ```

## Windows Support

GUI forwarding on Windows requires an X server like VcXsrv or Xming:

1. **Install VcXsrv**
2. **Configure with "Disable access control"**
3. **Run container:**
   ```bash
   docker-compose run --rm \
     -e DISPLAY=host.docker.internal:0.0 \
     app
   ```

## Development Workflow

### Live Development
For development with live code reloading:

```bash
# Start services
docker-compose up -d elasticsearch

# Run GUI application with code mounted
docker-compose -f docker-compose.yml -f docker-compose.gui.yml run --rm app
```

### Testing GUI Components
Use the CLI interface for testing without GUI:

```bash
# Test core functionality
docker-compose exec app python src/cli.py health
docker-compose exec app python src/cli.py search "test query"
```

## Performance Tips

1. **Use host networking** for better performance:
   ```yaml
   network_mode: host
   ```

2. **Mount only necessary directories** to reduce I/O overhead

3. **Use local X11 socket** instead of TCP for better performance

4. **Limit container resources** to prevent system slowdown:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2.0'
         memory: 4g
   ```