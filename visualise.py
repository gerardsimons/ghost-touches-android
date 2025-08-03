import matplotlib.pyplot as plt
import re
import sys

# --- Configuration ---
# Max time in seconds between two points to be considered part of the same gesture.
# A good starting value is between 0.2 and 0.5 seconds.
GROUPING_THRESHOLD_SECONDS = 0.5

# Pixel 7 Pro Screen Resolution
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 3120

def parse_and_visualize(log_file):
    """
    Parses a getevent log, groups points by time, and plots them with different colors.
    """
    x_coords = []
    y_coords = []
    colors = []  # This will store a color value for each point

    # A list of distinct colors to cycle through for different gestures
    color_cycle = ['#FF5733', '#33FF57', '#3357FF', '#FF33A1', '#A133FF', 
                   '#33FFA1', '#FFFF33', '#FF8C33', '#33FFF3', '#F333FF']

    current_x = None
    current_y = None
    last_timestamp = 0.0
    group_id = 0

    print(f"Parsing log file with a {GROUPING_THRESHOLD_SECONDS}s grouping threshold...")

    with open(log_file, 'r') as f:
        for line in f:
            if 'ABS_MT_POSITION_X' in line:
                value_str = line.strip().split()[-1]
                current_x = int(value_str, 16)
            elif 'ABS_MT_POSITION_Y' in line:
                value_str = line.strip().split()[-1]
                current_y = int(value_str, 16)

            if 'SYN_REPORT' in line:
                if current_x is not None and current_y is not None:
                    # Extract the timestamp from the line
                    timestamp_str = re.search(r'\[\s*(\d+\.\d+)\s*\]', line).group(1)
                    current_timestamp = float(timestamp_str)

                    # If the time gap is large, it's a new gesture. Move to the next color.
                    if last_timestamp > 0 and (current_timestamp - last_timestamp) > GROUPING_THRESHOLD_SECONDS:
                        group_id += 1
                    
                    # Record the point and its group color
                    x_coords.append(current_x)
                    y_coords.append(SCREEN_HEIGHT - current_y)
                    colors.append(color_cycle[group_id % len(color_cycle)]) # Cycle through colors
                    
                    # Update the timestamp of the last recorded point
                    last_timestamp = current_timestamp

                current_x = None
                current_y = None

    if not x_coords:
        print("No touch coordinates were successfully parsed from the log file.")
        return

    print(f"Found and plotted {len(x_coords)} touch points in {group_id + 1} distinct groups.")

    # --- Plotting ---
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(6, 12))
    
    # Create a scatter plot, using our 'colors' list for the 'c' (color) argument
    ax.scatter(x_coords, y_coords, s=15, c=colors, alpha=0.7, edgecolors='none')

    ax.set_xlim(0, SCREEN_WIDTH)
    ax.set_ylim(0, SCREEN_HEIGHT)
    ax.set_aspect('equal')
    ax.set_title('Time-Grouped Touch Events')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    
    ax.set_xticks([])
    ax.set_yticks([])

    plt.savefig('touch_map_colored.png', dpi=300)
    print("\nColored visualization saved as 'touch_map_colored.png'")
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python visualize_touches.py <path_to_touch_log.txt>")
    else:
        parse_and_visualize(sys.argv[1])