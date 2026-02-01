import pygame
import asyncio
async def main():
    pygame.display.init()
    screen = pygame.display.set_mode((800, 600))
    while True:
        screen.fill("red")
        pygame.display.flip()
        await asyncio.sleep(0)

