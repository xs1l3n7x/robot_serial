import cv2
import math

# Initialize webcam capture (0 is usually the default camera)
cap = cv2.VideoCapture(1)

# Initialize point A and point B coordinates as None
point_a = None
point_b = None

# Specify the maximum distance in mm
max_distance_mm = 200

# Create a function to calculate the distance
def calculate_distance(event, x, y, flags, param):
    global point_a, point_b
    global cap
    frame_width = int(cap.get(3))  # Width of the captured frame
    frame_height = int(cap.get(4))  # Height of the captured frame
    if event == cv2.EVENT_LBUTTONDOWN:
        if point_a is not None:
            dx = x - point_a[0]  # Calculate the x difference
            dy = point_a[1] - y  # Convert y-coordinate difference to positive
            distance_x_mm = (dx / frame_width) * max_distance_mm
            distance_y_mm = (dy / frame_height) * max_distance_mm
            print(f"Distance from clicked point to point A (X): {distance_x_mm:.2f} mm")
            print(f"Distance from clicked point to point A (Y): {distance_y_mm:.2f} mm")

# Create a mouse callback function for calibration
def calibrate(event, x, y, flags, param):
    global point_a, point_b

    if event == cv2.EVENT_LBUTTONDOWN:
        if point_a is None:
            point_a = (x, y)
            print(f"Point A coordinates set to ({x}, {y})")
        elif point_b is None:
            point_b = (x, y)
            print(f"Point B coordinates set to ({x}, {y})")

# Create a window for the main program and set the mouse callback for distance calculation
cv2.namedWindow('Main Program')
cv2.setMouseCallback('Main Program', calculate_distance)



# Create a variable to track if calibration is completed
calibration_completed = False

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    if not calibration_completed:
        # Calibration phase: Draw a circle at Point A and Point B if they are set during calibration
        if point_a is not None:
            cv2.circle(frame, point_a, 5, (0, 0, 255), -1)
        if point_b is not None:
            cv2.circle(frame, point_b, 5, (0, 255, 0), -1)

    # Display the frame
    cv2.imshow('Main Program', frame)

    # Check if calibration is completed
    if not calibration_completed:
        print("Calibration: Click on the webcam feed to set Point A and Point B coordinates.")
        print("Press 'c' when both points are set.")
        # Create a window and set the mouse callback for calibration
        cv2.namedWindow('Main Program')
        cv2.setMouseCallback('Main Program', calibrate)

    # Break the loop and proceed to the main program when 'c' is pressed
    if point_a and point_b:
        calibration_completed = True

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if calibration_completed:
        # Create a window and set the mouse callback for calibration
        cv2.namedWindow('Main Program')
        cv2.setMouseCallback('Main Program', calculate_distance)


# Release the webcam and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()