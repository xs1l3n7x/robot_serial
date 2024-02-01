import cv2
import numpy as np

# Initialize video capture
cap = cv2.VideoCapture(1)  # 0 for the default camera, adjust as needed

# Initialize the tracker
tracker = cv2.createBackgroundSubtractorMOG2()

while True:
    # Read a new frame from the video
    ret, frame = cap.read()
    blurred = cv2.GaussianBlur(frame, (3, 3), 0)
    mask = tracker.apply(blurred)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Minimum area threshold
    min_area = 5000  # Replace with your desired minimum area

    # Use a list comprehension to filter contours by area
    filtered_contours = [contour for contour in contours if cv2.contourArea(contour) >= min_area]
    
    for contour in filtered_contours:
        cv2.drawContours(frame, [contour], -1, (255, 0, 0), 2)
    # Display the frame
    cv2.imshow("Object Tracking", frame)
    cv2.imshow("mask", mask)
    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close OpenCV windows
cap.release()