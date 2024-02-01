import pygame

def main():
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

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check for controller input
        for i in range(joystick.get_numbuttons()):
            button_state = joystick.get_button(i)
            if button_state:
                print(f"Button {i} is pressed")
                if i == 6:
                    running = False
        # Check for hat button events
        if event.type == pygame.JOYHATMOTION:
            hat_x, hat_y = joystick.get_hat(0)
            if hat_x == 1:
                print("Right button pressed")
            elif hat_x == -1:
                print("Left button pressed")
            elif hat_y == 1:
                print("Up button pressed")
            elif hat_y == -1:
                print("Down button pressed")

        pygame.time.delay(100)  # Add a small delay to reduce CPU usage

    # Quit Pygame
    pygame.quit()

if __name__ == "__main__":
    main()
