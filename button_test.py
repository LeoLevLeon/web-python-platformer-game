import pygame 
import random

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode((400, 400))

button_surface = pygame.Surface((150, 50))
button_rect = pygame.Rect(125, 125, 150, 50)

button_surface_1 = pygame.Surface((150, 50))
button_rect_1 = pygame.Rect(125, 195, 150, 50)

screen.fill("white")

while True:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if button_rect.collidepoint(event.pos):
                print("красный")
                screen.fill("red")
            
            elif button_rect_1.collidepoint(event.pos):
                print("синий")
                screen.fill("blue")

    if button_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(button_surface, (127, 255, 212), (1, 1, 148, 48))

    elif button_rect_1.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(button_surface_1, (127, 255, 212), (1, 1, 148, 48))

    else:
        pygame.draw.rect(button_surface, (0, 0, 0), (0, 0, 150, 150))
        pygame.draw.rect(button_surface_1, (0, 0, 0), (0, 0, 150, 150))
        
    
    screen.blit(button_surface, (button_rect.x, button_rect.y))
    screen.blit(button_surface_1, (button_rect_1.x, button_rect_1.y))

    pygame.display.update()