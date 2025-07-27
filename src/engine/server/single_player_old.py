import pygame

# 1. Initialize Pygame
pygame.init()

# 2. Set up the display window
win_width = 500
win_height = 500
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Single Player Game")

# 3. Player properties
x = 50
y = 50
width = 40
height = 60
vel = 5
color = (255, 0, 0) # Red

# 4. Main game loop
run = True
while run:
    pygame.time.delay(10) # A small delay to control the game speed

    # Check for events, like closing the window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Check for key presses to move the player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and x > 0:
        x -= vel
    if keys[pygame.K_RIGHT] and x < win_width - width:
        x += vel
    if keys[pygame.K_UP] and y > 0:
        y -= vel
    if keys[pygame.K_DOWN] and y < win_height - height:
        y += vel

    # 5. Drawing phase
    win.fill((255, 255, 255)) # Fill the window with white
    pygame.draw.rect(win, color, (x, y, width, height)) # Draw the player
    pygame.display.update() # Update the screen to show what we've drawn

pygame.quit()