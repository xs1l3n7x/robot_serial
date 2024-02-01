import cv2
import numpy as np

# Define the chessboard size (number of inner corners)
chessboard_size = (3, 3)

# Initialize the webcam
cap = cv2.VideoCapture(1)  # 0 for the default camera, adjust as needed

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    if not ret:
        break
    
    # Apply Gaussian blur to the frame
    blurred = cv2.GaussianBlur(frame, (9, 5), 0)
    # Convert the frame to grayscale
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to the grayscale image
    _, thresholded = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)

    # Try to find the chessboard corners in the thresholded image
    ret, corners = cv2.findChessboardCorners(thresholded, chessboard_size, None)

    if ret:
        # If corners are found, draw them on the frame
        cv2.drawChessboardCorners(frame, chessboard_size, corners, ret)

    # Display the frame
    cv2.imshow('Chessboard Detection', frame)
    cv2.imshow('Thresh', thresholded)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()