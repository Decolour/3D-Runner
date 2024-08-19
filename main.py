import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
HORIZON_Y = SCREEN_HEIGHT // 4  # Горизонтальная линия на границе между первой и остальными тремя четвертями
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Инициализация экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3D Runner")  # Установка заголовка окна

# Загрузка изображений
player_image = pygame.image.load('player.png').convert_alpha()
obstacle_image = pygame.image.load('obstacle.png').convert_alpha()


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.speed_x = 0

    def update(self):
        self.rect.x += self.speed_x

        # Ограничение движения игрока по экрану
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH


# Класс препятствий
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = obstacle_image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.start_pos = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.center = (self.start_pos, HORIZON_Y)
        self.size = 0.1  # Начальный размер препятствия

    def update(self, global_speed):
        min_speed = 0.5  # Минимальная скорость, с которой объекты будут двигаться
        effective_speed = max(global_speed, min_speed)

        # Увеличиваем размер постепенно и пропорционально увеличиваем позицию
        if self.size < 1.0:
            self.size += effective_speed / 100  # Регулируем скорость увеличения
        self.image = pygame.transform.scale(self.original_image,
                                            (int(self.original_image.get_width() * self.size),
                                             int(self.original_image.get_height() * self.size)))
        self.rect = self.image.get_rect(center=(self.start_pos, self.rect.centery + int(effective_speed * 10)))

        # Удаляем препятствие, если оно вышло за пределы экрана
        if self.rect.top > SCREEN_HEIGHT or self.size > 2:  # Убираем слишком увеличенные препятствия
            self.kill()


# Основная игра
def game():
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    # Начальная скорость и ускорение
    speed = 0  # Начальная скорость равна нулю
    acceleration = 0.0005  # Ускорение
    deceleration = acceleration / 3  # Замедление при отпускании клавиши
    fast_deceleration = acceleration * 2  # Быстрое замедление при нажатии вниз

    # Начальный интервал появления препятствий
    obstacle_interval = 1000  # В миллисекундах
    last_obstacle_time = pygame.time.get_ticks()

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.speed_x = -5
                elif event.key == pygame.K_RIGHT:
                    player.speed_x = 5
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.speed_x = 0

        # Получаем текущее состояние клавиш
        keys = pygame.key.get_pressed()

        # Ускорение при удержании клавиши "Вверх"
        if keys[pygame.K_UP]:
            speed += acceleration
        # Замедление при удержании клавиши "Вниз" (в два раза быстрее, чем ускорение)
        elif keys[pygame.K_DOWN]:
            speed -= fast_deceleration
            if speed < 0:
                speed = 0  # Скорость не может быть отрицательной
        # Плавное замедление, если никакие клавиши не удерживаются
        else:
            speed -= deceleration
            if speed < 0:
                speed = 0  # Скорость не может быть отрицательной

        # Обновляем интервал появления препятствий в зависимости от скорости
        if speed > 0:
            obstacle_interval = max(1000 - int(speed * 900), 100)  # Интервал от 1000 до 100 мс
            if current_time - last_obstacle_time > obstacle_interval:
                obstacle = Obstacle()
                all_sprites.add(obstacle)
                obstacles.add(obstacle)
                last_obstacle_time = current_time

        # Обновляем игрока и препятствия отдельно
        player.update()
        obstacles.update(speed)

        # Проверка на столкновение
        if pygame.sprite.spritecollideany(player, obstacles):
            running = False

        # Отрисовка горизонта
        screen.fill(WHITE)
        pygame.draw.line(screen, BLACK, (0, HORIZON_Y), (SCREEN_WIDTH, HORIZON_Y), 3)  # Линия горизонта
        all_sprites.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game()




