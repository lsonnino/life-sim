import pygame
from time import sleep

from src.constants import NAME, VERSION, WIN_SIZE, FPS
from src.constants import BACKGROUND_COLOR
from src.game import Game

###############################
#    INITIALIZATION
###############################

# Initialize PyGame
pygame.init()

# Creating the window
window = pygame.display.set_mode(WIN_SIZE)
window.fill(BACKGROUND_COLOR)

# Setting the window name
pygame.display.set_caption(NAME + " - " + VERSION)

# Setting up the clock
clock = pygame.time.Clock()


###############################
#    GAME LOOP
###############################

running = True
game = Game(window)

while running:
    # Check events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Quitting")
            running = False
            break

    # Check keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        print("Quitting")
        running = False
        break
    elif keys[pygame.K_SPACE]:
        print("Game pause")
        sleep(0.2)
        continue

    #
    # Run the game
    #

    game.draw()

    #
    #
    #

    # Refresh the window
    pygame.display.flip()
    # Clock tick
    clock.tick(FPS)

pygame.quit()
