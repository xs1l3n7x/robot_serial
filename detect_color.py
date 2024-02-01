import cv2
import numpy as np

# Initialize the webcam
cap = cv2.VideoCapture(1)  # 0 represents the default camera (you can change this if you have multiple cameras)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for yellow in HSV
    lower_yellow = np.array([3, 145, 145])  # Lower bound for yellow in HSV
    upper_yellow = np.array([40, 255, 255])  # Upper bound for yellow in HSV
    lower_red = np.array([0, 100, 100])  # Lower bound for red in HSV
    upper_red = np.array([10, 255, 255])  # Upper bound for red in HSV
    # Create a mask that selects pixels within the specified yellow color range
    mask = cv2.inRange(hsv_frame, lower_red, upper_red)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize a list to store the coordinates of yellow objects
    yellow_object_coordinates = []
    # Initialize a list to store the simplified contours of yellow objects
    simplified_contours = []
    # Iterate through the detected contours
    for contour in contours:
        # Simplify the contour to have 4 points using Douglas-Peucker algorithm
        epsilon = 0.03 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        simplified_contours.append(approx)
        # Calculate the centroid (x, y) of each contour
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            yellow_object_coordinates.append((cX, cY))

    # Print the coordinates of yellow objects
    for i, (x, y) in enumerate(yellow_object_coordinates):
        print(f"Yellow object {i + 1}: X = {x}, Y = {y} - {cv2.contourArea(contour)}")

    # Draw the contours on the frame
    simplified_contours = [contour for contour in contours if cv2.contourArea(contour) <= 500]
    cv2.drawContours(frame, simplified_contours, -1, (0, 255, 0), 2)

    # Display the frame with contours
    cv2.imshow('Yellow Object Detection', frame)

    # Break the loop when the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()