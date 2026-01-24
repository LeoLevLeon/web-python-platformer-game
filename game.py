# Tiny Green Cube - PyScript версия
# Основной файл игры

import sys
import os
import time

print("=== ЗАГРУЗКА ИГРЫ TINY GREEN CUBE ===")

# Определяем среду выполнения
IN_PYSCRIPT = "pyscript" in sys.modules

# Конфигурация путей
if IN_PYSCRIPT:
    print("Запуск в PyScript")
    BASE_PATH = "./assets/"
else:
    print("Запуск на десктопе")
    BASE_PATH = "assets/"

# Пробуем импортировать pygame
try:
    import pygame
    PYGAME_AVAILABLE = True
    print(f"✅ Pygame загружен, версия: {pygame.version.ver}")
except ImportError as e:
    PYGAME_AVAILABLE = False
    print(f"❌ Pygame не доступен: {e}")
    print("Создаем заглушку для Pygame")

# Если Pygame не доступен, создаем заглушки
if not PYGAME_AVAILABLE:
    # Минимальная заглушка для Pygame
    class PygameStub:
        class Surface:
            def __init__(self, size):
                self.size = size
                self.width, self.height = size
            def fill(self, color): pass
            def get_rect(self): return self
            def blit(self, surf, pos): pass
            def get_width(self): return self.width
            def get_height(self): return self.height
        
        class Rect:
            def __init__(self, x, y, w, h):
                self.x = x
                self.y = y
                self.width = w
                self.height = h
                self.left = x
                self.right = x + w
                self.top = y
                self.bottom = y + h
            
            def colliderect(self, other):
                return (self.x < other.x + other.width and
                       self.x + self.width > other.x and
                       self.y < other.y + other.height and
                       self.y + self.height > other.y)
        
        @staticmethod
        def init(): print("Pygame инициализирован (заглушка)")
        @staticmethod
        def quit(): print("Pygame завершен")
        
        @staticmethod
        def display():
            class Display:
                @staticmethod
                def set_mode(size):
                    return PygameStub.Surface(size)
                @staticmethod
                def set_caption(caption): pass
                @staticmethod
                def flip(): pass
                @staticmethod
                def update(): pass
            return Display
        
        class font:
            @staticmethod
            def SysFont(name, size):
                class Font:
                    def render(self, text, antialias, color):
                        return PygameStub.Surface((len(text) * 10, size))
                return Font()
        
        class mouse:
            @staticmethod
            def get_pos():
                return (0, 0)
        
        class key:
            @staticmethod
            def get_pressed():
                class Pressed:
                    def __getitem__(self, key):
                        return False
                return Pressed()
        
        class event:
            @staticmethod
            def get():
                return []
            
            QUIT = pygame.QUIT if hasattr(pygame, 'QUIT') else 1
            KEYDOWN = pygame.KEYDOWN if hasattr(pygame, 'KEYDOWN') else 2
            KEYUP = pygame.KEYUP if hasattr(pygame, 'KEYUP') else 3
            MOUSEBUTTONDOWN = pygame.MOUSEBUTTONDOWN if hasattr(pygame, 'MOUSEBUTTONDOWN') else 4
            MOUSEBUTTONUP = pygame.MOUSEBUTTONUP if hasattr(pygame, 'MOUSEBUTTONUP') else 5
        
        class draw:
            @staticmethod
            def rect(surface, color, rect, width=0, border_radius=0):
                pass
            
            @staticmethod
            def circle(surface, color, center, radius):
                pass
            
            @staticmethod
            def polygon(surface, color, points):
                pass
            
            @staticmethod
            def line(surface, color, start_pos, end_pos, width=1):
                pass
    
    pygame = PygameStub()

# Инициализация Pygame
try:
    pygame.init()
    print("✅ Pygame инициализирован")
except Exception as e:
    print(f"⚠ Ошибка инициализации Pygame: {e}")

# Константы игры
WIDTH = 800
HEIGHT = 600
FPS = 60

# Глобальные переменные
current_level = 0
max_level = 5
game_started = False
game_completed = False
score = 0
sound_play = True
fullscreen = False

# Функции для загрузки ресурсов
def load_image(filename):
    """Загружает изображение с обработкой ошибок"""
    try:
        if IN_PYSCRIPT:
            # В PyScript используем прямой путь
            return pygame.image.load(BASE_PATH + "images/" + filename)
        else:
            return pygame.image.load(os.path.join(BASE_PATH, "images", filename))
    except Exception as e:
        print(f"⚠ Не удалось загрузить изображение {filename}: {e}")
        # Создаем цветную заглушку
        return create_color_surface(filename)

def create_color_surface(filename):
    """Создает цветную поверхность вместо изображения"""
    surface = pygame.Surface((50, 50))
    
    # Выбираем цвет по названию файла
    if "player" in filename:
        surface.fill((0, 255, 0))  # Зеленый для игрока
    elif "saw" in filename:
        surface.fill((255, 0, 0))  # Красный для пилы
    elif "coin" in filename:
        surface.fill((255, 255, 0))  # Желтый для монеты
    elif "spike" in filename:
        surface.fill((128, 128, 128))  # Серый для шипов
    elif "bg" in filename:
        # Градиентный фон
        for y in range(surface.get_height()):
            color_val = 100 + int(155 * y / surface.get_height())
            pygame.draw.line(surface, (color_val, color_val, 255), 
                           (0, y), (surface.get_width(), y))
    else:
        surface.fill((200, 200, 200))  # Серый для всего остального
    
    return surface

def load_sound(filename):
    """Загружает звук с обработкой ошибок"""
    try:
        if IN_PYSCRIPT:
            return pygame.mixer.Sound(BASE_PATH + "sounds/" + filename)
        else:
            return pygame.mixer.Sound(os.path.join(BASE_PATH, "sounds", filename))
    except Exception as e:
        print(f"⚠ Не удалось загрузить звук {filename}: {e}")
        # Создаем заглушку для звука
        class DummySound:
            def play(self): 
                print(f"[ЗВУК] Воспроизведение: {filename}")
            def stop(self): pass
            def set_volume(self, vol): pass
        return DummySound()

# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("bg_and_sprites/player_sprite.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x_velocity = 0
        self.y_velocity = 0
        self.on_ground = False
    
    def update(self):
        self.rect.x += self.x_velocity
        self.rect.y += self.y_velocity
        
        # Границы экрана
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True
        if self.rect.top < 0:
            self.rect.top = 0

# Класс врага (пила)
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_range):
        super().__init__()
        self.image = load_image("bg_and_sprites/saw_sprite.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x
        self.patrol_range = patrol_range
        self.direction = 1
        self.speed = 1
    
    def update(self):
        self.rect.x += self.speed * self.direction
        
        if abs(self.rect.x - self.start_x) > self.patrol_range:
            self.direction *= -1
        
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.direction = -1
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1

# Класс шипов
class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("bg_and_sprites/spike_sprite_2.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Класс монет
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("bg_and_sprites/coin_sprite.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Класс платформ
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((225, 82, 242))
        pygame.draw.rect(self.image, (174, 32, 200), (0, 0, width, height), 3)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Класс кнопок
class Button:
    def __init__(self, x, y, color1, color2, text):
        self.rect = pygame.Rect(x, y, 180, 120)
        self.color1 = color1
        self.color2 = color2
        self.text = text
        self.font = pygame.font.SysFont(None, 28)
        self.hovered = False
    
    def draw(self, screen):
        color = self.color2 if self.hovered else self.color1
        
        pygame.draw.rect(screen, color, self.rect, border_radius=20)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, width=3, border_radius=20)
        
        text_surf = self.font.render(self.text, True, (225, 225, 225))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def is_over(self, pos):
        return self.rect.collidepoint(pos)

# Загрузка ресурсов
print("Загрузка ресурсов...")
try:
    bg_1 = load_image("bg_and_sprites/bg_1.png")
    bg_2 = load_image("bg_and_sprites/bg_2.png")
    bg_3 = load_image("bg_and_sprites/bg_3.png")
    bg_4 = load_image("bg_and_sprites/bg_4.png")
    bg_5 = load_image("bg_and_sprites/bg_5.png")
    bg_6 = load_image("bg_and_sprites/bg_6.png")
    bg_7 = load_image("bg_and_sprites/bg_7.png")
    
    jump_sound = load_sound("sounds_and_music/Jump_sound_1.mp3")
    coin_sound = load_sound("sounds_and_music/moneta.mp3")
    death_sound = load_sound("sounds_and_music/Hit_sound_3.mp3")
    win_sound = load_sound("sounds_and_music/New_level_sound.mp3")
    button_sound = load_sound("sounds_and_music/Push_button.mp3")
    menu_music = load_sound("sounds_and_music/Beep-beep_melody.mp3")
    end_music = load_sound("sounds_and_music/Game_end_song.mp3")
    level_song_1 = load_sound("sounds_and_music/Cool_song.mp3")
    level_song_2 = load_sound("sounds_and_music/Happ_song.mp3")
    level_song_3 = load_sound("sounds_and_music/Game_song.mp3")
    level_song_4 = load_sound("sounds_and_music/Fon_song.mp3")
    level_song_5 = load_sound("sounds_and_music/fon.mp3")
    
    print("✅ Ресурсы загружены")
except Exception as e:
    print(f"⚠ Ошибка загрузки ресурсов: {e}")

# Определение уровней
levels_platforms = {
    1: [Platform(50, 450, 125, 50), Platform(250, 450, 125, 50), Platform(475, 400, 125, 50)],
    2: [Platform(600, 475, 125, 50), Platform(325, 475, 125, 50), Platform(50, 475, 125, 50), 
        Platform(0, 400, 75, 50), Platform(200, 325, 125, 50), Platform(375, 300, 50, 50), 
        Platform(475, 325, 125, 50), Platform(650, 250, 75, 50), Platform(475, 175, 75, 50), 
        Platform(200, 125, 175, 50), Platform(50, 225, 25, 50), Platform(110, 225, 25, 50)],
    3: [Platform(50, 500, 125, 50), Platform(300, 500, 125, 50), Platform(500, 500, 25, 100), 
        Platform(600, 500, 125, 50), Platform(750, 450, 50, 50), Platform(650, 375, 50, 50), 
        Platform(750, 300, 50, 50), Platform(650, 225, 50, 50), Platform(750, 150, 50, 50), 
        Platform(650, 75, 50, 50), Platform(625, 75, 25, 350), Platform(0, 350, 625, 25), 
        Platform(475, 0, 25, 225), Platform(0, 225, 100, 25), Platform(150, 175, 100, 25), 
        Platform(0, 225, 100, 25), Platform(25, 50, 200, 25), Platform(300, 125, 100, 25), 
        Platform(125, 275, 100, 25)],
    4: [Platform(675, 100, 150, 25), Platform(175, 75, 450, 50), Platform(50, 250, 150, 25), 
        Platform(225, 200, 50, 50), Platform(350, 200, 150, 50), Platform(575, 200, 250, 50), 
        Platform(675, 250, 25, 175), Platform(250, 375, 425, 50), Platform(0, 425, 100, 50), 
        Platform(175, 450, 50, 50), Platform(250, 525, 475, 50), Platform(775, 475, 25, 75), 
        Platform(700, 400, 25, 75), Platform(775, 325, 25, 75), Platform(700, 300, 50, 25)],
    5: [Platform(175, 75, 575, 25), Platform(75, 125, 25, 25), Platform(0, 200, 50, 50), 
        Platform(75, 275, 50, 50), Platform(175, 350, 50, 50), Platform(125, 425, 400, 50), 
        Platform(250, 150, 50, 75), Platform(425, 150, 50, 75), Platform(425, 250, 100, 25), 
        Platform(575, 275, 50, 50), Platform(675, 350, 50, 50), Platform(575, 400, 50, 50), 
        Platform(775, 150, 25, 50), Platform(625, 150, 25, 25)]
}

levels_enemies = {
    1: [Spike(300, 425)] + [Spike(i * 50, 575) for i in range(16)],
    2: [Spike(375, 275), Spike(400, 275), Spike(50, 200), Spike(110, 200), 
        Enemy(525, 300, 62)] + [Spike(i * 50, 575) for i in range(16)],
    3: [Spike(500, 475), Spike(575, 325), Spike(600, 325), 
        Enemy(550, 150, 50), Enemy(550, 100, 50), Enemy(100, 325, 100), 
        Enemy(225, 325, 100)] + [Spike(i * 50, 575) for i in range(16)],
    4: [Spike(450, 50), Spike(325, 50), Spike(125, 225), Spike(400, 175), 
        Spike(475, 175), Spike(350, 350), Spike(0, 400), Spike(75, 400), 
        Spike(375, 500), Spike(500, 500), Spike(700, 275), Spike(575, 175), 
        Spike(625, 175), Spike(675, 175), Spike(725, 175), Spike(775, 175), 
        Enemy(425, 350, 50), Enemy(300, 500, 50), Enemy(600, 500, 50)] + 
        [Spike(i * 50, 575) for i in range(16)],
    5: [Spike(275, 50), Spike(700, 50), Spike(0, 175), Spike(375, 400), 
        Spike(700, 325), Spike(475, 225), Spike(500, 225), Enemy(400, 50, 50), 
        Enemy(525, 50, 50)] + [Spike(i * 50, 575) for i in range(16)]
}

levels_collectibles = {
    1: [Collectible(150, 425), Collectible(500, 375)],
    2: [Collectible(100, 450), Collectible(475, 150), 
        Collectible(200, 100), Collectible(75, 250)],
    3: [Collectible(775, 425), Collectible(675, 50), 
        Collectible(50, 325), Collectible(525, 325), Collectible(50, 25)],
    4: [Collectible(425, 175), Collectible(500, 350), 
        Collectible(50, 400), Collectible(725, 275)],
    5: [Collectible(625, 125), Collectible(325, 50), Collectible(450, 225)]
}

player_start_positions = {
    1: (75, 425),
    2: (675, 450),
    3: (100, 400),
    4: (750, 75),
    5: (250, 125)
}

# Функции коллизий
def check_collision_platforms(player, platforms):
    for platform in platforms:
        if pygame.sprite.collide_rect(player, platform):
            dx = player.rect.centerx - platform.rect.centerx
            dy = player.rect.centery - platform.rect.centery
            
            overlap_x = min(player.rect.right, platform.rect.right) - max(player.rect.left, platform.rect.left)
            overlap_y = min(player.rect.bottom, platform.rect.bottom) - max(player.rect.top, platform.rect.top)
            
            if overlap_x < overlap_y:
                if dx > 0:
                    player.rect.left = platform.rect.right
                    player.x_velocity = 0
                else:
                    player.rect.right = platform.rect.left
                    player.x_velocity = 0
            else:
                if dy > 0:
                    player.rect.top = platform.rect.bottom
                    player.y_velocity = 0
                else:
                    player.rect.bottom = platform.rect.top
                    player.y_velocity = 0
                    player.on_ground = True

def check_collision_enemies(player, enemies):
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            death_sound.play()
            start_pos = player_start_positions[current_level]
            player.rect.x = start_pos[0]
            player.rect.y = start_pos[1]
            player.x_velocity = 0
            player.y_velocity = 0
            return True
    return False

def check_collision_collectibles(player, collectibles):
    global score
    collected = False
    
    for collectible in collectibles[:]:
        if player.rect.colliderect(collectible.rect):
            coin_sound.play()
            collectible.kill()
            collectibles.remove(collectible)
            score += 1
            collected = True
    
    return collected

def check_level_completion():
    global current_level, game_completed
    
    if current_level in levels_collectibles:
        remaining = [c for c in levels_collectibles[current_level] if c in collectibles]
        if len(remaining) == 0:
            if current_level < max_level:
                current_level += 1
                win_sound.play()
                load_level(current_level)
            else:
                game_completed = True

# Функция загрузки уровня
def load_level(level):
    global player, platforms, enemies, collectibles, all_sprites
    
    if level not in player_start_positions:
        return
    
    # Очищаем группы спрайтов
    if 'all_sprites' in globals():
        all_sprites.empty()
    else:
        all_sprites = pygame.sprite.Group()
    
    # Создаем игрока
    start_pos = player_start_positions[level]
    player = Player(start_pos[0], start_pos[1])
    all_sprites.add(player)
    
    # Загружаем объекты
    platforms = levels_platforms.get(level, [])[:]
    enemies = levels_enemies.get(level, [])[:]
    collectibles = levels_collectibles.get(level, [])[:]
    
    # Добавляем в группы
    for platform in platforms:
        all_sprites.add(platform)
    
    for enemy in enemies:
        all_sprites.add(enemy)
    
    for collectible in collectibles:
        all_sprites.add(collectible)

# Функция управления
def handle_input(player):
    player.x_velocity = 0
    
    # Проверяем управление из JavaScript
    try:
        import js
        controls = {
            'left': bool(js.window.gameControls.left),
            'right': bool(js.window.gameControls.right),
            'jump': bool(js.window.gameControls.jump)
        }
        
        if controls['left']:
            player.x_velocity = -5
        if controls['right']:
            player.x_velocity = 5
        if controls['jump'] and player.on_ground:
            player.y_velocity = -7
            player.on_ground = False
            jump_sound.play()
            
            js.window.gameControls.jump = False
    except:
        pass
    
    # Клавиатура
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.x_velocity = -5
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.x_velocity = 5
    
    if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and player.on_ground:
        player.y_velocity = -7
        player.on_ground = False
        jump_sound.play()

# Создаем кнопки меню
button_start = Button(300, 200, (200, 68, 32), (242, 117, 82), "Старт")
button_fullscreen = Button(300, 350, (32, 103, 200), (82, 138, 242), "Полный экран")
button_sound = Button(300, 500, (48, 200, 32), (82, 242, 93), "Звук вкл/выкл")

# Функция для отправки события в JavaScript
def send_pyscript_event(name, detail=""):
    try:
        import js
        event = js.CustomEvent.new(f"pygame:{name}", {"detail": detail})
        js.document.dispatchEvent(event)
    except:
        pass

# Основная функция игры
def main_game():
    global current_level, game_started, game_completed, score, fullscreen, sound_play
    
    print("Создаем игровое окно...")
    
    # Создаем экран
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tiny Green Cube - PyScript")
        print("✅ Игровое окно создано")
        send_pyscript_event("ready", "Игра готова к запуску")
    except Exception as e:
        print(f"❌ Ошибка создания окна: {e}")
        send_pyscript_event("error", str(e))
        return
    
    clock = pygame.time.Clock()
    running = True
    
    print("Запускаем игровой цикл...")
    
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                if not game_started:
                    if button_start.is_over(mouse_pos):
                        button_sound.play()
                        current_level = 1
                        load_level(current_level)
                        game_started = True
                    elif button_fullscreen.is_over(mouse_pos):
                        button_sound.play()
                        if not fullscreen:
                            try:
                                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                                fullscreen = True
                            except:
                                print("Полноэкранный режим не поддерживается")
                        else:
                            screen = pygame.display.set_mode((WIDTH, HEIGHT))
                            fullscreen = False
                    elif button_sound.is_over(mouse_pos):
                        button_sound.play()
                        sound_play = not sound_play
        
        # Меню
        if not game_started:
            screen.blit(bg_6, (0, 0))
            
            # Заголовок
            title_font = pygame.font.SysFont(None, 48)
            title_text = title_font.render("Tiny Green Cube", True, (0, 255, 0))
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
            
            # Кнопки
            button_start.hovered = button_start.is_over(pygame.mouse.get_pos())
            button_fullscreen.hovered = button_fullscreen.is_over(pygame.mouse.get_pos())
            button_sound.hovered = button_sound.is_over(pygame.mouse.get_pos())
            
            button_start.draw(screen)
            button_fullscreen.draw(screen)
            button_sound.draw(screen)
            
            # Музыка меню
            if sound_play:
                menu_music.play()
            
            pygame.display.flip()
            clock.tick(FPS)
            continue
        
        # Завершение игры
        if game_completed:
            menu_music.stop()
            end_music.play()
            
            screen.blit(bg_2, (0, 0))
            
            font = pygame.font.SysFont(None, 48)
            text1 = font.render("Спасибо за игру!", True, (0, 0, 0))
            text2 = font.render(f"Итоговый счет: {score}", True, (0, 0, 255))
            
            screen.blit(text1, (WIDTH//2 - text1.get_width()//2, 200))
            screen.blit(text2, (WIDTH//2 - text2.get_width()//2, 300))
            
            # Кнопка для отзыва
            button_feedback = Button(325, 375, (32, 103, 200), (82, 138, 242), "Оставить отзыв")
            button_feedback.hovered = button_feedback.is_over(pygame.mouse.get_pos())
            button_feedback.draw(screen)
            
            pygame.display.flip()
            clock.tick(FPS)
            
            # Обработка клика на кнопку отзыва
            if pygame.mouse.get_pressed()[0]:
                if button_feedback.is_over(pygame.mouse.get_pos()):
                    try:
                        import js
                        js.window.open("https://t.me/Infoplatformer_bot", "_blank")
                    except:
                        print("Открываем ссылку на бота")
            
            continue
        
        # Основной игровой процесс
        if 'player' in globals() and player:
            # Управление
            handle_input(player)
            
            # Гравитация
            player.y_velocity += 0.3
            
            # Обновление
            player.update()
            for enemy in enemies:
                if isinstance(enemy, Enemy):
                    enemy.update()
            
            # Коллизии
            check_collision_platforms(player, platforms)
            check_collision_enemies(player, enemies)
            check_collision_collectibles(player, collectibles)
            
            # Проверка завершения уровня
            check_level_completion()
        
        # Отрисовка
        if current_level == 1:
            screen.blit(bg_1, (0, 0))
            if sound_play:
                level_song_1.play()
        elif current_level == 2:
            screen.blit(bg_3, (0, 0))
            if sound_play:
                level_song_2.play()
        elif current_level == 3:
            screen.blit(bg_4, (0, 0))
            if sound_play:
                level_song_3.play()
        elif current_level == 4:
            screen.blit(bg_5, (0, 0))
            if sound_play:
                level_song_4.play()
        elif current_level == 5:
            screen.blit(bg_7, (0, 0))
            if sound_play:
                level_song_5.play()
        else:
            screen.fill((0, 0, 0))
        
        # Отрисовка всех спрайтов
        if 'all_sprites' in globals():
            all_sprites.draw(screen)
        
        # UI
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Счет: {score}", True, (0, 0, 0))
        level_text = font.render(f"Уровень: {current_level}/{max_level}", True, (0, 0, 255))
        
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        
        # Обновление экрана
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    print("Игра завершена")

# Запуск игры
if __name__ == "__main__":
    try:
        main_game()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        send_pyscript_event("error", str(e))