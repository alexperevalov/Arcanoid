import pygame
import random

W = 500
H = 400
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
FIRE_BRICK = (178, 34, 34)
ORANGE = (255, 140, 0)
BLUE = (0, 0, 255)
YELLOW = (240, 255, 48)
GREEN = (50, 205, 50)

# константы для шарика
MAX_DXY = 6
ball_speed = BALL_SPEED_DEFAULT = 1
BALL_R = 10
BALL_RECT_SIZE = int((BALL_R * 2) ** 0.5)
# константы для биты
BAT_SPEED = 6
bat_width = BAT_WIDTH_DEFAULT = 40
BAT_HEIGHT = 10
BAT_LIFT = 20

pygame.init()
screen = pygame.display.set_mode((W, H))


def bat_n_ball_init():
    global bat_x, bat_y, bat_rect, ball_x, ball_y, dx, dy, ball_rect
    # инициализация биты
    bat_x = W // 2 - bat_width // 2
    bat_y = H - BAT_LIFT - BAT_HEIGHT
    bat_rect = pygame.Rect(bat_x, bat_y, bat_width, BAT_HEIGHT)

    # инициализация шарика
    ball_x = bat_x + bat_width // 2
    ball_y = bat_y - BALL_R
    dx = random.randint(-MAX_DXY, MAX_DXY) * ball_speed
    dy = -int(((MAX_DXY * ball_speed) ** 2 - dx ** 2) ** 0.5)

    # для расчета столкновений с кирпичиками будем использовать "вписанный" квадрат
    ball_rect = pygame.Rect(ball_x - BALL_RECT_SIZE // 2, ball_y - BALL_RECT_SIZE // 2, BALL_RECT_SIZE, BALL_RECT_SIZE)


bat_n_ball_init()

# кирпичики
BRICKS_TOP = 50
BRICK_ROWS = 3
BRICKS_IN_ROW = 10
BRICK_COLORS = [
    None,
    GREEN,
    ORANGE,
    FIRE_BRICK
]
BRICK_W = W // BRICKS_IN_ROW
BRICK_H = 30
BORDER = 2

# уровни
# каждый уровень - список из 30-ти цифр 0..3
# где 0 - пусто
# 1..3 - количество ударов, которые разбивают кирпич
LEVELS = [
    [0, 0, 0, 1, 1, 1, 1, 0, 0, 0,
     0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 3, 3, 3, 1, 1, 3, 3, 3, 1,
     1, 1, 2, 1, 1, 1, 1, 2, 1, 1,
     1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
     0, 2, 0, 2, 0, 2, 0, 2, 0, 2,
     0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [0, 3, 3, 3, 3, 3, 3, 3, 3, 0,
     0, 3, 3, 3, 3, 3, 3, 3, 3, 0,
     0, 3, 3, 3, 3, 3, 3, 3, 3, 0],
]
level = 0  # начнем с нулевого для простоты

# БОНУСЫ
BONUSES = ['speed_ball', 'wide_bat']
BONUS_FALLING_SPEED = 1
BONUS_TIME = 10000
current_bonus = None
current_bonus_type = ''

# ЗВУКИ
hit_sound = pygame.mixer.Sound('sounds/hit.wav')
fail_sound = pygame.mixer.Sound('sounds/fail.wav')
done_sound = pygame.mixer.Sound('sounds/next_level.wav')
b_cancel_sound = pygame.mixer.Sound('sounds/bonus_cancel.wav')
b_ext_sound = pygame.mixer.Sound('sounds/extension.wav')
b_fast_ball_sound = pygame.mixer.Sound('sounds/fast_ball.wav')

def get_bricks():
    lv = LEVELS[level]
    rects = []
    for i in range(BRICK_ROWS):
        for j in range(BRICKS_IN_ROW):
            if lv[i * BRICKS_IN_ROW + j]:
                # формируем список, где каждый элемент - список из двух элементов
                # "сила" (этоже цвет) кирпичика и
                # Rect объект для кирпичика - будет использоваться для отрисовки и для проверки столкновений
                rects.append([lv[i * BRICKS_IN_ROW + j],
                              pygame.Rect(j * BRICK_W + BORDER,
                                          i * BRICK_H + BORDER + BRICKS_TOP,
                                          BRICK_W - BORDER,
                                          BRICK_H - BORDER)])
    return rects


bricks = get_bricks()
points = 0  # очки
lives = 3  # жизней на старте

points_font = pygame.font.SysFont('comic sans ms', 18)
small_font = pygame.font.SysFont('comic sans ms', 16)
small_font.set_bold(True)
big_font = pygame.font.SysFont('comic sans ms', 60)
mid_font = pygame.font.SysFont('comic sans ms', 32)

gameover_text = big_font.render('GAME OVER', 1, RED)
welldone_text = mid_font.render('СУПЕР! ТЫ МОЛОДЕЦ!', 1, RED)
nextlevel_text = mid_font.render('СЛЕДУЮЩИЙ УРОВЕНЬ...', 1, GREEN)
win_text = big_font.render('WIN', 1, GREEN)
press_space_text = points_font.render('жми <пробел> и играй еще раз!', 1, YELLOW)

lastTime = 0
currentTime = 0

pygame.display.set_caption('АРКАНОИД')

heart_img = pygame.image.load('heart.png')

clock = pygame.time.Clock()

game_mode = 'start'
moving = ''

running = True
while running:
    screen.fill(BLACK)

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_LEFT:
                moving = 'left'
            if ev.key == pygame.K_RIGHT:
                moving = 'right'
            if ev.key == pygame.K_SPACE and game_mode == 'start':
                game_mode = 'play'
            if ev.key == pygame.K_SPACE and game_mode == 'gameover':
                game_mode = 'start'
                points = 0
                bat_n_ball_init()
                lastTime = 0  # сброс таймера
                bricks = get_bricks()

        if ev.type == pygame.KEYUP:
            if ev.key == pygame.K_LEFT or ev.key == pygame.K_RIGHT:
                moving = 'stop'

    if moving == 'left' and bat_rect.left > 0:
        bat_rect.left -= BAT_SPEED
        if game_mode == 'start':
            ball_x -= BAT_SPEED
    if moving == 'right' and bat_rect.right < W:
        bat_rect.left += BAT_SPEED
        if game_mode == 'start':
            ball_x += BAT_SPEED

    if game_mode == 'play':
        x = ball_x + dx
        y = ball_y + dy
        # отскок от стен
        if x + BALL_R > W or x - BALL_R < 0:
            dx = -dx
            ball_x += dx
            ball_y = y
        elif y - BALL_R < 0:
            dy = -dy
            ball_y += dy
            ball_x = x
        # отскок от биты
        elif y + BALL_R >= bat_rect.top and bat_rect.left - BALL_R <= x <= bat_rect.left + bat_width + BALL_R:
            dx = (ball_x - (bat_rect.left + bat_width // 2)) / (
                bat_width // 2 + BALL_R) * MAX_DXY * ball_speed  # сложные вычисления для определения направления
                                                                 # отскока
            if dx == 0:  # запретим вертикальный отскок!
                dx = ball_speed
            dy = -int(abs((MAX_DXY * ball_speed) ** 2 - dx ** 2) ** 0.5)
            if dy == 0:  # запретим и горизонтальный отскок тоже!
                dy = -1
            ball_x += dx
            ball_y += dy
            pygame.mixer.Sound.play(hit_sound)
        elif y > H:  # шарик уходит за нижнюю границу
            lives -= 1
            pygame.mixer.Sound.play(fail_sound)
            if lives == 0:
                game_mode = 'gameover'
            else:
                game_mode = 'start'
                bat_n_ball_init()
        else:
            ball_x = x
            ball_y = y
        ball_rect.left = ball_x - BALL_RECT_SIZE // 2
        ball_rect.top = ball_y - BALL_RECT_SIZE // 2

        # проверяем столкновения с кирпичиками
        brick_rect_list = []
        for r in bricks:
            # формируем список Rect'ов
            brick_rect_list.append(r[1])
        index = ball_rect.collidelist(brick_rect_list)
        if index != -1:
            # есть столкновение, определяем направление отскока шарика
            brick = bricks[index][1]
            pygame.mixer.Sound.play(hit_sound)
            if dx > 0:
                delta_x = ball_rect.right - brick.left
            else:
                delta_x = brick.right - ball_rect.left
            if dy > 0:
                delta_y = ball_rect.bottom - brick.top
            else:
                delta_y = brick.bottom - ball_rect.top
            if abs(delta_x - delta_y) < 5:
                dx, dy = -dx, -dy
            elif delta_x > delta_y:
                dy = -dy
            elif delta_y > delta_x:
                dx = -dx
            if bricks[index][0] == 1:
                # кирпичик выбит
                points += 1
                del bricks[index]
                if len(bricks) == 0:
                    game_mode = 'next_level'
                    level += 1
                    pygame.mixer.Sound.play(done_sound)
                    if level == len(LEVELS):
                        game_mode = 'win'
            else:
                # еще держится, но уже слабее ))
                bricks[index] = (bricks[index][0] - 1, bricks[index][1])

    for brick in bricks:
        pygame.draw.rect(screen, BRICK_COLORS[brick[0]], brick[1])

    pygame.draw.rect(screen, YELLOW, bat_rect)
    ball_color = WHITE
    if current_bonus is not None and current_bonus_type == 'speed_ball' and current_bonus['lastTime'] != 0:
        ball_color = FIRE_BRICK
    pygame.draw.circle(screen, ball_color, (ball_x, ball_y), BALL_R)

    if game_mode == 'play' and current_bonus is not None:
        if current_bonus['lastTime'] == 0:
            # бонус "падает"
            current_bonus['y'] += BONUS_FALLING_SPEED
            if current_bonus['y'] > H:
                current_bonus = None
            elif bat_rect.colliderect(pygame.Rect(current_bonus['x'], current_bonus['y'], 10, 10)):
                # поймали бонус
                current_bonus['lastTime'] = pygame.time.get_ticks()
                if current_bonus_type == 'speed_ball':
                    ball_speed *= 1.5
                    pygame.mixer.Sound.play(b_fast_ball_sound)
                elif current_bonus_type == 'wide_bat':
                    bat_width *= 2
                    bat_rect.width = bat_width
                    pygame.mixer.Sound.play(b_ext_sound)
            else:
                screen.blit(current_bonus['text'], (current_bonus['x'], current_bonus['y']))
        else:
            # проверяем таймер отмены бонуса
            currentTime = pygame.time.get_ticks()
            if currentTime - current_bonus['lastTime'] > BONUS_TIME:
                pygame.mixer.Sound.play(b_cancel_sound)
                current_bonus = None
                ball_speed = BALL_SPEED_DEFAULT
                bat_width = BAT_WIDTH_DEFAULT
                bat_rect.width = bat_width
    elif game_mode == 'play' and current_bonus is None:
        # "запускаем" бонус
        current_bonus_type = random.choice(BONUSES)
        current_bonus = {}
        bonus_color = GREEN
        if current_bonus_type == 'speed_ball':
            bonus_color = FIRE_BRICK
        current_bonus['text'] = small_font.render('B', 1, bonus_color)
        current_bonus['y'] = BRICKS_TOP
        current_bonus['x'] = random.randint(50, W - 60)
        current_bonus['lastTime'] = 0

    if game_mode == 'next_level':
        current_bonus = None
        ball_speed = BALL_SPEED_DEFAULT
        bat_width = BAT_WIDTH_DEFAULT
        screen.fill(BLACK)
        screen.blit(welldone_text, (70, 140))
        currentTime = pygame.time.get_ticks()
        if lastTime == 0:
            lastTime = currentTime  # запускаем таймер
        elif 4000 >= currentTime - lastTime > 1000:
            screen.blit(nextlevel_text, (60, 220))
        elif currentTime - lastTime > 4000:
            game_mode = 'start'
            lives += 1  # вознаграждение: +1 жизнь
            bat_n_ball_init()
            lastTime = 0  # сброс таймера
            bricks = get_bricks()

    if game_mode == 'win':
        screen.fill(BLACK)
        screen.blit(win_text, (170, 140))

    if game_mode == 'gameover':
        lives = 3
        level = 0
        current_bonus = None
        ball_speed = BALL_SPEED_DEFAULT
        bat_width = BAT_WIDTH_DEFAULT
        screen.fill(BLACK)
        screen.blit(gameover_text, (80, 140))
        currentTime = pygame.time.get_ticks()
        if lastTime == 0:
            lastTime = currentTime  # запускаем таймер
        elif 20000 >= currentTime - lastTime > 1000:
            screen.blit(press_space_text, (120, 230))
        elif currentTime - lastTime > 20000:
            game_mode = 'start'
            points = 0
            bat_n_ball_init()
            lastTime = 0  # сброс таймера
            bricks = get_bricks()

    screen.blit(points_font.render(str(points), 1, ORANGE), (10, 10))
    for li in range(lives):
        screen.blit(heart_img, (W - 30 * (li + 1), 10))

    clock.tick(FPS)
    pygame.display.update()
pygame.quit()
