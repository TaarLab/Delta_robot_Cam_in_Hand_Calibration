import cv2
import numpy as np
import PySimpleGUI as psg
import os
from datetime import datetime

# ============================================================
# CAMERA
# ============================================================

cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)

cam.set(cv2.CAP_PROP_FRAME_WIDTH, 4000)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 4000)

print(
    "Camera Resolution:",
    int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)),
    int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
)

# ============================================================
# GUI
# ============================================================

layout = [
    [psg.Text("Circle Radius")],
    [
        psg.Slider(
            range=(10, 500),
            default_value=100,
            orientation="horizontal",
            size=(50, 20),
            key="-A-"
        )
    ],
    [psg.Text("Robot X")],
    [
        psg.Slider(
            range=(-50, 50),
            default_value=0,
            orientation="horizontal",
            key="-B-"
        )
    ],
    [psg.Text("Robot Y")],
    [
        psg.Slider(
            range=(-50, 50),
            default_value=0,
            orientation="horizontal",
            key="-C-"
        )
    ],
    [psg.Text("Robot Z")],
    [
        psg.Slider(
            range=(-81, -37),
            default_value=-37,
            orientation="horizontal",
            key="-D-"
        )
    ],
    [psg.Button("Save All"), psg.Button("Clear Saved"), psg.Exit()]
]

window = psg.Window("Circle Detector", layout, finalize=True)

# ============================================================
# CALIBRATION FILES
# ============================================================

mtx = np.load(
    "../delta_robot_manager/delta_manager/parameters/camera_matrix.npy"
)

dist = np.load(
    "../delta_robot_manager/delta_manager/parameters/dist_coeff.npy"
)

newcameramtx = np.load(
    "../delta_robot_manager/delta_manager/parameters/newcameramtx.npy"
)

roi = np.load(
    "../delta_robot_manager/delta_manager/parameters/roi.npy"
)

# ============================================================
# STORAGE FOR SAVED COORDINATES
# ============================================================

saved_circles = []  # List to store all circle data

def save_circles_with_image(circles_data, image, robot_coord):
    """Save all detected circles and the image with robot coordinates in filename"""
    if not circles_data:
        print("No circles to save!")
        return None, None
    
    # Get robot coordinates
    rx, ry, rz = robot_coord
    
    # Create filename with robot coordinates and number of circles
    # Format: robot_x_X.XX_y_Y.YY_minusZ_ZZ.ZZ_N_123
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Handle negative Z - replace minus sign with 'minus'
    if rz < 0:
        z_str = f"minus{abs(rz):.2f}"
    else:
        z_str = f"{rz:.2f}"
    
    base_filename = (
        f"robot_x_{rx:.2f}_y_{ry:.2f}_{z_str}"
        f"_N_{len(circles_data)}"
    )
    
    # Save numpy file with circle coordinates
    circles_array = np.array(circles_data, dtype=object)
    npy_filename = f"{base_filename}.npy"
    np.save(npy_filename, circles_array)
    print(f"Saved {len(circles_data)} circles to {npy_filename}")
    
    # Save image
    image_filename = f"{base_filename}.jpg"
    cv2.imwrite(image_filename, image)
    print(f"Saved image to {image_filename}")
    
    # Print summary
    print("\nSaved circle data:")
    for i, circle in enumerate(circles_data):
        print(f"Circle {i+1}: Pixel({circle[0]}, {circle[1]}), "
              f"Radius={circle[2]}px, "
              f"Robot({circle[3]:.2f}, {circle[4]:.2f}, {circle[5]:.2f})")
    print()
    
    return npy_filename, image_filename

def clear_saved_circles():
    """Clear all saved circle data"""
    global saved_circles
    saved_circles = []
    print("Cleared all saved circles")

# ============================================================
# DISPLAY WINDOW
# ============================================================

cv2.namedWindow("image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("image", 1200, 900)

# ============================================================
# MAIN LOOP
# ============================================================

robot_capturing_coord = np.array([0, 0, -37])  # Initialize

while True:
    event, values = window.read(timeout=1)
    
    if event == psg.WIN_CLOSED or event == "Exit":
        break
    
    if event == "Save All":
        if saved_circles:
            # Get the last robot coordinates used
            save_circles_with_image(saved_circles, last_display_image, robot_capturing_coord)
            clear_saved_circles()  # Clear after saving
        else:
            print("No circles saved to save!")
        continue
    
    if event == "Clear Saved":
        clear_saved_circles()
        continue
    
    ret, frame = cam.read()
    
    if not ret:
        continue
    
    robot_capturing_coord = np.array([
        int(values["-B-"]),
        int(values["-C-"]),
        int(values["-D-"])
    ])
    
    # ========================================================
    # RADIUS CONTROL
    # ========================================================
    
    radius_target = int(values["-A-"])
    min_radius = max(5, radius_target - 20)
    max_radius = radius_target + 20
    
    # ========================================================
    # UNDISTORT
    # ========================================================
    
    dst = cv2.undistort(
        frame,
        mtx,
        dist,
        None,
        newcameramtx
    )
    
    # ========================================================
    # PREPROCESS
    # ========================================================
    
    gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)
    
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        27,
        3
    )
    
    # ========================================================
    # HOUGH CIRCLES
    # ========================================================
    
    circles = cv2.HoughCircles(
        thresh,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=50,
        param1=100,
        param2=30,
        minRadius=min_radius,
        maxRadius=max_radius
    )
    
    display = dst.copy()
    current_circles = []  # Store circles found in this frame
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype(int)
        
        for (x, y, r) in circles:            
            # Store circle data with robot coordinates
            circle_data = (
                x,  # pixel x
                y,  # pixel y
                r,  # radius in pixels
            )
            current_circles.append(circle_data)
            
            # Draw circle
            cv2.circle(display, (x, y), r, (0, 255, 0), 2)
            cv2.circle(display, (x, y), 3, (0, 0, 255), -1)
            cv2.putText(
                display,
                f"R={r}px",
                (x + 10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )
            cv2.putText(
                display,
                f"Search [{min_radius}-{max_radius}]",
                (x + 10, y + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                1
            )
            
    
    # Display number of circles found and saved
    cv2.putText(
        display,
        f"Found: {len(current_circles)} circles | Saved: {len(saved_circles)}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )
    
    # Display current robot position
    cv2.putText(
        display,
        f"Robot Pos: ({robot_capturing_coord[0]:.1f}, {robot_capturing_coord[1]:.1f}, {robot_capturing_coord[2]:.1f})",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )
    
    # Store the current display image for saving
    last_display_image = display.copy()
    
    cv2.imshow("image", display)
    cv2.imshow("thresh", thresh)
    
    key = cv2.waitKey(1) & 0xFF
    
    # Keyboard shortcuts
    if key == ord("q"):
        break
    elif key == ord("s"):  # Press 's' to save current circles
        if current_circles:
            # Add all current circles to saved list
            saved_circles.extend(current_circles)
            print(f"Added {len(current_circles)} circles to saved list (Total: {len(saved_circles)})")
            # Save immediately with current robot coordinates
            save_circles_with_image(saved_circles, last_display_image, robot_capturing_coord)
            clear_saved_circles()  # Clear after saving
        else:
            print("No circles detected to save!")
    elif key == ord("c"):  # Press 'c' to clear
        clear_saved_circles()
    elif key == ord("a"):  # Press 'a' to add to saved list without saving
        if current_circles:
            saved_circles.extend(current_circles)
            print(f"Added {len(current_circles)} circles to saved list (Total: {len(saved_circles)})")
        else:
            print("No circles detected to add!")

# ============================================================
# CLEANUP
# ============================================================

cam.release()
cv2.destroyAllWindows()
window.close()

print(f"Program ended. Total circles saved: {len(saved_circles)}")