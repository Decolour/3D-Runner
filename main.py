import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
HORIZON_Y = SCREEN_HEIGHT // 4  # Горизонтальная линия
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Инициализация экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3D Runner")

# Загрузка изображений
player_image = pygame.image.load('player.png').convert_alpha()
obstacle_image = pygame.image.load('obstacle.png').convert_alpha()
hazard_image = pygame.image.load('hazard.png').convert_alpha()  # Второй тип препятствий
blood_splash_image = pygame.image.load('blood_splash.png').convert_alpha()
damage_splash_image = pygame.image.load('damage_splash.png').convert_alpha()


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.speed_x = 0
        self.health = 100  # Начальное здоровье игрока

    def update(self):
        self.rect.x += self.speed_x

        # Ограничение движения игрока по экрану
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH


# Класс препятствий
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image, effect_type="blood", points=50, health_impact=0):
        super().__init__()
        self.original_image = image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.start_pos = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.center = (self.start_pos, HORIZON_Y)
        self.size = 0.1  # Начальный размер препятствия
        self.effect_type = effect_type
        self.points = points  # Очки за это препятствие
        self.health_impact = health_impact  # Влияние на здоровье игрока при столкновении

    def update(self, global_speed):
        min_speed = 0.5  # Минимальная скорость
        effective_speed = max(global_speed, min_speed)

        if self.size < 1.0:
            self.size += effective_speed / 100  # Скорость увеличения
        self.image = pygame.transform.scale(self.original_image,
                                            (int(self.original_image.get_width() * self.size),
                                             int(self.original_image.get_height() * self.size)))
        self.rect = self.image.get_rect(center=(self.start_pos, self.rect.centery + int(effective_speed * 10)))

        if self.rect.top > SCREEN_HEIGHT or self.size > 2:  # Убираем слишком увеличенные препятствия
            self.kill()


# Функция для отображения изображения на короткий промежуток времени
def show_effect(effect_image, duration=0.25):
    screen.blit(effect_image, (
    SCREEN_WIDTH // 2 - effect_image.get_width() // 2, SCREEN_HEIGHT // 2 - effect_image.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(int(duration * 1000))


# Основная игра
def game():
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    # Начальная скорость и ускорение
    speed = 0  # Начальная скорость равна нулю
    acceleration = 0.005  # Ускорение
    deceleration = acceleration / 3  # Замедление при отпускании клавиши
    fast_deceleration = acceleration * 2  # Быстрое замедление при нажатии вниз

    # Начальный интервал появления препятствий
    obstacle_interval = 1000  # В миллисекундах
    last_obstacle_time = pygame.time.get_ticks()

    # Начальные очки
    score = 0

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
                # Определяем тип препятствия случайным образом
                if random.choice([True, False]):
                    obstacle = Obstacle(obstacle_image, "blood", 50)
                else:
                    obstacle = Obstacle(hazard_image, "damage", 0, -20)  # Второй тип препятствия с уменьшением здоровья

                all_sprites.add(obstacle)
                obstacles.add(obstacle)
                last_obstacle_time = current_time

        # Обновляем игрока и препятствия отдельно
        player.update()
        obstacles.update(speed)

        # Проверка на столкновение с учетом вертикального выравнивания и перекрытия
        for obstacle in obstacles:
            # Проверка на одну линию по вертикали
            if abs(player.rect.centery - obstacle.rect.centery) < 7:  # Допустимая погрешность в пикселях
                # Проверка горизонтального перекрытия только если выполнено первое условие
                horizontal_overlap = min(player.rect.right, obstacle.rect.right) - max(player.rect.left,
                                                                                       obstacle.rect.left)
                if horizontal_overlap >= 10:  # Проверка перекрытия на 10 пикселей
                    if obstacle.effect_type == "blood":
                        score += obstacle.points  # Добавляем очки за столкновение
                        show_effect(blood_splash_image)  # Показать брызги крови

                        # Показать изображение очков
                        font = pygame.font.Font(None, 74)
                        score_text = font.render("+50", True, RED)
                        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                                                 SCREEN_HEIGHT // 2 - score_text.get_height() // 2))
                        pygame.display.flip()
                        pygame.time.delay(250)

                    elif obstacle.effect_type == "damage":
                        player.health += obstacle.health_impact  # Уменьшаем здоровье игрока
                        show_effect(damage_splash_image)  # Показать повреждение

                        # Показать уменьшение здоровья
                        font = pygame.font.Font(None, 74)
                        health_text = font.render(f"{obstacle.health_impact}", True, RED)
                        screen.blit(health_text, (SCREEN_WIDTH // 2 - health_text.get_width() // 2,
                                                  SCREEN_HEIGHT // 2 - health_text.get_height() // 2))
                        pygame.display.flip()
                        pygame.time.delay(250)

                    obstacle.kill()  # Удаляем препятствие после столкновения

        # Завершение игры при достижении 10000 очков или если здоровье игрока падает до 0
        if score >= 10000 or player.health <= 0:
            running = False

        # Отрисовка горизонта
        screen.fill(WHITE)
        pygame.draw.line(screen, BLACK, (0, HORIZON_Y), (SCREEN_WIDTH, HORIZON_Y), 2)

        # Отображение всех спрайтов
        all_sprites.draw(screen)

        # Отображение текущих очков
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Отображение текущего здоровья
        health_text = font.render(f"Health: {player.health}", True, BLACK)
        screen.blit(health_text, (10, 50))

        # Обновление экрана
        pygame.display.flip()

        # Ограничение FPS
        clock.tick(FPS)

        # Завершаем Pygame
    pygame.quit()
    sys.exit()


# Запуск игры
if __name__ == "__main__":
    game()

1


