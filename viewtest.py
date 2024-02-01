import pygame
import math

# Initialize Pygame
pygame.init()

# Set up screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)

colors = [white, gray]

# Robot arm parameters
link_lengths = [120, 120]  # Lengths of each link
base_x = 20  # Base position (x-coordinate)
base_y = 20  # Base position (y-coordinate)

# Function to draw a single link
def draw_link(screen, start_x, start_y, length, angle):
    end_x = start_x + length * math.cos(angle)
    end_y = start_y + length * math.sin(angle)
    pygame.draw.line(screen, gray, (start_x, start_y), (end_x, end_y), 10)

def draw_arm(screen, angles):
    x = base_x
    y = screen_height - link_lengths[0]  # Start at the bottom of the screen
    for i, angle in enumerate(angles):
        draw_link(screen, x, y, link_lengths[i], angle)
        x, y = int(x + link_lengths[i] * math.cos(angle)), int(y + link_lengths[i] * math.sin(angle))
    # Draw a circle for the end effector
    pygame.draw.circle(screen, white, (x, y), 10)

# Function to calculate inverse kinematics
def inverse_kinematics(x, y, link_lengths):
    # Calculate the distance from the base to the target position
    d = math.sqrt(x**2 + y**2)

    # Check if the target position is within the arm's reach
    if d > sum(link_lengths):
        return None  # Target is unreachable

    # Calculate the angles for the first two joints using the law of cosines
    theta1 = math.atan2(y, x)
    c = (d**2 - link_lengths[0]**2 - link_lengths[1]**2) / (2 * link_lengths[0] * link_lengths[1])
    if abs(c) > 1:
        return None  # Unrealizable configuration
    theta2 = math.acos(c)

    # # Calculate the angle for the third joint (if applicable)
    # if len(link_lengths) > 2:
    #     theta3 = math.pi - math.atan2(y - link_lengths[0] * math.sin(theta1),
    #                                    x - link_lengths[0] * math.cos(theta1)) - theta2
    # else:
    #     theta3 = None

    return [theta1, theta2]  # Return the calculated angles

# Function to draw the arm using inverse kinematics
def draw_arm_with_ik(screen, end_x, end_y):
    angles = inverse_kinematics(end_x - base_x, end_y - base_y, link_lengths)
    if angles is not None:
        draw_arm(screen, angles)
    else:
        print("Target position is unreachable")

# Main loop
running = True
end_x, end_y = (174, 120)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get user input for endpoint coordinates (replace with your input method)
    # Draw the arm using inverse kinematics
    draw_arm_with_ik(screen, end_x, end_y)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()