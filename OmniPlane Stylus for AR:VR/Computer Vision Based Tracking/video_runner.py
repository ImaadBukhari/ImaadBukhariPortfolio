from collections import deque
import numpy as np
import imutils
import time
import cv2
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Color boundaries for tracking
lower_color_boundary = (75, 30, 180)
upper_color_boundary = (100, 200, 255)
points = deque(maxlen=64)  # Set a proper maxlen
depth_values = deque(maxlen=100)  # To store depth values for plotting

print("Booting the Stereo Video streams...")
left_vs = cv2.VideoCapture("1stereo1.mov")
right_vs = cv2.VideoCapture("2stereo2.mov")
time.sleep(2.0)

# Create plot window for depth visualization
plt.figure(figsize=(8, 4))
line, = plt.plot([], [], 'r-')
plt.xlabel('Frame')
plt.ylabel('Depth (pixels)')
plt.title('Object Depth')
plt.grid(True)
plt.ion()  # Interactive mode on

def process_frame(frame, is_left=True):
    """Process a frame and return tracking info"""
    frame = imutils.resize(frame, width=700)
    frame = cv2.flip(frame, 1)  # Flip horizontally
    
    # Apply cropping to left video only
    if is_left:
        frame = frame[50:-1, 25:-25]
    
    frame = cv2.flip(frame, 0)  # Flip vertically
    
    # Apply blur and convert to HSV
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # Create mask and clean up with erosion + dilation
    mask = cv2.inRange(hsv, lower_color_boundary, upper_color_boundary)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # Find contours
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    
    center = None
    x, y, radius = 0, 0, 0
    
    if len(contours) > 0:
        contour = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(contour)
        M = cv2.moments(contour)
        if M["m00"] > 0:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            if center is not None:
                cv2.circle(frame, center, 5, (0, 0, 225), -1)
    
    return frame, center, (x, y, radius)

frame_count = 0
baseline = 65  
focal_length = 700 

while True:
    ret_left, left_frame = left_vs.read()
    ret_right, right_frame = right_vs.read()
    
    if not ret_left or not ret_right or left_frame is None or right_frame is None:
        break
    
    # Process both frames
    left_processed, left_center, left_data = process_frame(left_frame, is_left=True)
    right_processed, right_center, right_data = process_frame(right_frame, is_left=False)
    
    # Calculate disparity and depth if we have both centers
    if left_center is not None and right_center is not None:
        # Calculate disparity (difference in x-coordinates)
        disparity = abs(left_center[0] - right_center[0])
        
        # Calculate depth using the formula: depth = (baseline * focal_length) / disparity
        if disparity > 0:  # Avoid division by zero
            depth = (baseline * focal_length) / disparity
            depth_values.append(depth)
            
            # Display depth on frames
            cv2.putText(left_processed, f"Depth: {depth:.2f} mm", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(right_processed, f"Depth: {depth:.2f} mm", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Draw trail on left frame
    if left_center is not None:
        points.appendleft(left_center)
        
        for i in range(1, len(points)):
            if points[i - 1] is None or points[i] is None:
                continue
            thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
            cv2.line(left_processed, points[i - 1], points[i], (0, 0, 225), thickness)
    
    # Create side-by-side display
    h_left, w_left = left_processed.shape[:2]
    h_right, w_right = right_processed.shape[:2]
    
    # Option 1: Resize right frame to match left frame height
    right_resized = cv2.resize(right_processed, (int(w_right * h_left / h_right), h_left))
    combined_frame = np.hstack((left_processed, right_resized))
    cv2.imshow("Stereo Vision", combined_frame)
    
    # Update depth plot every 5 frames
    frame_count += 1
    if frame_count % 5 == 0 and len(depth_values) > 0:
        plt.clf()
        plt.plot(list(range(len(depth_values))), list(depth_values), 'r-')
        plt.xlabel('Frame')
        plt.ylabel('Depth (mm)')
        plt.title('Object Depth Over Time')
        plt.grid(True)
        plt.pause(0.01)
    
    # Break on key press
    key = cv2.waitKey(1)
    if key == ord("x"):
        break

# Cleanup
left_vs.release()
right_vs.release()
cv2.destroyAllWindows()
plt.close()