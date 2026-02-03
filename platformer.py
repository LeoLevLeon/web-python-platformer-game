print("пайтон запущен")
import pygame
import asyncio

async def main():
    # 1. Инициализация (СТРОГО ВНУТРИ main)
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Тест системы")

    # 2. Загрузка (ТОЛЬКО ПОСЛЕ set_mode)
    # Используем один из твоих файлов из pyscript.json
    try:
        player_img = pygame.image.load("assets/images/player_sprite.png").convert_alpha()
        # Попробуем загрузить звук (если браузер не заблокирует автоплей)
        test_sound = pygame.mixer.Sound("assets/sounds/moneta.mp3")
        print("Ресурсы загружены!")
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        # Если не найдет файл, создадим просто квадрат, чтобы игра не упала
        player_img = pygame.Surface((50, 50))
        player_img.fill((255, 0, 0))

    x, y = 100, 100
    
    # 3. Упрощенный цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Воспроизводим звук при клике (браузеры любят, когда звук идет после клика)
            if event.type == pygame.MOUSEBUTTONDOWN:
                test_sound.play()

        # Двигаем картинку для проверки анимации
        x = (x + 2) % 800

        screen.fill((30, 30, 30)) # Темно-серый фон
        screen.blit(player_img, (x, y))
        
        pygame.display.flip()
        
        # КРИТИЧЕСКИ ВАЖНО
        await asyncio.sleep(0)
    


