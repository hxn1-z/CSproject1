"""Dino Game in Python

A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @bassemfarid (anthropic), no one or nothing else. 🤖 hmm r we sure abt that gang.

Taken over by @hani (brain intelligence)
"""

import pygame
from random import randint
import random as _rnd


# ---- functions ----

def display_score():
    """Draw the score box and return the current score (scales with difficulty)."""
    elapsed = pygame.time.get_ticks() / 1000 - start_time
    difficulty_level = (obstacle_speed - 7.0) / 0.5 + 1
    base = int(elapsed * difficulty_level)
    current_score = base
    surf = game_font.render(f"Score: {current_score}", False, (240, 240, 240))
    r = surf.get_rect(center=(400, 50))
    draw_rect_alpha(game_surface, (0, 0, 0, 115), r.inflate(22, 10), border_radius=12)
    game_surface.blit(surf, r)
    return current_score


def obstacle_movement(obstacle_list, speed):
    """Move and draw each obstacle, then return only the ones still on screen."""
    if obstacle_list:
        for obstacle_rect in obstacle_list:
            obstacle_rect.x -= int(speed)
            if obstacle_rect.bottom >= PLAYER_STAND_Y:
                if selected_character == "player":
                    game_surface.blit(ground_egg_surf, obstacle_rect)
                elif selected_character == "egg":
                    game_surface.blit(ground_player_surf, obstacle_rect)
                else:
                    game_surface.blit(orc_surf, obstacle_rect)
            elif selected_character in ("player", "egg"):
                game_surface.blit(flyegg_surf, obstacle_rect)
            else:
                game_surface.blit(arrow_surf, obstacle_rect)
        remaining = []
        for o in obstacle_list:
            if o.x > -100:
                remaining.append(o)
        return remaining
    else:
        return []


def collisions(player, obstacles):
    """Return False if the player hit any obstacle, True if safe."""
    if obstacles:
        player_hitbox = player.inflate(-10, -6)
        for obstacle_rect in obstacles:
            if player_hitbox.colliderect(obstacle_rect.inflate(-12, -8)):
                return False
    return True


def player_animation():
    """Pick the right player image: jump, duck, or cycle the walk frames."""
    global player_surf, player_index
    if player_rect.bottom < PLAYER_STAND_Y:
        player_surf = player_jump
    elif is_ducking:
        player_surf = player_duck
    else:
        player_index += 0.1
        if player_index >= len(player_walk):
            player_index = 0
        player_surf = player_walk[int(player_index)]


def apply_character(name):
    """Swap the active player sprite set to the chosen character."""
    global player_walk, player_jump, player_duck, player_stand, player_surf
    if name == "egg":
        player_walk = egg_walk
        player_jump = egg_jump
        player_duck = egg_duck
        player_stand = egg_stand
    elif name == "player":
        player_walk = plr_walk
        player_jump = plr_jump
        player_duck = plr_duck
        player_stand = plr_stand
    else:
        player_walk = sol_walk
        player_jump = sol_jump
        player_duck = sol_duck
        player_stand = sol_stand
    player_surf = player_walk[0]


def get_letterbox():
    """Return the scale and centering offset to fit the game in the window without stretching."""
    sw, sh = screen.get_size()
    scale = min(sw / LOGICAL_W, sh / LOGICAL_H)
    nw, nh = int(LOGICAL_W * scale), int(LOGICAL_H * scale)
    ox, oy = (sw - nw) // 2, (sh - nh) // 2
    return scale, ox, oy, nw, nh


def screen_to_game(pos):
    """Convert a window mouse position back into game (800x400) coordinates."""
    scale, ox, oy, _, _ = get_letterbox()
    return (int((pos[0] - ox) / scale), int((pos[1] - oy) / scale))


def draw_rect_alpha(surface, color_rgba, rect, border_radius=0, width=0):
    """Draw a see-through (alpha) rectangle, which pygame.draw.rect can't do directly."""
    tmp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(tmp, color_rgba, tmp.get_rect(), width=width, border_radius=border_radius)
    surface.blit(tmp, rect.topleft)


def draw_shadow_text(surface, text, font, color, shadow_col, center):
    """Draw text twice (offset shadow then top color) for a drop-shadow effect."""
    shadow = font.render(text, True, shadow_col)
    txt = font.render(text, True, color)
    surface.blit(shadow, shadow.get_rect(center=(center[0] + 3, center[1] + 3)))
    surface.blit(txt, txt.get_rect(center=center))



def load_highscores():
    """Read highscores.txt into a sorted top-10 list of (name, score) tuples."""
    try:
        scores = []
        with open("highscores.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 2 and parts[1].isdigit():
                    scores.append((parts[0], int(parts[1])))
        # sort by score, high to low
        for i in range(len(scores) - 1):
            for j in range(len(scores) - 1 - i):
                if scores[j][1] < scores[j + 1][1]:
                    scores[j], scores[j + 1] = scores[j + 1], scores[j]
        return scores[:10]
    except FileNotFoundError:
        return []


def save_highscores(scores):
    """Write the (name, score) list back to highscores.txt, one per line."""
    with open("highscores.txt", "w") as f:
        for name, s in scores:
            f.write(f"{name},{s}\n")


def update_highscores(name, new_score, scores):
    """Add or update a player's score, re-sort, keep the top 10, and save."""
    if new_score <= 0:
        return scores
    # check if name is already in the list, update if new score is better
    found = False
    for i in range(len(scores)):
        if scores[i][0] == name:
            if new_score > scores[i][1]:
                scores[i] = (name, new_score)
            found = True
            break
    if not found:
        scores.append((name, new_score))
    # sort by score, high to low
    for i in range(len(scores) - 1):
        for j in range(len(scores) - 1 - i):
            if scores[j][1] < scores[j + 1][1]:
                scores[j], scores[j + 1] = scores[j + 1], scores[j]
    scores = scores[:10]
    save_highscores(scores)
    return scores


def draw_leaderboard(surface, scores, scroll=0):
    """Draw the high-score table with medal colors and scrolling."""
    draw_shadow_text(surface, "HIGH SCORES", small_font, (255, 215, 65), (0, 0, 0), (590, 112))
    pygame.draw.line(surface, (80, 200, 165), (410, 130), (770, 130), 1)
    if not scores:
        s = tiny_font.render("no scores yet", True, (160, 200, 190))
        surface.blit(s, s.get_rect(center=(590, 190)))
        return
    MEDAL = [(255, 215, 0), (195, 195, 210), (205, 127, 50)]
    visible = scores[scroll:scroll + 5]
    for i, (name, sc) in enumerate(visible):
        rank = scroll + i + 1
        ry = 152 + i * 28
        col = MEDAL[rank - 1] if rank <= 3 else (180, 220, 210)
        if rank == 1:
            draw_rect_alpha(surface, (255, 215, 0, 22), pygame.Rect(408, ry - 12, 362, 24), border_radius=4)
        rank_t = tiny_font.render(f"#{rank}", True, col)
        surface.blit(rank_t, rank_t.get_rect(midleft=(415, ry)))
        name_t = tiny_font.render(name, True, col)
        surface.blit(name_t, name_t.get_rect(midleft=(458, ry)))
        score_t = tiny_font.render(str(sc), True, col)
        surface.blit(score_t, score_t.get_rect(midright=(772, ry)))


def draw_name_entry(surface, name_input):
    """Draw the 'enter your name' popup with a blinking text cursor."""
    overlay = pygame.Surface((800, 400), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    surface.blit(overlay, (0, 0))
    px, py, pw, ph = 175, 95, 450, 200
    draw_rect_alpha(surface, (10, 20, 50, 240), pygame.Rect(px, py, pw, ph), border_radius=16)
    pygame.draw.rect(surface, (80, 200, 165), pygame.Rect(px, py, pw, ph), width=2, border_radius=16)
    draw_shadow_text(surface, "ENTER YOUR NAME", small_font, (255, 215, 65), (0, 0, 0), (400, 138))
    pygame.draw.line(surface, (80, 200, 165), (193, 158), (607, 158), 1)
    box = pygame.Rect(215, 172, 370, 50)
    draw_rect_alpha(surface, (20, 38, 65, 255), box, border_radius=10)
    pygame.draw.rect(surface, (80, 200, 165), box, 2, border_radius=10)
    blink = pygame.time.get_ticks() % 900 < 450
    txt = small_font.render(name_input + ("|" if blink else " "), True, (255, 255, 255))
    surface.blit(txt, txt.get_rect(midleft=(box.x + 12, box.centery)))
    hint = tiny_font.render("ENTER to confirm   |   ESC to clear", True, (160, 200, 190))
    surface.blit(hint, hint.get_rect(center=(400, 264)))


def draw_hud(surface, lives, dj_recharge_end):
    """Draw the heart lives and the double-jump cooldown bar."""
    for i in range(lives):
        surface.blit(heart_img, (10 + i * 38, 8))
    now = pygame.time.get_ticks()
    bar_x = 10
    bar_y = 46
    bar_w = 76
    bar_h = 7
    if dj_recharge_end > 0 and now < dj_recharge_end:
        elapsed = DJ_COOLDOWN - (dj_recharge_end - now)
        pct = elapsed / DJ_COOLDOWN
        draw_rect_alpha(surface, (30, 30, 70, 200), pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=4)
        draw_rect_alpha(surface, (100, 190, 255, 230), pygame.Rect(bar_x, bar_y, int(bar_w * pct), bar_h), border_radius=4)
        lbl = tiny_font.render("2nd jump", True, (150, 200, 240))
        surface.blit(lbl, lbl.get_rect(midleft=(bar_x + bar_w + 6, bar_y + bar_h // 2)))


def draw_pause_menu(surface):
    """Draw the paused overlay with resume/quit options."""
    overlay = pygame.Surface((800, 400), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 155))
    surface.blit(overlay, (0, 0))
    px, py, pw, ph = 230, 98, 340, 194
    draw_rect_alpha(surface, (10, 20, 50, 238), pygame.Rect(px, py, pw, ph), border_radius=16)
    pygame.draw.rect(surface, (80, 200, 165), pygame.Rect(px, py, pw, ph), width=2, border_radius=16)
    draw_shadow_text(surface, "PAUSED", game_font, (255, 215, 65), (0, 0, 0), (400, 143))
    pygame.draw.line(surface, (80, 200, 165), (248, 168), (552, 168), 1)
    r = tiny_font.render("[P]  resume", True, (200, 230, 215))
    surface.blit(r, r.get_rect(center=(400, 218)))
    q = tiny_font.render("[Q]  quit to menu", True, (200, 230, 215))
    surface.blit(q, q.get_rect(center=(400, 252)))


def draw_settings_screen(surface, selected_character):
    """Draw the settings popup for choosing a character."""
    overlay = pygame.Surface((800, 400), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    surface.blit(overlay, (0, 0))
    px, py, pw, ph = 148, 82, 504, 228
    draw_rect_alpha(surface, (10, 20, 50, 238), pygame.Rect(px, py, pw, ph), border_radius=16)
    pygame.draw.rect(surface, (80, 200, 165), pygame.Rect(px, py, pw, ph), width=2, border_radius=16)
    draw_shadow_text(surface, "SETTINGS", small_font, (255, 215, 65), (0, 0, 0), (400, 116))
    pygame.draw.line(surface, (80, 200, 165), (166, 138), (634, 138), 1)
    if selected_character == "soldier":
        char_label = "Soldier (Hard)"
    elif selected_character == "egg":
        char_label = "Egg (Medium)"
    else:
        char_label = "Player (Easy)"
    draw_shadow_text(surface, "CHARACTER", tiny_font, (160, 200, 190), (0, 0, 0), (308, 170))
    draw_shadow_text(surface, f"< {char_label} >", small_font, (200, 230, 215), (0, 0, 0), (308, 204))
    surface.blit(player_stand, player_stand.get_rect(center=(560, 196)))
    hint = tiny_font.render("LEFT / RIGHT to change   |   ESC to close", True, (160, 200, 190))
    surface.blit(hint, hint.get_rect(center=(400, 274)))


def draw_howtoplay_screen(surface):
    """Draw the how-to-play popup listing the controls."""
    overlay = pygame.Surface((800, 400), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    surface.blit(overlay, (0, 0))
    px, py, pw, ph = 120, 36, 560, 324
    draw_rect_alpha(surface, (10, 20, 50, 238), pygame.Rect(px, py, pw, ph), border_radius=16)
    pygame.draw.rect(surface, (80, 200, 165), pygame.Rect(px, py, pw, ph), width=2, border_radius=16)
    draw_shadow_text(surface, "HOW TO PLAY", small_font, (255, 215, 65), (0, 0, 0), (400, 68))
    pygame.draw.line(surface, (80, 200, 165), (138, 88), (662, 88), 1)
    lines = [
        ("SPACE/W/UP/click", "double jump  (2.5s cooldown)"),
        ("DOWN / S",      "duck under flying obstacles"),
        ("player char",   "enemies: egg + flying egg"),
        ("2 lives",       "each hit removes one life"),
        ("P",             "pause"),
        ("F11",           "fullscreen"),
    ]
    for i, (key, desc) in enumerate(lines):
        k = tiny_font.render(key, True, (255, 215, 65))
        d = tiny_font.render(desc, True, (200, 230, 215))
        surface.blit(k, k.get_rect(midright=(375, 112 + i * 28)))
        surface.blit(d, d.get_rect(midleft=(385, 112 + i * 28)))
    hint = tiny_font.render("ESC to close", True, (160, 200, 190))
    surface.blit(hint, hint.get_rect(center=(400, 342)))


# ---- init ----

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("graphics/sounds/candyland.mp3")
pygame.mixer.music.play(-1)

LOGICAL_W, LOGICAL_H = 800, 400
game_surface = pygame.Surface((LOGICAL_W, LOGICAL_H))
screen = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.RESIZABLE)
pygame.display.set_caption("Jumping Farid")
is_fullscreen = False
clock = pygame.time.Clock()
running = True
start_time = 0
score = 0
high_scores = load_highscores()
player_name = ""
name_input = ""
is_entering_name = True   # only ask once per session
leaderboard_scroll = 0

# game state
is_playing = False
is_paused = False
menu_screen = "main"       # "main" | "settings" | "howtoplay"
selected_character = "soldier"

# physics / gameplay
GROUND_Y = 300
PLAYER_STAND_Y = GROUND_Y + 4
JUMP_GRAVITY_START_SPEED = -22
DJ_COOLDOWN = 2500
players_gravity_speed = 0
is_ducking = False
lives = 2
jumps_remaining = 2
dj_recharge_end = 0
hit_invincible_end = 0
obstacle_speed = 7.0
spawn_interval = 1500


# ---- assets ----

SKY_SURF    = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
SKY2_SURF    = pygame.image.load("graphics/level/sky2.png").convert()
GROUND2_SURF = pygame.image.load("graphics/level/ground2.png").convert()
heart_img = pygame.transform.scale(pygame.image.load("graphics/heart.png").convert_alpha(), (32, 32))

game_font  = pygame.font.SysFont("Verdana", 50, bold=True)
small_font = pygame.font.SysFont("Verdana", 32, bold=True)
tiny_font  = pygame.font.SysFont("Verdana", 18)

_rnd.seed(42)
STARS = [(_rnd.randint(0, 800), _rnd.randint(8, 275)) for _ in range(60)]
menu_t = 0.0

# soldier sprites
_sol_walk = pygame.image.load(
    "graphics/onlineassets/Characters(100x100)/Soldier/Soldier/Soldier-Walk.png"
).convert_alpha()
_sol_idle = pygame.image.load(
    "graphics/onlineassets/Characters(100x100)/Soldier/Soldier/Soldier-Idle.png"
).convert_alpha()
sol_walk = [
    pygame.transform.scale(_sol_walk.subsurface(pygame.Rect(41 + i * 100, 38, 15, 19)), (55, 70))
    for i in range(4)
]
sol_jump  = pygame.transform.scale(_sol_idle.subsurface(pygame.Rect(41, 38, 15, 19)), (55, 70))
sol_duck  = pygame.transform.scale(sol_walk[0], (55, 35))
sol_stand = pygame.transform.rotozoom(sol_jump, 0, 2.0)

# egg sprites
_ew1 = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()
_ew2 = pygame.image.load("graphics/egg/egg_2.png").convert_alpha()
egg_walk  = [_ew1, _ew2]
egg_jump  = _ew1
egg_duck  = pygame.transform.scale(_ew1, (48, 24))
egg_stand = _ew1

# player sprites
_pw1 = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
_pw2 = pygame.image.load("graphics/player/player_walk_2.png").convert_alpha()
_pj  = pygame.image.load("graphics/player/player_jump.png").convert_alpha()
plr_walk  = [_pw1, _pw2]
plr_jump  = _pj
plr_duck  = pygame.transform.scale(_pw1, (48, 32))
plr_stand = _pw1

# flying egg obstacles (used when playing as player)
_fe1 = pygame.image.load("graphics/flyingegg/flyegg1.png").convert_alpha()
_fe2 = pygame.image.load("graphics/flyingegg/flyegg2.png").convert_alpha()
flyegg_frames      = [_fe1, _fe2]
flyegg_frame_index = 0
flyegg_surf        = flyegg_frames[0]

# ground egg obstacle (used when playing as player)
ground_egg_frame_index = 0
ground_egg_surf        = egg_walk[0]

# ground player obstacle (used when playing as egg) — flipped so it faces left
_gp1 = pygame.transform.flip(plr_walk[0], True, False)
_gp2 = pygame.transform.flip(plr_walk[1], True, False)
ground_player_frames      = [_gp1, _gp2]
ground_player_frame_index = 0
ground_player_surf        = ground_player_frames[0]

# active player sprites (default soldier)
player_walk  = sol_walk
player_jump  = sol_jump
player_duck  = sol_duck
player_stand = sol_stand
player_index = 0
player_surf  = player_walk[0]
player_rect  = player_surf.get_rect(bottomleft=(25, PLAYER_STAND_Y))

start_button_rect     = pygame.Rect(0, 0, 180, 42)
start_button_rect.center = (400, 316)
settings_button_rect  = pygame.Rect(0, 0, 136, 30)
settings_button_rect.center = (222, 363)
howtoplay_button_rect = pygame.Rect(0, 0, 148, 30)
howtoplay_button_rect.center = (580, 363)

# orc obstacle
_orc_sheet = pygame.image.load(
    "graphics/onlineassets/Characters(100x100)/Orc/Orc/Orc-Walk.png"
).convert_alpha()
orc_frames = [
    pygame.transform.flip(
        pygame.transform.scale(_orc_sheet.subsurface(pygame.Rect(44 + i * 100, 41, 22, 16)), (81, 69)),
        True, False
    )
    for i in range(4)
]
orc_frame_index = 0
orc_surf = orc_frames[orc_frame_index]

FLY_BOTTOM = GROUND_Y - 30

# arrow obstacle
arrow_w, arrow_h = 90, 26
arrow_surf = pygame.Surface((arrow_w, arrow_h), pygame.SRCALPHA)
_mid = arrow_h // 2
pygame.draw.rect(arrow_surf, (139, 90, 43), (24, _mid - 4, 44, 8))
pygame.draw.polygon(arrow_surf, (80, 80, 90),    [(0, _mid), (28, 0), (28, arrow_h)])
pygame.draw.polygon(arrow_surf, (200, 60, 60), [(66, _mid - 4), (90, 0),        (90, _mid - 4)])
pygame.draw.polygon(arrow_surf, (200, 60, 60), [(66, _mid + 4), (90, arrow_h),  (90, _mid + 4)])

obstacle_rect_list = []

# timers
obstacle_timer      = pygame.USEREVENT + 1
orc_animation_timer = pygame.USEREVENT + 2
difficulty_timer    = pygame.USEREVENT + 3
pygame.time.set_timer(obstacle_timer,      spawn_interval)
pygame.time.set_timer(orc_animation_timer, 150)
pygame.time.set_timer(difficulty_timer,    6000)


# ---- main loop ----

while running:
    menu_t += 0.04
    game_mouse  = screen_to_game(pygame.mouse.get_pos())
    btn_hover   = start_button_rect.collidepoint(game_mouse)
    set_hover   = settings_button_rect.collidepoint(game_mouse)
    htp_hover   = howtoplay_button_rect.collidepoint(game_mouse)
    # pick level assets based on character
    if selected_character in ("egg", "player"):
        sky_img = SKY2_SURF
        gnd_img = GROUND2_SURF
    else:
        sky_img = SKY_SURF
        gnd_img = GROUND_SURF

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # fullscreen toggle
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            is_fullscreen = not is_fullscreen
            if is_fullscreen:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                screen = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.RESIZABLE)

        elif is_playing:
            # pause toggle
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                is_paused = not is_paused

            if is_paused:
                # quit to menu
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    is_playing = False
                    is_paused  = False
                    pygame.mixer.music.load("graphics/sounds/candyland.mp3")
                    pygame.mixer.music.play(-1)
                    high_scores        = update_highscores(player_name, score, high_scores)
                    leaderboard_scroll = 0
            else:
                # double jump (space / W / up arrow / mouse click)
                jump_keys = (pygame.K_SPACE, pygame.K_w, pygame.K_UP)
                if (
                    event.type == pygame.KEYDOWN and event.key in jump_keys
                    or event.type == pygame.MOUSEBUTTONDOWN
                ) and jumps_remaining > 0 and not is_ducking:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    jumps_remaining -= 1
                    if jumps_remaining == 0 and player_rect.bottom < PLAYER_STAND_Y:
                        dj_recharge_end = pygame.time.get_ticks() + DJ_COOLDOWN
                # duck (S / down arrow)
                duck_keys = (pygame.K_DOWN, pygame.K_s)
                if event.type == pygame.KEYDOWN and event.key in duck_keys and player_rect.bottom >= PLAYER_STAND_Y:
                    is_ducking = True
                if event.type == pygame.KEYUP and event.key in duck_keys:
                    is_ducking = False
                # obstacle spawn
                if event.type == obstacle_timer:
                    if randint(0, 2):
                        if selected_character == "player":
                            obstacle_rect_list.append(ground_egg_surf.get_rect(bottomleft=(randint(900, 1100), PLAYER_STAND_Y)))
                        elif selected_character == "egg":
                            obstacle_rect_list.append(ground_player_surf.get_rect(bottomleft=(randint(900, 1100), PLAYER_STAND_Y)))
                        else:
                            obstacle_rect_list.append(orc_surf.get_rect(bottomleft=(randint(900, 1100), PLAYER_STAND_Y)))
                    else:
                        fly_x = randint(900, 1050)
                        if selected_character in ("player", "egg"):
                            for i in range(2):
                                obstacle_rect_list.append(flyegg_surf.get_rect(midbottom=(fly_x + i * 65, FLY_BOTTOM)))
                        else:
                            for i in range(2):
                                obstacle_rect_list.append(arrow_surf.get_rect(midbottom=(fly_x + i * 100, FLY_BOTTOM)))
                # orc + flyegg animation
                if event.type == orc_animation_timer:
                    orc_frame_index = (orc_frame_index + 1) % len(orc_frames)
                    orc_surf = orc_frames[orc_frame_index]
                    flyegg_frame_index = (flyegg_frame_index + 1) % len(flyegg_frames)
                    flyegg_surf = flyegg_frames[flyegg_frame_index]
                    ground_egg_frame_index = (ground_egg_frame_index + 1) % len(egg_walk)
                    ground_egg_surf = egg_walk[ground_egg_frame_index]
                    ground_player_frame_index = (ground_player_frame_index + 1) % len(ground_player_frames)
                    ground_player_surf = ground_player_frames[ground_player_frame_index]
                # difficulty ramp
                if event.type == difficulty_timer:
                    obstacle_speed  = min(obstacle_speed + 0.7, 16.0)
                    spawn_interval  = max(600, spawn_interval - 80)
                    pygame.time.set_timer(obstacle_timer, spawn_interval)

        elif is_entering_name:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and name_input:
                    player_name      = name_input
                    name_input       = ""
                    is_entering_name = False
                elif event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    name_input = ""
                elif len(name_input) < 12 and event.unicode.isalnum():
                    name_input += event.unicode

        else:
            # esc closes sub-screens
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                menu_screen = "main"

            elif menu_screen == "settings":
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    if selected_character == "soldier":
                        selected_character = "egg"
                    elif selected_character == "egg":
                        selected_character = "player"
                    else:
                        selected_character = "soldier"
                    apply_character(selected_character)

            elif menu_screen == "main":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    is_playing         = True
                    lives              = 2
                    jumps_remaining    = 2
                    dj_recharge_end    = 0
                    hit_invincible_end = 0
                    obstacle_speed     = 7.0
                    spawn_interval     = 1500
                    pygame.time.set_timer(obstacle_timer, spawn_interval)
                    pygame.mixer.music.load("graphics/sounds/ncs.mp3")
                    pygame.mixer.music.play(-1)
                    start_time = int(pygame.time.get_ticks() / 1000)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    gpos = screen_to_game(event.pos)
                    if start_button_rect.collidepoint(gpos):
                        is_playing         = True
                        lives              = 2
                        jumps_remaining    = 2
                        dj_recharge_end    = 0
                        hit_invincible_end = 0
                        obstacle_speed     = 7.0
                        spawn_interval     = 1500
                        pygame.time.set_timer(obstacle_timer, spawn_interval)
                        pygame.mixer.music.load("graphics/sounds/ncs.mp3")
                        pygame.mixer.music.play(-1)
                        start_time = int(pygame.time.get_ticks() / 1000)
                    elif settings_button_rect.collidepoint(gpos):
                        menu_screen = "settings"
                    elif howtoplay_button_rect.collidepoint(gpos):
                        menu_screen = "howtoplay"
                elif event.type == pygame.MOUSEWHEEL:
                    max_scroll = max(0, len(high_scores) - 5)
                    leaderboard_scroll = max(0, min(leaderboard_scroll - event.y, max_scroll))

    # ---- game update + draw ----

    if is_playing and not is_paused:
        game_surface.blit(sky_img, (0, 0))
        game_surface.blit(gnd_img, (0, GROUND_Y))
        score = display_score()

        # gravity
        players_gravity_speed += 1.5
        player_rect.y += players_gravity_speed
        if player_rect.bottom >= PLAYER_STAND_Y:
            player_rect.bottom = PLAYER_STAND_Y
            if pygame.time.get_ticks() >= dj_recharge_end:
                jumps_remaining = 2   # double jump recharged
            else:
                jumps_remaining = max(jumps_remaining, 1)   # at least 1 jump while on ground

        player_animation()
        # duck/stand height
        stand_h = player_walk[0].get_height()
        if is_ducking and player_rect.bottom >= PLAYER_STAND_Y:
            player_rect.height = max(stand_h // 2, 24)
            player_rect.bottom = PLAYER_STAND_Y
        elif player_rect.bottom >= PLAYER_STAND_Y:
            player_rect.height = stand_h
            player_rect.bottom = PLAYER_STAND_Y

        # flash during post-hit invincibility
        now = pygame.time.get_ticks()
        if not (now < hit_invincible_end and now % 200 < 100):
            game_surface.blit(player_surf, player_rect)

        # obstacles
        obstacle_rect_list = obstacle_movement(obstacle_rect_list, obstacle_speed)

        draw_hud(game_surface, lives, dj_recharge_end)

        # collision - skip during post-hit invincibility
        is_invincible = now < hit_invincible_end
        if not collisions(player_rect, obstacle_rect_list) and not is_invincible:
            lives -= 1
            hit_invincible_end = pygame.time.get_ticks() + 1500
            if lives <= 0:
                is_playing = False
                pygame.mixer.music.load("graphics/sounds/candyland.mp3")
                pygame.mixer.music.play(-1)
                high_scores        = update_highscores(player_name, score, high_scores)
                leaderboard_scroll = 0

    elif is_playing and is_paused:
        # draw paused frame
        game_surface.blit(sky_img, (0, 0))
        game_surface.blit(gnd_img, (0, GROUND_Y))
        display_score()
        for obs in obstacle_rect_list:
            if obs.bottom >= PLAYER_STAND_Y:
                if selected_character == "player":
                    game_surface.blit(ground_egg_surf, obs)
                elif selected_character == "egg":
                    game_surface.blit(ground_player_surf, obs)
                else:
                    game_surface.blit(orc_surf, obs)
            elif selected_character in ("player", "egg"):
                game_surface.blit(flyegg_surf, obs)
            else:
                game_surface.blit(arrow_surf, obs)
        game_surface.blit(player_surf, player_rect)
        draw_hud(game_surface, lives, dj_recharge_end)
        draw_pause_menu(game_surface)

    else:
        # menu
        game_surface.blit(sky_img, (0, 0))
        game_surface.blit(gnd_img, (0, GROUND_Y))

        # reset player for menu screen
        obstacle_rect_list.clear()
        player_rect.height     = player_walk[0].get_height()
        player_rect.bottomleft = (25, PLAYER_STAND_Y)
        players_gravity_speed  = 0
        is_ducking = False

        # full-width panel
        panel = pygame.Surface((760, 362), pygame.SRCALPHA)
        panel.fill((10, 20, 50, 185))
        game_surface.blit(panel, (20, 18))
        pygame.draw.rect(game_surface, (80, 200, 165), pygame.Rect(20, 18, 760, 362), width=2)
        pygame.draw.line(game_surface, (140, 255, 215), (22, 378), (22, 20))
        pygame.draw.line(game_surface, (140, 255, 215), (22, 20), (778, 20))

        draw_shadow_text(game_surface, "jumping farid", game_font, (111, 196, 169), (0, 0, 0), (400, 55))

        pygame.draw.line(game_surface, (80, 200, 165), (35,  90), (765,  90), 1)
        pygame.draw.line(game_surface, (80, 200, 165), (400, 94), (400, 298), 1)
        pygame.draw.line(game_surface, (80, 200, 165), (35, 301), (765, 301), 1)

        # left column - player sprite + last score
        game_surface.blit(player_stand, player_stand.get_rect(center=(215, 188)))
        if score > 0:
            draw_shadow_text(game_surface, f"Score: {score}", small_font, (255, 215, 65), (0, 0, 0), (215, 272))

        # right column - leaderboard
        draw_leaderboard(game_surface, high_scores, leaderboard_scroll)

        # START button
        start_button_rect.center = (400, 316)
        button_label = "START" if score == 0 else "RESTART"
        pygame.draw.rect(game_surface, (20, 70, 50), start_button_rect.move(4, 4), border_radius=10)
        face_rect = start_button_rect.move(3, 3) if btn_hover else start_button_rect
        pygame.draw.rect(game_surface, (100, 220, 170) if btn_hover else (60, 170, 130), face_rect, border_radius=10)
        pygame.draw.rect(game_surface, (120, 240, 195), face_rect, width=2, border_radius=10)
        lbl = small_font.render(button_label, False, "white")
        game_surface.blit(lbl, lbl.get_rect(center=face_rect.center))

        # SETTINGS button
        settings_button_rect.center = (222, 363)
        pygame.draw.rect(game_surface, (20, 55, 42), settings_button_rect.move(3, 3), border_radius=8)
        s_face = settings_button_rect.move(2, 2) if set_hover else settings_button_rect
        pygame.draw.rect(game_surface, (70, 145, 108) if set_hover else (45, 110, 80), s_face, border_radius=8)
        pygame.draw.rect(game_surface, (80, 210, 165), s_face, width=1, border_radius=8)
        s_txt = tiny_font.render("SETTINGS", True, "white")
        game_surface.blit(s_txt, s_txt.get_rect(center=s_face.center))

        # HOW TO PLAY button
        howtoplay_button_rect.center = (580, 363)
        pygame.draw.rect(game_surface, (20, 55, 42), howtoplay_button_rect.move(3, 3), border_radius=8)
        h_face = howtoplay_button_rect.move(2, 2) if htp_hover else howtoplay_button_rect
        pygame.draw.rect(game_surface, (70, 145, 108) if htp_hover else (45, 110, 80), h_face, border_radius=8)
        pygame.draw.rect(game_surface, (80, 210, 165), h_face, width=1, border_radius=8)
        h_txt = tiny_font.render("HOW TO PLAY", True, "white")
        game_surface.blit(h_txt, h_txt.get_rect(center=h_face.center))

        # overlay popups
        if menu_screen == "settings":
            draw_settings_screen(game_surface, selected_character)
        elif menu_screen == "howtoplay":
            draw_howtoplay_screen(game_surface)
        if is_entering_name:
            draw_name_entry(game_surface, name_input)

    # letterbox scale to window
    scale, ox, oy, nw, nh = get_letterbox()
    screen.fill((0, 0, 0))
    screen.blit(pygame.transform.scale(game_surface, (nw, nh)), (ox, oy))
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
