import matplotlib.pyplot as plt
import re
import sys

# --- Configuration ---
GHOST_TOUCH_DURATION_THRESHOLD_S = 0.05
GESTURE_GAP_THRESHOLD_S = 0.5
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 3120

def classify_gesture(gesture_points):
    """Applies heuristics to classify a gesture. Returns 'ghost' or 'human'."""
    if not gesture_points:
        return 'human'
    
    start_time = gesture_points[0]['timestamp']
    end_time = gesture_points[-1]['timestamp']
    duration = end_time - start_time
    
    if duration < GHOST_TOUCH_DURATION_THRESHOLD_S:
        return 'ghost'
        
    return 'human'

def parse_and_visualize(log_file):
    """Parses, classifies, and creates an advanced plot of touch events."""
    all_gestures = []
    current_gesture_points = []
    current_x, current_y, last_timestamp = None, None, 0.0

    print("Step 1: Parsing log file to identify gestures...")
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
                    timestamp_str = re.search(r'\[\s*(\d+\.\d+)\s*\]', line).group(1)
                    current_timestamp = float(timestamp_str)
                    
                    if current_gesture_points and (current_timestamp - last_timestamp) > GESTURE_GAP_THRESHOLD_S:
                        # **FIX**: Store the gesture as a dictionary
                        all_gestures.append({'points': current_gesture_points})
                        current_gesture_points = []

                    current_gesture_points.append({'x': current_x, 'y': current_y, 'timestamp': current_timestamp})
                    last_timestamp = current_timestamp
                current_x, current_y = None, None
                
    if current_gesture_points:
        # **FIX**: Store the final gesture as a dictionary
        all_gestures.append({'points': current_gesture_points})

    # --- Analysis and Statistics ---
    print("Step 2: Classifying gestures and calculating statistics...")
    num_ghost_points = 0
    total_points = sum(len(g['points']) for g in all_gestures)
    
    for gesture in all_gestures:
        # **FIX**: Pass the list of points to the function and store the result in the dictionary
        points = gesture['points']
        classification = classify_gesture(points)
        gesture['classification'] = classification
        if classification == 'ghost':
            num_ghost_points += len(points)

    print("\n--- Classification Summary ---")
    if total_points > 0:
        ghost_percentage = (num_ghost_points / total_points) * 100
        print(f"Total Touch Points Recorded: {total_points}")
        print(f"Gestures Found: {len(all_gestures)}")
        print(f"Suspected Ghost Points: {num_ghost_points}")
        print(f"Ghost Touch Percentage: {ghost_percentage:.2f}%")
    else:
        print("No touch points were found to analyze.")
        return

    # --- Plotting ---
    print("Step 3: Generating advanced visualization...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(6, 12))
    color_cycle = ['#FF5733', '#33FF57', '#3357FF', '#FF33A1', '#A133FF', 
                   '#33FFA1', '#FFFF33', '#FF8C33', '#33FFF3', '#F333FF']
    group_id = 0
    last_gesture_timestamp = 0.0

    for gesture in all_gestures:
        points = gesture['points']
        if not points:
            continue
        
        if last_gesture_timestamp > 0 and (points[0]['timestamp'] - last_gesture_timestamp) > GESTURE_GAP_THRESHOLD_S:
            group_id += 1
        
        # **FIX**: Access classification from the dictionary key
        color = color_cycle[group_id % len(color_cycle)]
        marker = 'x' if gesture['classification'] == 'ghost' else 'o'
        
        x_coords = [p['x'] for p in points]
        y_coords = [SCREEN_HEIGHT - p['y'] for p in points]

        ax.plot(x_coords, y_coords, color=color, linewidth=1, alpha=0.6)
        ax.scatter(x_coords, y_coords, s=20, c=color, marker=marker, alpha=0.7)
        ax.scatter(x_coords[0], y_coords[0], s=60, c=color, marker=marker,
                   edgecolors='white', linewidths=1)

        last_gesture_timestamp = points[-1]['timestamp']

    ax.set_xlim(0, SCREEN_WIDTH)
    ax.set_ylim(0, SCREEN_HEIGHT)
    ax.set_aspect('equal')
    ax.set_title('Gesture Analysis')
    ax.set_xticks([])
    ax.set_yticks([])

    plt.savefig('touch_map_analysis.png', dpi=300)
    print("\nAnalysis visualization saved as 'touch_map_analysis.png'")
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python visualize_touches.py <path_to_touch_log.txt>")
    else:
        parse_and_visualize(sys.argv[1])