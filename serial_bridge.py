import math
import re
import serial
import time
import sys
import pygame
import cv2
import math
from functools import partial
import numpy as np
#PORT DECLARATIONS
port = 'COM4' #SEE PORT NAME IN ARDUINO IDE: TOOLS>PORT:
baud = 115200 #BY DEFAULT 115200
timeout = None #LEAVE AS IS
ser = None
time.sleep(2)

#LIST OF COMMANDS TO BE EXECUTED BY ROBOT ARM, CHANGE ACCORDINGLY
cmdList = []
bCmdList = []
prevCmdList = []
prevCmd = None
fileProcess = False

last_coords = [0, 180, 100, 0]


for cmd in cmdList:
    cmd_temp = cmd + '\r'
    bCmdList.append(cmd_temp.encode('utf-8'))

def print_cmds():
    print("> homing: G28")
    print("> movement: G0 X0 Y0 Z0 E0 / Absolute mode: G90 / Relative mode: G91")
    print("> gripper: M3/M5 - laser M6/M7 - pump M1/M2")
    print("> fan: M106/M107")
    print("> dwell: G4 1S")
    print("> disable steppers: M17/M18")
    print("> report coordenates: M114")


def wait_complete():
    waitstatus = 1
    while True:
        a = ser.readline()
        b = a
        print(a.decode("utf-8"))
        
        if "ERROR" or "INFO" in b.decode("utf-8"):
            getLastCoordenates(b.decode("utf-8"))

        if "ok" in a.decode("utf-8"):
            waitstatus = 0
            break
        if "COMMAND NOT RECOGNIZED" in a.decode("utf-8"):
            waitstatus = 0
            break
        

def getLastCoordenates(response):
    global last_coords
    # Define a regular expression pattern to extract the values
    pattern = r"X:([\d.]+) Y:([\d.]+) Z:([\d.]+) E:([\d.]+)"

    # Use re.search to find the values
    match = re.search(pattern, response)

    if match:
        x_value = float(match.group(1))
        y_value = float(match.group(2))
        z_value = float(match.group(3))
        e_value = float(match.group(4))
        last_coords = [x_value, y_value, z_value, e_value]
        print(f" last coordenates X: {x_value}, Y: {y_value}, Z: {z_value}, E: {e_value}")
    else:
        print("Commands yielded no coordenates")

def circle(radius, numpts):
    # Define the parameters of the circle
    center_x = 0.0  # Center X-coordinate
    center_y = 160.0  # Center Y-coordinate
    z_start = 70.0    # Starting Z-coordinate
    radius = int(radius)     # Radius of the circle
    num_points = int(numpts)  # Number of points to generate

    gcode = f'M205 S0\r'  # Use G0 for rapid positioning
    gcode = gcode.encode('utf-8')
    ser.write(gcode)
    wait_complete()
    # Generate G-code to trace the circle
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = center_x + radius * math.cos(angle)  # Move in the X-axis
        z = z_start + radius * math.sin(angle)   # Move in the Z-axis
        gcode = f'G0 X{x} Y{center_y} Z{z}\r'  # Use G0 for rapid positioning
        gcode = gcode.encode('utf-8')
        print(gcode)
        try:
            ser.write(gcode)
        except Exception:
            print('circle error')
        wait_complete()
    gcode = f'M205 S2\r'  # Use G0 for rapid positioning
    gcode = gcode.encode('utf-8')
    ser.write(gcode)
    wait_complete()

def process_file():
    file1 = open(sys.argv[2], 'r')
    Lines = file1.readlines()
    # Strips the newline character
    count = 0
    for line in Lines:
        count += 1
        new_cmd = line.strip()
        # if 'G28' in new_cmd:
        #     break
        try:
            new_cmd = new_cmd + '\r'
            new_cmd = new_cmd.encode('utf-8')
            ser.write(new_cmd)
            print(new_cmd)
            wait_complete()
        except Exception:
            pass
    fileProcess = False


point_a, point_b = None, None
calibration_complete = False
middle_pressed = False  # Track if the middle mouse button is pressed


def calc_dist_simple(x, y, cap):
    global point_a, point_b
    frame_width = int(cap.get(3))  # Width of the captured frame
    frame_height = int(cap.get(4))  # Height of the captured frame
    if point_a is not None:
        # Calculate the distance from point A to the clicked point (point_b)
        dx = x - point_a[0]
        dy = y - point_a[1]

        # Calculate the distances in mm using point B as the maximum
        distance_x_mm = (dx / frame_width) * max_distance_mm
        distance_y_mm = (dy / frame_height) * max_distance_mm
        # invert y
        distance_y_mm = abs(distance_y_mm)

        print(f"Distance from object point to point A (X): {distance_x_mm:.2f} mm")
        print(f"Distance from object point to point A (Y): {distance_y_mm:.2f} mm")
        # if distance_y_mm > 70:
        #     gcode = f'G0 Y{distance_y_mm} E{distance_x_mm * 1.7}\r'
        # else:
        #     gcode = f'G0 Y70 E{distance_x_mm * 1.7}\r'  # Use G0 for rapid positioning
        return distance_x_mm, distance_y_mm

# Create a function to calculate the distance
def calculate_distance(event, x, y, flags, param, cap):
    global point_a, point_b, middle_pressed
    frame_width = int(cap.get(3))  # Width of the captured frame
    frame_height = int(cap.get(4))  # Height of the captured frame
    
    if event == cv2.EVENT_MBUTTONDOWN:
        print("mid button pressed")
        middle_pressed = True
    if event == cv2.EVENT_MBUTTONUP:
        print("mid button released")
        middle_pressed = False
    if event == cv2.EVENT_LBUTTONDOWN:
        if point_a is not None:
            # Calculate the distance from point A to the clicked point (point_b)
            dx = x - point_a[0]
            dy = y - point_a[1]

            # Calculate the distances in mm using point B as the maximum
            distance_x_mm = (dx / frame_width) * max_distance_mm
            distance_y_mm = (dy / frame_height) * max_distance_mm
            # invert y
            distance_y_mm = abs(distance_y_mm)

            print(f"Distance from clicked point to point A (X): {distance_x_mm:.2f} mm")
            print(f"Distance from clicked point to point A (Y): {distance_y_mm:.2f} mm")
            if distance_y_mm > 70:
                gcode = f'G0 Y{distance_y_mm} E{distance_x_mm * 1.7}\r'
            else:
                gcode = f'G0 Y70 E{distance_x_mm * (distance_x_mm * 0.2)}\r'  # Use G0 for rapid positioning

            gcode = gcode.encode('utf-8')
            ser.write(gcode)
            wait_complete()
# Initialize a variable to keep track of the last time the function was called
last_call_time = time.time()
def draw_circle(radius, num_segments=100, axis='x'):
    radius = int(radius)
    num_segments = int(num_segments)

    global last_coords
    registration_point = last_coords

    # Move to the starting position
    gcode = f'G0 X{registration_point[0]} Y{registration_point[1]} Z{registration_point[2]} E{registration_point[3]}\r'
    gcode = gcode.encode('utf-8')
    ser.write(gcode)
    wait_complete()

    # Draw the circle based on the specified axis
    for i in range(num_segments):
        angle = 2 * math.pi * i / num_segments
        if axis == 'x':
            x = registration_point[0] + radius * math.cos(angle)
            y = registration_point[1] + radius * math.sin(angle)
        

        gcode = f'G0 E{x} Y{y}\r'
        gcode = gcode.encode('utf-8')
        ser.write(gcode)
        wait_complete()

    # Move back to the starting position
    gcode = f'G0 X{registration_point[0]} Y{registration_point[1]} Z{registration_point[2]} E{registration_point[3]}\r'
    gcode = gcode.encode('utf-8')
    ser.write(gcode)
    wait_complete()

def draw_square(_w, _h, _a):
    global last_coords
    registration_point = last_coords
    # Move to the starting position
    gcode = f'G0 X{registration_point[0]} Y{registration_point[1]} Z{registration_point[2]} E{registration_point[3]}\r'
    gcode = gcode.encode('utf-8')
    ser.write(gcode)
    wait_complete()
    if _a == 'x':
        # Move to the first corner (pos1)
        gcode = f'G0 Z{registration_point[2] - float(_h)}\r'
        gcode = gcode.encode('utf-8')
        ser.write(gcode)
        wait_complete()

        # Move to the second corner (pos2)
        gcode = f'G0 Z{registration_point[2] - float(_h)} E{registration_point[3] + float(_w)}\r'
        gcode = gcode.encode('utf-8')
        ser.write(gcode)
        wait_complete()

        # Move to the third corner (pos3)
        gcode = f'G0 Z{registration_point[2]} E{registration_point[3] + float(_w)}\r'
        gcode = gcode.encode('utf-8')
        ser.write(gcode)
        wait_complete()
    if _a == 'y':
        # Move to the first corner (pos1)
        gcode = f'G0 Y{registration_point[1] - float(_h)}\r'
        gcode = gcode.encode('utf-8')
        ser.write(gcode)
        wait_complete()

        # Move to the second corner (pos2)
        gcode = f'G0 Y{registration_point[1] - float(_h)} E{registration_point[3] + float(_w)}\r'
        gcode = gcode.encode('utf-8')
        ser.write(gcode)
        wait_complete()

        # Move to the third corner (pos3)
        gcode = f'G0 Y{registration_point[1]} E{registration_point[3] + float(_w)}\r'
        gcode = gcode.encode('utf-8')
        ser.write(gcode)
        wait_complete()
    if _a == 'z':
        # Move to the first corner (pos1)
        gcode = f'G0 Z{registration_point[2] - float(_h)}\r'
        gcode = gcode.encode('utf-8')
        ser.write(gcode)
        wait_complete()

        # Move to the second corner (pos2)
        gcode = f'G0 Z{registration_point[2] - float(_h)} Y{registration_point[1] + float(_w)}\r'
        gcode = gcode.encode('utf-8')
        ser.write(gcode)
        wait_complete()

        # Move to the third corner (pos3)
        gcode = f'G0 Z{registration_point[2]} Y{registration_point[1] + float(_w)}\r'
        gcode = gcode.encode('utf-8')
        ser.write(gcode)
        wait_complete()
    # Move back to the starting position
    gcode = f'G0 X{registration_point[0]} Y{registration_point[1]} Z{registration_point[2]} E{registration_point[3]}\r'
    gcode = gcode.encode('utf-8')
    ser.write(gcode)
    wait_complete()

def follow_color():
    global point_a, point_b, last_call_time
    print("here we go...")
    # Initialize webcam capture (0 is usually the default camera)
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    calibrated = None
    # Check if enough time has passed since the last function call
    
    if not point_a and not point_b:
        calibrated = False
        # Create a window and set the mouse callback for calibration
        cv2.namedWindow('Main Program')
        res = cv2.setMouseCallback('Main Program', calibrate)

        print("Calibration: Click on the webcam feed to set Point A and Point B coordinates.")

        while True:
            # Read a frame from the webcam
            ret, frame = cap.read()
            current_time = time.time()
            completed = False
            if point_a and point_b:
                
                if current_time - last_call_time >= 1 and not completed:
                    ret, frame = cap.read()
                    # Convert the frame to HSV color space
                    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                    # Define the lower and upper bounds for yellow in HSV
                    lower_yellow = np.array([3, 145, 145])  # Lower bound for yellow in HSV
                    upper_yellow = np.array([40, 255, 255])  # Upper bound for yellow in HSV
                    lower_red = np.array([0, 100, 100])  # Lower bound for red in HSV
                    upper_red = np.array([10, 255, 255])  # Upper bound for red in HSV
                    # Define the lower and upper bounds for green in HSV
                    lower_green = np.array([1, 12, 74])      # Lower bound for green in HSV
                    upper_green = np.array([80, 255, 130])    # Upper bound for green in HSV
                    # Create a mask that selects pixels within the specified yellow color range
                    mask = cv2.inRange(hsv_frame, lower_yellow, upper_yellow)

                    # Find contours in the mask
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    contours = [contour for contour in contours if cv2.contourArea(contour) >= 1000 and cv2.contourArea(contour)]
                    # Initialize a list to store the coordinates of yellow objects
                    yellow_object_coordinates = []
                    # Initialize a list to store the simplified contours of yellow objects
                    simplified_contours = []
                    # Iterate through the detected contours
                    for contour in contours:
                        # Simplify the contour to have 4 points using Douglas-Peucker algorithm
                        epsilon = 0.03 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        # Calculate the centroid (x, y) of each contour
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                            yellow_object_coordinates.append((cX, cY))

                    # Print the coordinates of yellow objects
                    for i, (x, y) in enumerate(yellow_object_coordinates):
                        print(f"object {i + 1}: X = {x}, Y = {y} - {cv2.contourArea(contour)}")
                        tx, yx = calc_dist_simple(x, y, cap=cap)
                        tx = tx * 1.6
                        gcode = f'G0 E{tx}Y{yx*1.6 + (33*2)}Z0\r'
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()

                        gcode = f'M5\r'
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()

                        gcode = f'G0 Z-85\r'
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()

                        gcode = f'M3\r'
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()

                        gcode = f'G0Z100\r'
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()
                        gcode = f'G0E300X0Y200\r'
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()
                        gcode = f'G0E300X0Z0Y200\r'
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()

                        gcode = f'M5\r'
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()

                        gcode = f'G0X0Z100Y100\r'
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()
                        completed = True
                    gcode = f'G0X0E0\r'
                    gcode = gcode.encode('utf-8')
                    ser.write(gcode)
                    wait_complete()
                    time.sleep(2)

                    # Draw the contours on the frame
                    
                    cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
                    cv2.circle(frame, point_a, 5, (255, 255, 255), -1)
                    cv2.circle(frame, point_b, 5, (255, 255, 255), -1)
                    frame = cv2.line(frame, point_a, point_b, (255, 255, 255), 1)
                    frame = cv2.putText(frame, 'Start', point_a, cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (255,255,255), 1, cv2.LINE_AA)
                    # Update the last call time
                    last_call_time = current_time
                     # Display the frame
                    cv2.imshow('Main Program', frame)

            else:
                cv2.namedWindow('Main Program')
                cv2.setMouseCallback('Main Program', calibrate)
                # Calibration phase: Draw a circle at Point A and Point B if they are set during calibration
                if point_a is not None:
                    cv2.circle(frame, point_a, 5, (0, 0, 255), -1)
                if point_b is not None:
                    cv2.circle(frame, point_b, 5, (0, 255, 0), -1)
            
            # Display the frame
            cv2.imshow('Main Program', frame)

            # Break the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            

    # Release the webcam and close the OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

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
    if point_a and point_b:
        print('Thank you')
        print('Completed calibration')
        return True
    else:
        return False
        

def computer_vision():
    global point_a, point_b
    print("here we go...")
    # Initialize webcam capture (0 is usually the default camera)
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    calibrated = None

    if not point_a and not point_b:
        calibrated = False
        # Create a window and set the mouse callback for calibration
        cv2.namedWindow('Main Program')
        res = cv2.setMouseCallback('Main Program', calibrate)

        print("Calibration: Click on the webcam feed to set Point A and Point B coordinates.")
        
        while True:
            # Read a frame from the webcam
            ret, frame = cap.read()
            

            if point_a and point_b:
                # Create a partial function with the calculate_distance function and pass the 'frame' variable
                calculate_distance_partial = partial(calculate_distance, cap=None)
                cv2.circle(frame, point_a, 5, (0, 0, 255), -1)
                cv2.circle(frame, point_b, 5, (0, 255, 0), -1)
                frame = cv2.line(frame, point_a, point_b, (0, 0, 255), 1)
                frame = cv2.putText(frame, 'Start', point_a, cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (255,255,255), 1, cv2.LINE_AA)
   
                # Update the 'frame' parameter in the partial function
                calculate_distance_partial.keywords['cap'] = cap
                # Set the mouse callback with the partial function
                cv2.setMouseCallback('Main Program', calculate_distance_partial)
                #break
            else:
                cv2.namedWindow('Main Program')
                cv2.setMouseCallback('Main Program', calibrate)
                # Calibration phase: Draw a circle at Point A and Point B if they are set during calibration
                if point_a is not None:
                    cv2.circle(frame, point_a, 5, (0, 0, 255), -1)
                if point_b is not None:
                    cv2.circle(frame, point_b, 5, (0, 255, 0), -1)
            
            # Display the frame
            cv2.imshow('Main Program', frame)

            # Break the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        

    # Release the webcam and close the OpenCV windows
    cap.release()
    cv2.destroyAllWindows()


def joypad_control():
    # Initialize Pygame
    pygame.init()

    # Initialize the joystick module
    pygame.joystick.init()

    # Check if there are any available joysticks/controllers
    if pygame.joystick.get_count() == 0:
        print("No controllers found.")
        return

    # Initialize the first joystick
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    joypad_on = True
    gstate = False
    speed = 2

    prev_key = None
    same_key_pressed_count = 0

    gcode = f'M205 S0\r'  # Use G0 for rapid positioning
    gcode = gcode.encode('utf-8')
    ser.write(gcode)
    wait_complete()
    while joypad_on:
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    joypad_on = False
                
            
            # Check for controller input
            for i in range(joystick.get_numbuttons()):
                button_state = joystick.get_button(i)
                current_key = i
                if button_state:
                    print(f"Button {i} is pressed")
                    
                    # speed control
                    
                    if current_key == prev_key:
                        same_key_pressed_count += 1
                    else:
                        same_key_pressed_count = 0
                    
                    if same_key_pressed_count > 5:
                        speed = 10
                    elif same_key_pressed_count > 10:
                        speed = 20
                    else:
                        speed = 2
                    
                    # end

                    if i == 6:
                        joypad_on = False
                    # R1 = E left
                    if i == 4:

                        e_pos = last_coords[3]
                        gcode = f'G0 E{e_pos + speed}\r'  # Use G0 for rapid positioning
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()
                        prev_key = current_key

                    if i == 5:
                        e_pos = last_coords[3]
                        gcode = f'G0 E{e_pos - speed}\r'  # Use G0 for rapid positioning
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()
                        prev_key = current_key

                    # X button = gripper
                    if i == 0:
                        if gstate:
                            gcode = f'M5\r'  # Use G0 for rapid positioning
                            gcode = gcode.encode('utf-8')
                            ser.write(gcode)
                            wait_complete()
                            gstate = False
                        else:
                            gcode = f'M3\r'  # Use G0 for rapid positioning
                            gcode = gcode.encode('utf-8')
                            ser.write(gcode)
                            wait_complete()
                            gstate = True
                    
                    # Check for hat button events
                if event.type == pygame.JOYHATMOTION:
                    hat_x, hat_y = joystick.get_hat(0)
                    if hat_x == 1:
                        print("Right button pressed")
                        x_pos = last_coords[0]
                        gcode = f'G0 X{x_pos + speed}\r'  # Use G0 for rapid positioning
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()
                        prev_key = current_key
                    elif hat_x == -1:
                        print("Left button pressed")
                        x_pos = last_coords[0]
                        gcode = f'G0 X{x_pos - speed}\r'  # Use G0 for rapid positioning
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()
                        prev_key = current_key
                    elif hat_y == 1:
                        print("Up button pressed")
                        y_pos = last_coords[2]
                        gcode = f'G0 Z{y_pos + speed}\r'  # Use G0 for rapid positioning
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()
                        prev_key = current_key
                    elif hat_y == -1:
                        print("Down button pressed")
                        y_pos = last_coords[2]
                        gcode = f'G0 Z{y_pos - speed}\r'  # Use G0 for rapid positioning
                        gcode = gcode.encode('utf-8')
                        ser.write(gcode)
                        wait_complete()
                        prev_key = current_key

            pygame.time.delay(50)  # Add a small delay to reduce CPU usage

    gcode = f'M205 S2\r'  # Use G0 for rapid positioning
    gcode = gcode.encode('utf-8')
    ser.write(gcode)
    wait_complete()
    # Quit Pygame
    pygame.quit()
    print()


if __name__ == '__main__':
    # total arguments
    n = len(sys.argv)
    
    max_distance_mm = 300

    try:
        fileProcess = sys.argv[2]
    except:
        print()
        
    ser = serial.Serial(sys.argv[1],baud,timeout=timeout)
    time.sleep(5)

    while True:
        print_cmds()
        print()
        new_cmd = input('CMD: ')
        if "control" in new_cmd:
            joypad_control()
        if "circle" in new_cmd:
            new_cmd = new_cmd.split(' ')
            draw_circle(new_cmd[1], new_cmd[2], new_cmd[3])
        if "square" in new_cmd:
            new_cmd = new_cmd.split(' ')
            draw_square(new_cmd[1], new_cmd[2], new_cmd[3])
        if "save" in new_cmd:
            prevCmdList.append(lastCmd)
            print("saved")
        if "export" in new_cmd:
            filename = new_cmd.split(' ')[1]
            file = open(filename,'w')
            for cmd in prevCmdList:
                file.write(cmd +"\n")
            file.close()
            print(f"saved {filename}")
        if "load" in new_cmd:
            prevCmdList = []
            filename = new_cmd.split(' ')[1]
            file1 = open(filename, 'r')
            Lines = file1.readlines()
            # Strips the newline character
            count = 0
            for line in Lines:
                count += 1
                prevCmdList.append(line + '\r\n')
            print('commands loaded, you can play')
        if "list" in new_cmd:
            print(prevCmdList)
        if "clear" in new_cmd:
            prevCmdList = []
        if "play" in new_cmd:
            count = 0
            for command in prevCmdList:
                count += 1
                # command = command.strip()
                ser.write(bytes(command, 'utf-8'))
                print(command)
                wait_complete()
        if "vision" in new_cmd:
            count = 0
            computer_vision()
        if "color" in new_cmd:
            count = 0
            follow_color()
        new_cmd = f'{new_cmd}\r'
        new_cmd = new_cmd.encode()
        ser.write(new_cmd)
        print(new_cmd)
        wait_complete()
        lastCmd = new_cmd.decode('utf-8')
        print('complete.')
            
