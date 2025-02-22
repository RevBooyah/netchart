# NetChart

A real-time network traffic monitoring tool that displays network interface statistics as charts in your terminal. The display is split into two panels:
- Left panel (75%): Real-time line chart showing upload and download speeds
- Right panel (25%): Network statistics summary and interface details

## Features

- Real-time monitoring of network traffic (send/receive) for all network interfaces
- Auto-scaling line chart with configurable history length
- Detailed statistics panel showing:
  - Total data transferred
  - Peak throughput rates
  - Current throughput rates
  - Per-interface statistics
  - Interface status indicators
  - Active interface count
  - Monitor duration
- Auto-scaling units (KB/s, MB/s, GB/s for speed; KB, MB, GB for data)
- Grid lines for better readability
- Color-coded interface lines
- Status indicators for interface up/down states

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/netchart.git
cd netchart
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable:
```bash
chmod +x netchart.py
```

## Usage

Basic usage:
```bash
./netchart.py
```

### Command Line Options

The following options are available:

- `-i, --interval FLOAT`: Update interval in seconds (default: 1.0)
  ```bash
  ./netchart.py --interval 2.0  # Update every 2 seconds
  ```

- `-h, --history INTEGER`: Number of data points to keep in history (default: 60)
  ```bash
  ./netchart.py --history 120  # Show last 2 minutes of data
  ```

- `--stats/--no-stats`: Show or hide the left statistics panel (default: enabled)
  ```bash
  ./netchart.py --no-stats  # Hide the statistics panel
  ```

- `--auto-scale/--no-auto-scale`: Enable or disable y-axis auto-scaling (default: enabled)
  ```bash
  ./netchart.py --no-auto-scale  # Disable auto-scaling
  ```

You can combine multiple options:
```bash
./netchart.py -i 0.5 --history 180 --no-stats  # Fast updates, longer history, no stats panel
```

## Controls

- Press Ctrl+C to exit the application

## Requirements

- Python 3.6 or higher
- WSL or Linux environment
- Terminal with Unicode support
- Required Python packages (see requirements.txt):
  - psutil: For network statistics
  - typer: For CLI interface
  - plotext: For terminal-based plotting


