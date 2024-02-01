import cv2
import numpy as np

# Initialize video capture
cap = cv2.VideoCapture(1)  # 0 for the default camera, adjust as needed

# Initialize the tracker (Mean-Shift)
tracker = cv2.TrackerMIL_create()

# Read the first frame
ret, frame = cap.read()

# Define a region of interest (ROI) for tracking
bbox = cv2.selectROI("Select Object to Track", frame, fromCenter=False, showCrosshair=True)
tracker.init(frame, bbox)

while True:
    # Read a new frame from the video
    ret, frame = cap.read()

    # Update the tracker
    ret, bbox = tracker.update(frame)

    # Convert the coordinates to integers
    bbox = tuple(map(int, bbox))

    # Draw the tracking rectangle on the frame
    if ret:
        cv2.rectangle(frame, bbox, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "Tracking Failed", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow("Object Tracking", frame)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close OpenCV windows
cap.release()