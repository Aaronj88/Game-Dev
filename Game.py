import pygame
import random
import time
import sys

pygame.init()
pygame.font.init()

#screen
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h
scr = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Walk Around')

#vars (p_speed is pixels per second now)
p_speed = 250.0
base_speed = 250.0
lives = 3
points = 0
level = 1
c_size = 50
base_size = 50
direction = "right"
bg_col = (200,120,250) #purple
r_val = 200
g_val = 120
b_val = 250

#new skeleton vars
crystals_collected = 0
STATUS_BAR_HEIGHT = 130
status_fill = 0  #bar filling value

#colors
w = (255,255,255)
b = (0,0,0)
r = (255,0,0)
g = (0,255,0)

#ui
font = pygame.font.SysFont('Arial', 35)
font_big = pygame.font.SysFont('msgothic', 120)

#game state
game_over_state = False
win_state = False

#player images
plyr_orig = pygame.image.load("player.png").convert_alpha()
plyr_right = pygame.transform.scale(plyr_orig, (80, 80))
plyr_left = pygame.transform.flip(plyr_right, True, False)
plyr = plyr_right
plyr_rect = plyr.get_rect()
plyr_rect.center = (WIDTH//2, HEIGHT//2 + 200)

#coin
coin_img = pygame.image.load("coin.png").convert_alpha()
def respawn_coin():
    global coin_scaled, coin_rect
    size = max(5, int(c_size))
    coin_scaled = pygame.transform.scale(coin_img, (size, size))
    coin_rect = coin_scaled.get_rect()
    coin_rect.x = random.randint(10, WIDTH - size - 10)
    coin_rect.y = random.randint(STATUS_BAR_HEIGHT + 10, HEIGHT - size - 10)
respawn_coin()

#crystal
crystal_img = pygame.image.load("crystal.png").convert_alpha()
crystal_img = pygame.transform.scale(crystal_img, (200,150))
crystal_active = False
crystal_time = 0

#walls
walls = []

#heart
heart = pygame.image.load("heart.png")
heart = pygame.transform.scale(heart,(65,65))

#background color (purple to green)
def bg_color_for_level(lvl):
    global r_val, g_val, b_val, level
    #purple (200,120,250) to green (120, 250, 150)
    t = min(1.0, lvl/10.0)
    if level <= 9:
        r_val -= 8
        g_val += 13
        b_val -= 10
    
    return (r_val, g_val, b_val)

bg_col = bg_color_for_level(level)
txt_c = (255,255,255)


#movement - dt-based
def handle_move(keys, dt):
    global direction, plyr, plyr_rect
    move_amount = p_speed * dt

    if keys[pygame.K_LEFT]:
        if direction != "left":
            direction = "left"
            plyr = plyr_left
        plyr_rect.x -= move_amount

    if keys[pygame.K_RIGHT]:
        if direction != "right":
            direction = "right"
            plyr = plyr_right
        plyr_rect.x += move_amount

    if keys[pygame.K_UP]:
        plyr_rect.y -= move_amount

    if keys[pygame.K_DOWN]:
        plyr_rect.y += move_amount

    #normal borders
    plyr_rect.x = max(0, min(plyr_rect.x, WIDTH - plyr_rect.width))
    plyr_rect.y = max(129, min(plyr_rect.y, HEIGHT - plyr_rect.height))


def check_border_touch():
    if (plyr_rect.left <= 0 or 
        plyr_rect.right >= WIDTH or 
        plyr_rect.bottom >= HEIGHT or
        plyr_rect.top <= 130):
        lose_life("border")


def lose_life(reason=''):
    global lives, p_speed, walls, crystal_active, plyr_rect, game_over_state

    lives -= 1
    plyr_rect.center = (WIDTH//2, HEIGHT//2 + 200)
    p_speed = max(base_speed, p_speed - 20.0)
    walls.clear()
    crystal_active = False

    if lives <= 0:
        game_over_state = True


def add_life():
    global lives, p_speed
    lives += 1
    p_speed = max(base_speed, p_speed - 20.0)



def spawn_wall():
    global w_, h_, x, y
    if abs(plyr_rect.x - coin_rect.x) > abs(plyr_rect.y - coin_rect.y):
        wmin, wmax = 10,80
        hmin, hmax = 20, 150
        h_ = random.randint(hmin, hmax) + abs(plyr_rect.y - coin_rect.y)
        w_ = random.randint(wmin,wmax)
        x = ((plyr_rect.x + coin_rect.x) / 2) + random.randint(-20,20)
        if plyr_rect.y < coin_rect.y:
            y = plyr_rect.y - random.randint(20,100)
        else:
            y = coin_rect.y - random.randint(20,100)
        
    else:
        hmin, hmax = 10,80
        wmin, wmax = 20,150
        h_ = random.randint(hmin,hmax)
        w_ = random.randint(wmin, wmax) + abs(plyr_rect.x - coin_rect.x)
        y = ((plyr_rect.y + coin_rect.y) / 2) + random.randint(-20,20)
        if plyr_rect.x < coin_rect.x:
            x = plyr_rect.x - random.randint(20,100)
        else:
            x = coin_rect.x - random.randint(20,100)


    tries = 0

    while tries < 40:
        rect = pygame.Rect(x, y, w_, h_)

        if not rect.colliderect(plyr_rect.inflate(120,120)) and not rect.colliderect(coin_rect.inflate(80,80)):
            color = (random.randint(50,200), random.randint(50,200), random.randint(50,200))
            walls.append({"rect": rect, "color": color, "time": time.time()})
            return
        tries += 1


def maybe_spawn_wall():
    chance = min(0.9, 0.05 + 0.07 * (level - 1))
    if random.random() < chance:
        spawn_wall()


def spawn_crystal():
    global crystal_active, crystal_rect, crystal_scaled, crystal_time

    size = max(25, int(c_size * 1.4))
    crystal_scaled = pygame.transform.scale(crystal_img, (20,50))
    crystal_rect = crystal_scaled.get_rect()
    crystal_rect.x = random.randint(10, WIDTH - crystal_rect.width - 10)
    crystal_rect.y = random.randint(STATUS_BAR_HEIGHT + 10, HEIGHT - crystal_rect.height - 10)

    crystal_time = time.time()
    crystal_active = True




#points/levels
def add_points():
    global points, level, c_size, p_speed

    if plyr_rect.colliderect(coin_rect):
        points += 1
        c_size -= 1
        if c_size <= 10:
            c_size = int(base_size * 0.9)

        p_speed += 12.0
        respawn_coin()

        new_lvl = points // 10 + 1
        if new_lvl > level:
            level_up(new_lvl)

        maybe_spawn_wall()


def level_up(n):
    global level, bg_col, status_fill, p_speed, win_state
    level = n

    #update background smooth transition
    bg_col = bg_color_for_level(level)

    #fill status bar more and more red
    status_fill = min(255, int((level/10)*255))

    p_speed += 20.0
    if level > 10:
        win_state = True


def handle_collisions():
    global crystal_active, crystals_collected

    if crystal_active and plyr_rect.colliderect(crystal_rect):
        crystals_collected += 1
        crystal_active = False

        if crystals_collected == 5:
            add_life()
            crystals_collected = 0

    for wdict in list(walls):
        if plyr_rect.colliderect(wdict["rect"]):
            try:
                walls.remove(wdict)
            except ValueError:
                pass
            lose_life("wall")
            break


def update_walls():
    now = time.time()
    life = 6 + level
    walls[:] = [w for w in walls if now - w["time"] < life]


def draw_status_bar():
    #draw bar bg
    pygame.draw.rect(scr, (40,40,40), (0,0,WIDTH,STATUS_BAR_HEIGHT))

    #red fill grows with level
    fill_rect = pygame.Rect(0,0,int(WIDTH*(level/10)),STATUS_BAR_HEIGHT)
    pygame.draw.rect(scr, (status_fill,0,0), fill_rect)

    #lives (hearts)
    for i in range(lives):
        scr.blit(heart, (20 + i*60, 20))

    #crystal counter box
    box_rect = pygame.Rect(WIDTH-375, 7, 140, 115)
    pygame.draw.rect(scr, (0,0,0), box_rect, border_radius=8)
    pygame.draw.rect(scr, (255,255,255), box_rect, 2, border_radius=8)
    scr.blit(crystal_img, (1545,-35))

    ctxt = font.render(str(crystals_collected), 1, (255,255,255))
    times_symb = font.render("x", 1, (240,240,240))
    scr.blit(ctxt, (box_rect.centerx - 45, box_rect.centery - ctxt.get_height()//2))
    scr.blit(times_symb, (box_rect.centerx - 20, box_rect.centery - ctxt.get_height()//2))

    #points and level
    ptxt = font.render(f"Points: {points}",1,txt_c)
    ltxt = font.render(f"Level: {level}/10",1,txt_c)
    scr.blit(ptxt, (WIDTH-185, 20))
    scr.blit(ltxt, (WIDTH-185, 60))


def draw():
    scr.fill(bg_col)

    draw_status_bar()

    if not game_over_state and not win_state:
        scr.blit(plyr, plyr_rect)
        scr.blit(coin_scaled, coin_rect)

    if crystal_active and not game_over_state:
        scr.blit(crystal_scaled, crystal_rect)

    for wdict in walls:
        pygame.draw.rect(scr, wdict["color"], wdict["rect"])

    if win_state:
        txt = font_big.render("You Win!", 1, g)
        scr.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//3))

    if game_over_state:
        pygame.image.load() #UNFINISHED


def main():
    global crystal_active, win_state, game_over_state

    last_time = time.time()
    running = True
    while running:
        now = time.time()
        dt = now - last_time
        last_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        if win_state or game_over_state:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                restart()
            draw()
            pygame.display.update()
            continue

        keys = pygame.key.get_pressed()
        handle_move(keys, dt)
        if keys[pygame.K_ESCAPE]:
            running = False

        check_border_touch()
        add_points()
        handle_collisions()
        update_walls()

        if not crystal_active and random.random() < 0.0008 * max(1, level):
            spawn_crystal()

        if crystal_active and time.time() - crystal_time > max(6, 12 - level):
            crystal_active = False

        draw()
        pygame.display.update()

    pygame.quit()


def restart():
    global p_speed, lives, points, level, c_size, win_state, game_over_state, walls, crystal_active, crystals_collected
    p_speed = base_speed
    lives = 3
    points = 0
    level = 1
    c_size = base_size
    walls.clear()
    crystal_active = False
    crystals_collected = 0
    win_state = False
    game_over_state = False
    plyr_rect.center = (WIDTH//2, HEIGHT//2 + 200)
    respawn_coin()


if __name__ == "__main__":
    main()
