#!/usr/bin/env python3

import psutil
import typer
import plotext as plt
import os
import shutil
from time import sleep
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

# Initialize data structures for storing network stats
interfaces_data: Dict[str, Dict[str, List]] = defaultdict(lambda: {
    'bytes_sent': [],
    'bytes_recv': [],
    'timestamps': [],
    'peak_sent': 0,
    'peak_recv': 0,
    'total_sent': 0,
    'total_recv': 0,
    'start_time': datetime.now()
})

def get_terminal_size():
    """Get terminal size and account for padding."""
    columns, rows = shutil.get_terminal_size()
    # Leave some space for borders and labels
    return columns - 5, rows - 3

def move_cursor_to_top():
    """Move cursor to the top of the screen without clearing."""
    print('\033[H', end='')

def get_network_stats() -> Dict[str, Tuple[float, float]]:
    """Get current network statistics for all interfaces."""
    stats = {}
    net_io = psutil.net_io_counters(pernic=True)
    for interface, data in net_io.items():
        if interface != 'lo':  # Exclude loopback interface
            stats[interface] = (data.bytes_sent, data.bytes_recv)
    return stats

def calculate_speed(current: float, previous: float) -> float:
    """Calculate speed in KB/s."""
    return (current - previous) / 1024  # Convert to KB/s

def format_speed(speed: float) -> str:
    """Format speed with appropriate unit."""
    if speed >= 1024 * 1024:  # >= 1 GB/s
        return f"{speed / (1024 * 1024):.2f} GB/s"
    elif speed >= 1024:  # >= 1 MB/s
        return f"{speed / 1024:.2f} MB/s"
    else:
        return f"{speed:.2f} KB/s"

def format_bytes(bytes: float) -> str:
    """Format bytes with appropriate unit."""
    if bytes >= 1024 * 1024 * 1024:  # >= 1 GB
        return f"{bytes / (1024 * 1024 * 1024):.2f} GB"
    elif bytes >= 1024 * 1024:  # >= 1 MB
        return f"{bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes / 1024:.2f} KB"

def get_interface_status(interface: str) -> bool:
    """Check if interface is up."""
    try:
        return psutil.net_if_stats()[interface].isup
    except:
        return False

def update_data(stats: Dict[str, Tuple[float, float]], previous_stats: Dict[str, Tuple[float, float]], history_size: int = 60):
    """Update the data structures with new network statistics."""
    for interface in stats:
        if interface in previous_stats:
            sent_speed = calculate_speed(stats[interface][0], previous_stats[interface][0])
            recv_speed = calculate_speed(stats[interface][1], previous_stats[interface][1])
            
            # Update peak speeds
            interfaces_data[interface]['peak_sent'] = max(interfaces_data[interface]['peak_sent'], sent_speed)
            interfaces_data[interface]['peak_recv'] = max(interfaces_data[interface]['peak_recv'], recv_speed)
            
            # Update total transfer
            interfaces_data[interface]['total_sent'] = stats[interface][0]
            interfaces_data[interface]['total_recv'] = stats[interface][1]
            
            interfaces_data[interface]['bytes_sent'].append(sent_speed)
            interfaces_data[interface]['bytes_recv'].append(recv_speed)
            interfaces_data[interface]['timestamps'].append(len(interfaces_data[interface]['timestamps']))
            
            if len(interfaces_data[interface]['timestamps']) > history_size:
                interfaces_data[interface]['bytes_sent'].pop(0)
                interfaces_data[interface]['bytes_recv'].pop(0)
                interfaces_data[interface]['timestamps'].pop(0)
                interfaces_data[interface]['timestamps'] = list(range(len(interfaces_data[interface]['timestamps'])))

def create_stats_display(width: int, height: int) -> List[str]:
    """Create the statistics display for the right panel."""
    # Calculate totals and stats
    total_sent = 0
    total_recv = 0
    peak_sent = 0
    peak_recv = 0
    current_sent = 0
    current_recv = 0
    
    for data in interfaces_data.values():
        if data['timestamps']:
            total_sent += data['total_sent']
            total_recv += data['total_recv']
            peak_sent = max(peak_sent, data['peak_sent'])
            peak_recv = max(peak_recv, data['peak_recv'])
            current_sent += data['bytes_sent'][-1]
            current_recv += data['bytes_recv'][-1]

    # Create the display with proper width formatting
    panel_width = width - 2  # Account for borders
    lines = []
    lines.append("┌" + "─" * panel_width + "┐")
    lines.append("│" + "Network Summary".center(panel_width) + "│")
    lines.append("│" + "═" * panel_width + "│")
    lines.append("│" + " " * panel_width + "│")
    
    # Helper function to add a line with proper borders
    def add_line(text="", emoji_count=0):
        # Adjust padding for emoji characters (each emoji takes 2 display columns but 1 string length)
        adjusted_width = panel_width - emoji_count  # Subtract emoji count to account for double-width display
        lines.append("│" + text.ljust(adjusted_width) + "│")

    add_line(" Total Transferred:")
    add_line(f"   ↑ {format_bytes(total_sent)}")
    add_line(f"   ↓ {format_bytes(total_recv)}")
    add_line()
    add_line(" Peak Throughput:")
    add_line(f"   ↑ {format_speed(peak_sent)}")
    add_line(f"   ↓ {format_speed(peak_recv)}")
    add_line()
    add_line(" Current Throughput:")
    add_line(f"   ↑ {format_speed(current_sent)}")
    add_line(f"   ↓ {format_speed(current_recv)}")
    add_line()
    
    # Add per-interface statistics
    add_line(" Interface Details:")
    for interface, data in interfaces_data.items():
        if data['timestamps']:
            is_up = get_interface_status(interface)
            status = "🟢" if is_up else "🔴"
            add_line()
            add_line(f" {status} {interface}:", emoji_count=1)  # Account for emoji width
            add_line(f"   Current: ↑{format_speed(data['bytes_sent'][-1])}")
            add_line(f"           ↓{format_speed(data['bytes_recv'][-1])}")
    
    add_line()
    add_line(" Active Interfaces:")
    add_line(f"   {len([d for d in interfaces_data.values() if d['timestamps']])}")
    add_line()
    
    # Add duration
    duration = datetime.now() - next(iter(interfaces_data.values()))['start_time']
    hours = int(duration.total_seconds() // 3600)
    minutes = int((duration.total_seconds() % 3600) // 60)
    seconds = int(duration.total_seconds() % 60)
    add_line(" Monitor Duration:")
    add_line(f"   {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    # Fill remaining space and add bottom border
    while len(lines) < height - 1:
        add_line()
    lines.append("└" + "─" * panel_width + "┘")
    
    return lines

def plot_network_traffic(show_stats: bool = True, auto_scale: bool = True, history_size: int = 60, dark_mode: bool = False):
    """Plot network traffic for all interfaces."""
    width, height = get_terminal_size()
    
    # Calculate panel sizes (75% chart, 25% stats)
    chart_width = int(width * 0.75)
    stats_width = width - chart_width
    
    # Create the chart
    plt.clear_data()
    plt.clear_figure()
    plt.plotsize(chart_width, height)
    
    # Set theme
    if dark_mode:
        plt.theme('dark')
    else:
        plt.theme('default')
    
    colors = ['red', 'blue', 'green', 'yellow', 'magenta', 'cyan']
    color_idx = 0
    
    # Calculate max speed for y-axis scaling
    max_speed = 1.0  # minimum scale
    if auto_scale:
        for interface_data in interfaces_data.values():
            if interface_data['bytes_sent'] or interface_data['bytes_recv']:
                max_speed = max(max_speed,
                              max(interface_data['bytes_sent'] + [0]),
                              max(interface_data['bytes_recv'] + [0]))
        plt.ylim(0, max_speed * 1.1)
    
    # Plot each interface
    for interface, data in interfaces_data.items():
        if not data['timestamps']:
            continue
        
        plt.plot(data['timestamps'], 
                data['bytes_sent'],
                label=f"{interface} (TX)",
                color=colors[color_idx % len(colors)])
        
        plt.plot(data['timestamps'],
                data['bytes_recv'],
                label=f"{interface} (RX)",
                color=colors[(color_idx + 1) % len(colors)])
        
        color_idx += 2
    
    plt.title("Network Traffic Monitor")
    plt.xlabel(f"Seconds ago (last {history_size}s)")
    plt.ylabel("Speed")
    plt.grid(True)
    plt.xlim(0, history_size)
    
    # Get the chart as string
    chart_lines = plt.build().split('\n')
    
    # Create the stats display
    stats_lines = create_stats_display(stats_width, height)
    
    # Combine chart and stats side by side
    print('\033[H', end='')  # Move cursor to top
    for i in range(height):
        chart_line = chart_lines[i] if i < len(chart_lines) else ' ' * chart_width
        stats_line = stats_lines[i] if i < len(stats_lines) else ' ' * stats_width
        print(chart_line + stats_line)

def main(
    interval: float = typer.Option(1.0, "--interval", "-i", help="Update interval in seconds"),
    history: int = typer.Option(60, "--history", "-h", help="Number of data points to keep in history"),
    show_stats: bool = typer.Option(True, "--stats/--no-stats", help="Show/hide statistics panel"),
    auto_scale: bool = typer.Option(True, "--auto-scale/--no-auto-scale", help="Auto-scale y-axis"),
    dark_mode: bool = typer.Option(False, "--dark/--light", help="Use dark or light theme"),
):
    """Network traffic monitor with real-time charts."""
    # Clear screen once at the start and hide cursor
    print('\033[2J\033[?25l', end='')
    try:
        previous_stats = get_network_stats()
        while True:
            current_stats = get_network_stats()
            update_data(current_stats, previous_stats, history)
            plot_network_traffic(show_stats, auto_scale, history, dark_mode)
            previous_stats = current_stats
            sleep(interval)
    except KeyboardInterrupt:
        # Show cursor again before exiting
        print('\033[?25h\nExiting...')

if __name__ == "__main__":
    typer.run(main) 