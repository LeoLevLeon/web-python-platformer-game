print("PYTHON СТАРТОВАЛ!") # Отладка
import os
print("Список файлов в системе:", os.listdir("."))
if os.path.exists("assets"):
    print("Содержимое assets:", os.listdir("assets"))
print(f"Пытаюсь найти: {os.path.abspath('assets/images/spike_sprite_2.png')}")
print(f"Файл существует? {os.path.exists('assets/images/spike_sprite_2.png')}")

import pygame
import random
import webbrowser
import asyncio

IS_WEB = True

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Константы-параметры окна
WIDTH = 800
HEIGHT = 600
FPS = 60

# Глобальные переменные уровня
current_level = 0
max_level = 5
game_started = False
game_completed = False
fullscreen = False
score = 0
number_of_button = 0
sound_play = True

def load_asset(path, fallback_color=(255, 0, 255)): # Яркий розовый — цвет ошибки
    if path.endswith('.png'):
        return pygame.image.load(path).convert_alpha()
    elif path.endswith(('.mp3', '.wav')):
        return pygame.mixer.Sound(path)
   

# Класс для игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        #создание изображения для спрайта
        self.image = load_asset("assets/images/player_sprite.png")   
        #создание хитбокса для спрайта
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        #компоненты скорости по оси X и Y
        self.x_velocity = 0
        self.y_velocity = 0

        #переменная-флаг для отслеживания в прыжке ли спрайт
        self.on_ground = False

    def update(self):
        # Обновление позиции игрока  
        self.rect.x += self.x_velocity
        self.rect.y += self.y_velocity
        # Ограничение выхода за границы экрана
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True
        if self.rect.top < 0:
            self.rect.top = 0

#класс для кнопки
class Button():
    def __init__(self, x, y, color_1 , color_2, text = ''):
        super().__init__()
        
        self.normal_color = str(color_1)
        self.hover_color = str(color_2)
        self.text_color = (225, 225, 225)

        self.rect = pygame.Rect(x, y, 150, 100)
        self.text = text
        self.font = pygame.font.SysFont(None, 24)
        self.is_hovered = False

    def draw_button(self, surface):
        if self.is_hovered:
            color = self.hover_color
        else:
            color = self.normal_color


        pygame.draw.rect(surface, color, self.rect)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center = self.rect.center)

        surface.blit(text_surf, text_rect)
    
    def is_over(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, mouse_pos):
        self.is_hovered = self.is_over(mouse_pos)

     
# Класс для патрулирующих врагов
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, _way_):
        super().__init__()

        #создание изображения для спрайта
        self.image = load_asset("assets/images/saw_sprite.png")  

        #начальная позиция по Х, нужна для патрулирования
        self.x_start = x
        #выбор направления начального движения
        self.direction = _way_ // _way_

        #создание хитбокса для спрайта
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self._way_ = _way_
        #компоненты скорости по оси Х и Y
        self.x_velocity = 1
        self.y_velocity = 0
    
    def update(self):
        # Если расстояние от начальной точки превысило _way_
        if abs(self.x_start - self.rect.x) > self._way_:
            self.direction *= -1
        
        # Движение спрайта по оси Х
        self.rect.x += self.x_velocity * self.direction
        
        # Ограничение выхода за границы экрана
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.direction *= -1
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction *= -1
# Класс для шипов
class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        #создание изображения для спрайта
        self.image = load_asset("assets/images/spike_sprite_2.png")
          

        #создание хитбокса для спрайта
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Класс для поднимаемых предметов
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        #создание изображения для спрайта
        self.image = load_asset("assets/images/coin_sprite.png")  

        #создание хитбокса для спрайта
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Класс для платформы
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, wight, height):
        super().__init__()
        #создание изображения дл я спрайта
        self.image = pygame.Surface((wight, height))
        self.image.fill("#e152f2")

        pygame.draw.rect(self.image, "#ae20c8", (0, 0, wight, height), width=3)

        #создание хитбокса для спрайта
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y         
    def draw(self, screen):
        screen.blit(self.image, self.rect)
# Функция для проверки коллизий с платформой
def check_collision_platforms(player, platforms):
    # Проверяем все коллизии
    for platform in platforms:
        if pygame.sprite.collide_rect(player, platform):
            # Определяем направление коллизии
            dx = player.rect.centerx - platform.rect.centerx
            dy = player.rect.centery - platform.rect.centery
            
            # Вычисляем перекрытие по осям
            overlap_x = min(player.rect.right, platform.rect.right) - max(player.rect.left, platform.rect.left)
            overlap_y = min(player.rect.bottom, platform.rect.bottom) - max(player.rect.top, platform.rect.top)
            
            # Решаем коллизию по оси с меньшим перекрытием
            if overlap_x < overlap_y:
                # Горизонтальная коллизия
                if dx > 0:  # Игрок справа от платформы
                    player.rect.left = platform.rect.right
                    player.x_velocity = 0
                else:  # Игрок слева от платформы
                    player.rect.right = platform.rect.left
                    player.x_velocity = 0
            else:
                # Вертикальная коллизия
                if dy > 0:  # Игрок НИЖЕ центра платформы (падает ВНИЗ)
                    player.rect.top = platform.rect.bottom  # Исправлено!
                    player.y_velocity = 0
                else:  # Игрок ВЫШЕ центра платформы (прыгает ВВЕРХ)
                    player.rect.bottom = platform.rect.top  # Исправлено!
                    player.y_velocity = 0
                    player.on_ground = True
                
                    player.on_groung = False

# Функция проверки коллизии выбранного объекта с объектами Enemies
def check_collision_enemies(player, enemies_list):
    for enemy in enemies_list:
        if player.rect.colliderect(enemy.rect):
            death_sound.play()
            # При столкновении с врагом возвращаем игрока на старт
            player.rect.x = player_start_positions[current_level][0]
            player.rect.y = player_start_positions[current_level][1]
            player.x_velocity = 0
            player.y_velocity = 0
            return True
    for spike in enemies_list:
        if player.rect.colliderect(spike.rect):
            death_sound.play()
            # При столкновении с врагом возвращаем игрока на старт
            player.rect.x = player_start_positions[current_level][0]
            player.rect.y = player_start_positions[current_level][1]
            player.x_velocity = 0
            player.y_velocity = 0
            return True
    return False
        
# Функция проверки коллизии с собираемыми предметами
def check_collision_collectibles(player, collectibles_list):
    global score
    collected = False
    
    for collectible in collectibles_list[:]:
        if player.rect.colliderect(collectible.rect):
            coin_sound.play()
            # Убираем этот объект из всех групп
            collectible.kill()
            # Убираем этот объект из списка
            collectibles_list.remove(collectible)
            # Прибавляем одно очко
            score += 1
            collected = True
    
    return collected


  
# Функция проверки завершения уровня
def check_level_completion():
    global current_level, game_completed
    
    # Уровень завершен, когда собраны все предметы
    if len(collectibles_list) == 0:
        if current_level < max_level:
            current_level += 1
            win_sound.play()
            load_level(current_level)
        else:
            game_completed = True

levels_platforms = {
    1: [Platform(50, 450, 125, 50), Platform(250, 450, 125, 50), Platform(475, 400, 125, 50)],
    2: [Platform(600, 475, 125, 50), Platform(325, 475, 125, 50), Platform(50, 475, 125, 50), Platform(0, 400, 75, 50), Platform(200, 325, 125, 50), Platform(375, 300, 50, 50), Platform(475, 325, 125, 50), Platform(650, 250, 75, 50), Platform(475, 175, 75, 50), Platform(200, 125, 175, 50), Platform(50, 225, 25, 50), Platform(110, 225, 25, 50)],    
    3: [Platform(50, 500, 125, 50), Platform(300, 500, 125, 50), Platform(500, 500, 25, 100), Platform(600, 500, 125, 50), Platform(750, 450, 50, 50), Platform(650, 375, 50, 50), Platform(750, 300, 50, 50), Platform(650, 225, 50, 50), Platform(750, 150, 50, 50), Platform(650, 75, 50, 50), Platform(625, 75, 25, 350), Platform(0, 350, 625, 25), Platform(475, 0, 25, 225), Platform(0, 225, 100, 25), Platform(150, 175, 100, 25), Platform(0, 225, 100, 25), Platform(25, 50, 200, 25), Platform(300, 125, 100, 25), Platform(125, 275, 100, 25)],
    4: [Platform(675, 100, 150, 25), Platform(175, 75, 450, 50), Platform(50, 250, 150, 25 ), Platform(225, 200, 50, 50), Platform(350, 200, 150, 50), Platform(575, 200, 250, 50), Platform(675, 250, 25, 175), Platform(250, 375, 425, 50), Platform(0, 425, 100, 50), Platform(175, 450, 50, 50), Platform(250, 525, 475, 50), Platform(775, 475, 25, 75), Platform(700, 400, 25, 75), Platform(775, 325, 25, 75, ), Platform(700, 300, 50, 25)],
    5: [Platform(175, 75, 575, 25), Platform(75, 125, 25, 25),Platform(0, 200, 50, 50), Platform(75, 275, 50, 50), Platform(175, 350, 50, 50), Platform(125, 425, 400, 50), Platform(250, 150, 50, 75), Platform(425, 150, 50, 75), Platform(425, 250, 100, 25), Platform(575, 275, 50, 50), Platform(675, 350, 50, 50), Platform(575, 400, 50, 50), Platform(775, 150, 25, 50), Platform(625, 150, 25, 25)]
}


levels_enemies = {
    1: [Spike(300, 425), Spike(0, 575), Spike(50, 575), Spike(100, 575), Spike(150, 575), Spike(200, 575), Spike(250, 575), Spike(300, 575), Spike(350, 575), Spike(400, 575), Spike(450, 575), Spike(500, 575), Spike(550, 575), Spike(600, 575), Spike(650, 575), Spike(700, 575), Spike(750, 575)],
    2: [Spike(375, 275),Spike(400, 275), Spike(50, 200), Spike(110, 200), Enemy(525, 300, 62.5), Spike(0, 575), Spike(50, 575), Spike(100, 575), Spike(150, 575), Spike(200, 575), Spike(250, 575), Spike(300, 575), Spike(350, 575), Spike(400, 575), Spike(450, 575), Spike(500, 575), Spike(550, 575), Spike(600, 575), Spike(650, 575), Spike(700, 575), Spike(750, 575)],
    3: [Spike(500, 475), Spike(575, 325), Spike(600, 325), Enemy(550, 150, 50), Enemy(550, 100, 50), Enemy(100, 325, 100), Enemy(225, 325, 100), Spike(0, 575), Spike(50, 575), Spike(100, 575), Spike(150, 575), Spike(200, 575), Spike(250, 575), Spike(300, 575), Spike(350, 575), Spike(400, 575), Spike(450, 575), Spike(500, 575), Spike(550, 575), Spike(600, 575), Spike(650, 575), Spike(700, 575), Spike(750, 575)],
    4: [Spike(450, 50), Spike(325, 50), Spike(125, 225), Spike(400, 175), Spike(475, 175), Spike(350, 350), Spike(0, 400), Spike(75, 400), Spike(375, 500), Spike(500, 500), Spike(700, 275), Spike(575, 175), Spike(625, 175), Spike(675, 175), Spike(725, 175), Spike(775, 175), Enemy(425, 350, 50), Enemy(300, 500, 50), Enemy(600, 500, 50), Spike(0, 575), Spike(50, 575), Spike(100, 575), Spike(150, 575), Spike(200, 575), Spike(250, 575), Spike(300, 575), Spike(350, 575), Spike(400, 575), Spike(450, 575), Spike(500, 575), Spike(550, 575), Spike(600, 575), Spike(650, 575), Spike(700, 575), Spike(750, 575)],
    5: [Spike(275, 50), Spike(700, 50), Spike(0, 175), Spike(375, 400), Spike(700, 325), Spike(475, 225), Spike(500, 225), Enemy(400, 50, 50), Enemy(525, 50, 50), Spike(0, 575), Spike(50, 575), Spike(100, 575), Spike(150, 575), Spike(200, 575), Spike(250, 575), Spike(300, 575), Spike(350, 575), Spike(400, 575), Spike(450, 575), Spike(500, 575), Spike(550, 575), Spike(600, 575), Spike(650, 575), Spike(700, 575), Spike(750, 575)]
}

levels_collectibles = {
    1: [Collectible(150, 425), Collectible(500, 375)],
    2: [Collectible(100, 450), Collectible(475, 150), Collectible(200, 100 ), Collectible(75, 250)],
    3: [Collectible(775, 425), Collectible(675, 50), Collectible(50, 325), Collectible(525, 325), Collectible(50, 25)],
    4: [Collectible(425, 175), Collectible(500, 350), Collectible(50, 400), Collectible(725, 275)],
    5: [Collectible(625, 125), Collectible(325, 50), Collectible(450, 225)]
}

# Начальные позиции игрока для каждого уровня
player_start_positions = {
    1: (75, 425),
    2: (675, 450),
    3: (100, 400),
    4: (750, 75),
    5: (250, 125)
}


# Функция загрузки уровня
def load_level(level):
    global platforms_list, enemies_list, collectibles_list, buttons_list, player_sprite
    
    # Загружаем объекты уровня
    platforms_list = levels_platforms[level][:]
    enemies_list = levels_enemies[level][:]
    collectibles_list = levels_collectibles[level][:]
    
    # Очищаем группы спрайтов
    player_sprite_group.empty()
    platforms.empty()
    enemies.empty()
    collectibles.empty()
    buttons_sprite_group.empty()
    
    # Создаем игрока
    player_sprite = Player(player_start_positions[level][0], player_start_positions[level][1])
    player_sprite_group.add(player_sprite)
    
    # Добавляем платформы
    for platform in platforms_list:
        platforms.add(platform)
    
    # Добавляем врагов
    for enemy in enemies_list:
        enemies.add(enemy)
    
    # Добавляем шипы    
    for spike in enemies_list:
        enemies.add(spike)
    
    # Добавляем собираемые предметы
    for collectible in collectibles_list:
        collectibles.add(collectible)
    # добавляем кнопки
    for button in buttons_list:
        buttons_sprite_group.add(button)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Платформер")
clock = pygame.time.Clock()

# Создаем шрифт для отображения счета и уровня
font = pygame.font.SysFont(None, 36)

button_1 = Button(325, 350, "#c84420", "#f27552", "Старт")
button_2 = Button(100, 350, "#2067c8", "#528af2", "Полный экран")
button_3 = Button(550, 350, "#30c820", "#52f25d", "Звук вкл/выкл")
# Создаем группы спрайтов
player_sprite_group = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
collectibles = pygame.sprite.Group()
buttons_sprite_group = pygame.sprite.Group()
# Переменные для хранения объектов уровня
platforms_list = []
enemies_list = []
collectibles_list = []
buttons_list = []
player_sprite = None


bg_1 = load_asset("assets/images/bg_1.png")
bg_2 = load_asset("assets/images/bg_2.png")
bg_3 = load_asset("assets/images/bg_3.png")
bg_4 = load_asset("assets/images/bg_4.png")
bg_5 = load_asset("assets/images/bg_5.png")
bg_6 = load_asset("assets/images/bg_6.png")
bg_7 = load_asset("assets/images/bg_7.png")

jump_sound = load_asset("assets/sounds/Jump_sound_1.mp3")
coin_sound = load_asset("assets/sounds/moneta.mp3")
death_sound = load_asset("assets/sounds/Hit_sound_3.mp3")
win_sound = load_asset("assets/sounds/New_level_sound.mp3")
button_sound = load_asset("assets/sounds/Push_button.mp3")
menu_music = load_asset("assets/sounds/Beep-beep_melody.mp3")
end_music = load_asset("assets/sounds/Game_end_song.mp3")
level_song_1 = load_asset("assets/sounds/Cool_song.mp3")
level_song_2 = load_asset("assets/sounds/Happ_song.mp3")
level_song_3 = load_asset("assets/sounds/Game_song.mp3")
level_song_4 = load_asset("assets/sounds/Fon_song.mp3")
level_song_5 = load_asset("assets/sounds/fon.mp3")

async def main():
    # Если ты используешь глобальные переменные, объяви их здесь в начале функции
    global running, game_started, current_level, score, button_1, button_2, button_3, screen, fullscreen, sound_play

    # Основной игровой цикл
    running = True
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_sprite.on_ground == True :
                    jump_sound.play()
                    player_sprite.y_velocity = -7
                    player_sprite.on_ground = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                
                if not game_started:

                    if button_1.is_over(pygame.mouse.get_pos()):
                        button_sound.play()
                        current_level += 1
                        load_level(current_level)
                        button_1 = None
                        button_2 = None
                        button_3 = None
                        game_started = True
                    
                    elif button_2.is_over(pygame.mouse.get_pos()):
                        button_sound.play()
                        if not fullscreen:
                            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN) 
                            fullscreen = True
                        else:
                            screen = pygame.display.set_mode((WIDTH, HEIGHT))
                            fullscreen = False
                    
                    elif button_3.is_over(pygame.mouse.get_pos()):
                        button_sound.play()
                        if not sound_play:
                            sound_play = True
                        else:
                            sound_play = False

                elif game_completed:
                    if button_4.is_over(pygame.mouse.get_pos()):
                        webbrowser.open("https://t.me/Infoplatformer_bot")



        if not sound_play:
            jump_sound.stop()
            coin_sound.stop()
            death_sound.stop()
            win_sound.stop()
            button_sound.stop()
            menu_music.stop()
            end_music.stop()
            level_song_1.stop()
            level_song_2.stop()
            level_song_3.stop()
            level_song_4.stop()
            level_song_5.stop()


        # Если игра завершена, показываем сообщение
        if game_completed:
            level_song_5.stop()
            end_music.play()
            screen.blit(bg_2, (0, 0))
            completion_text = font.render("Спасибо, что сыграли в нашу игру! :)", True, "black")
            score_text = font.render(f"Оставьте отзыв:", True, "blue")
            button_4 = Button(325, 375, "#2067c8", "#528af2", "Ссылка на бота")
            screen.blit(completion_text, (WIDTH//2 - completion_text.get_width()//2, HEIGHT//2 - 50))
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 10))
            button_4.update_hover(pygame.mouse.get_pos())
            button_4.draw_button(screen)
            pygame.display.flip()
            
            # Ждем нажатия клавиши для выхода
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False
            continue
        
        if not game_started:
            menu_music.play()
            screen.blit(bg_6, (0, 0))
            # Отображаем заголовок
            title_font = pygame.font.SysFont(None, 48)
            title_text = title_font.render("Tiny Green Cube", True, "green")
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
            title_text_ru = title_font.render("Крошечный зеленый кубик", True, "green")
            screen.blit(title_text_ru, (WIDTH//2 - title_text_ru.get_width()//2, 200))
            
            # Отображаем кнопки если они не None
            if button_1:
                button_1.update_hover(pygame.mouse.get_pos())
                button_1.draw_button(screen)
            if button_2:
                button_2.update_hover(pygame.mouse.get_pos())
                button_2.draw_button(screen)
            if button_3:
                button_3.update_hover(pygame.mouse.get_pos())
                button_3.draw_button(screen)
            
            # Отображаем подсказку
            hint_font = pygame.font.SysFont(None, 24)
            hint_text = hint_font.render("Игра создана в рамках проекта ко дню науки 2026", True, "black")
            screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT - 50))

            pygame.display.flip()
            clock.tick(FPS)
            continue
        else:
            menu_music.stop()

        # Управление
        keys = pygame.key.get_pressed()
        player_sprite.x_velocity = 0
        if keys[pygame.K_LEFT]:
            player_sprite.x_velocity = -5
        if keys[pygame.K_RIGHT]:
            player_sprite.x_velocity = 5
        
        # Гравитация
        player_sprite.y_velocity += 0.3
        
        # Обновление
        player_sprite.update()
        enemies.update()

        
        
        # Проверка коллизий
        check_collision_platforms(player_sprite, platforms_list)
        check_collision_enemies(player_sprite, enemies_list)
        check_collision_collectibles(player_sprite, collectibles_list)
        

        # Проверка завершения уровня
        check_level_completion()
        
        # Отрисовка
        if current_level == 1:
            level_song_1.play()
            screen.blit(bg_1, (0, 0))
        
        elif current_level == 2:
            level_song_1.stop()
            level_song_2.play()
            screen.blit(bg_3, (0, 0))
        
        elif current_level == 3:
            level_song_2.stop()
            level_song_3.play()
            screen.blit(bg_4, (0, 0))
        
        elif current_level == 4:
            level_song_3.stop()
            level_song_4.play()
            screen.blit(bg_5, (0, 0))
        
        elif current_level == 5:
            level_song_4.stop()
            level_song_5.play()
            screen.blit(bg_7, (0, 0))
        

        # Отрисовываем все спрайты
        platforms.draw(screen)
        enemies.draw(screen)
        collectibles.draw(screen)
        player_sprite_group.draw(screen)

        # Отображение счёта и уровня
        score_text = font.render(f"Счёт: {score}", True, "black")
        level_text = font.render(f"Уровень: {current_level}/{max_level}", True, "blue")
        
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))

        
        # Обновление экрана
        pygame.display.flip()
        
        # Установка частоты кадров
        clock.tick(FPS)

        await asyncio.sleep(0) 


asyncio.run(main())


pygame.quit()




