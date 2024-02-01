import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
LINK1_LENGTH, LINK2_LENGTH = 120, 120
JOINT_RADIUS = 10
END_EFFECTOR_RADIUS = 15

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
# Font
font = pygame.font.Font(None, 36)
# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2-Link Robot Arm")

# Get the desired end effector position (replace these values as needed)
target_x, target_y = 174, 120

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the desired end effector position (replace these values as needed)
    target_y -= 0.01

    # Calculate joint angles using inverse kinematics
    theta2 = math.acos(
        (target_x ** 2 + target_y ** 2 - LINK1_LENGTH ** 2 - LINK2_LENGTH ** 2) /
        (2 * LINK1_LENGTH * LINK2_LENGTH)
    )
    theta1 = math.atan2(target_y, target_x) - math.atan2(
        (LINK2_LENGTH * math.sin(theta2)),
        (LINK1_LENGTH + LINK2_LENGTH * math.cos(theta2)),
    )

    # Clear the screen
    screen.fill(WHITE)

    # Draw the robot arm
    joint1_x, joint1_y = (
        int(SCREEN_WIDTH / 2),
        int(SCREEN_HEIGHT / 2),
    )
    joint2_x = joint1_x + LINK1_LENGTH * math.cos(theta1)
    joint2_y = joint1_y + LINK1_LENGTH * math.sin(theta1)
    end_effector_x = joint2_x + LINK2_LENGTH * math.cos(theta1 + theta2)
    end_effector_y = joint2_y + LINK2_LENGTH * math.sin(theta1 + theta2)

    pygame.draw.circle(screen, BLACK, (joint1_x, joint1_y), JOINT_RADIUS)
    pygame.draw.line(screen, BLACK, (joint1_x, joint1_y), (joint2_x, joint2_y), 5)
    pygame.draw.circle(screen, BLACK, (joint2_x, joint2_y), JOINT_RADIUS)
    pygame.draw.line(
        screen, BLACK, (joint2_x, joint2_y), (end_effector_x, end_effector_y), 5
    )
    pygame.draw.circle(screen, BLACK, (end_effector_x, end_effector_y), END_EFFECTOR_RADIUS)

    # Display x and y labels
    x_label = font.render(f'X: {end_effector_x}', True, BLACK)
    y_label = font.render(f'Y: {end_effector_y}', True, BLACK)
    screen.blit(x_label, (10, 10))
    screen.blit(y_label, (10, 50))
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()