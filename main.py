"""Dino Game in Python

A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @bassemfarid (anthropic), no one or nothing else. 🤖 hmm r we sure abt that gang.
"""

import pygame
from random import randint
import os
import math
import random as _rnd

def display_score():
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = game_font.render(f"Score: {current_time}", False, (64, 64, 64))
    score_rect = score_surf.get_rect(center = (400, 50))
    game_surface.blit(score_surf, score_rect)
    return current_time

def obstacle_movement(obstacle_list):

    if obstacle_list:
        for obstacle_rect in obstacle_list:
            obstacle_rect.x -= 7


            if obstacle_rect.bottom >= PLAYER_STAND_Y:
                game_surface.blit(orc_surf, obstacle_rect)
            else:
                game_surface.blit(arrow_surf, obstacle_rect)

        obstacle_list = [obstacle for obstacle in obstacle_list if obstacle.x > -100]
        return obstacle_list
    else: return []

def collisions(player, obstacles):
    if obstacles:
        player_hitbox = player.inflate(-12, -18)
        for obstacle_rect in obstacles:
            if player_hitbox.colliderect(obstacle_rect.inflate(-18, -16)):
                return False
    return True

def player_animation():
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




def get_letterbox():
    sw, sh = screen.get_size()
    scale = min(sw / LOGICAL_W, sh / LOGICAL_H)
    nw, nh = int(LOGICAL_W * scale), int(LOGICAL_H * scale)
    ox, oy = (sw - nw) // 2, (sh - nh) // 2
    return scale, ox, oy, nw, nh


def screen_to_game(pos):
    scale, ox, oy, _, _ = get_letterbox()
    return (int((pos[0] - ox) / scale), int((pos[1] - oy) / scale))


def draw_rect_alpha(surface, color_rgba, rect, border_radius=0, width=0):
    tmp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(tmp, color_rgba, tmp.get_rect(), width=width, border_radius=border_radius)
    surface.blit(tmp, rect.topleft)


def draw_shadow_text(surface, text, font, color, shadow_col, center):
    shadow = font.render(text, True, shadow_col)
    txt = font.render(text, True, color)
    surface.blit(shadow, shadow.get_rect(center=(center[0] + 3, center[1] + 3)))
    surface.blit(txt, txt.get_rect(center=center))


def load_highscores():
    try:
        scores = []
        with open("highscores.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 2 and parts[1].isdigit():
                    scores.append((parts[0], int(parts[1])))
        return sorted(scores, key=lambda x: x[1], reverse=True)[:10]
    except FileNotFoundError:
        return []


def save_highscores(scores):
    with open("highscores.txt", "w") as f:
        for name, s in scores:
            f.write(f"{name},{s}\n")


def update_highscores(name, new_score, scores):
    if new_score > 0:
        scores = sorted(scores + [(name, new_score)], key=lambda x: x[1], reverse=True)[:10]
        save_highscores(scores)
    return scores


def draw_leaderboard(surface, scores):
    draw_shadow_text(surface, "HIGH SCORES", small_font, (255, 215, 65), (0, 0, 0), (585, 118))
    if not scores:
        s = tiny_font.render("no scores yet", True, (160, 200, 190))
        surface.blit(s, s.get_rect(center=(585, 175)))
        return
    for i, (name, sc) in enumerate(scores[:5]):
        color = (255, 215, 65) if i == 0 else (200, 230, 215)
        entry = tiny_font.render(f"{i + 1}.  {name}  -  {sc}", True, color)
        surface.blit(entry, entry.get_rect(midleft=(415, 152 + i * 27)))


def draw_name_entry(surface, name_input):
    overlay = pygame.Surface((800, 400), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    px, py, pw, ph = 180, 108, 440, 178
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    panel.fill((10, 20, 50, 230))
    surface.blit(panel, (px, py))
    pygame.draw.rect(surface, (80, 200, 165), pygame.Rect(px, py, pw, ph), width=2)
    pygame.draw.line(surface, (140, 255, 215), (px + 2, py + ph - 2), (px + 2, py + 2))
    pygame.draw.line(surface, (140, 255, 215), (px + 2, py + 2), (px + pw - 2, py + 2))
    draw_shadow_text(surface, "ENTER YOUR NAME", small_font, (255, 215, 65), (0, 0, 0), (400, 148))
    box = pygame.Rect(210, 173, 380, 44)
    pygame.draw.rect(surface, (25, 45, 75), box)
    pygame.draw.rect(surface, (80, 200, 165), box, 2)
    blink = pygame.time.get_ticks() % 900 < 450
    txt = small_font.render(name_input + ("|" if blink else " "), True, (255, 255, 255))
    surface.blit(txt, txt.get_rect(midleft=(box.x + 10, box.centery)))
    hint = tiny_font.render("ENTER to confirm   |   ESC to cancel", True, (160, 200, 190))
    surface.blit(hint, hint.get_rect(center=(400, 258)))


# Initialize Pygame and create a window
pygame.init()

#music 
pygame.mixer.init()
pygame.mixer.music.load("graphics/sounds/candyland.mp3")
pygame.mixer.music.play(-1)


LOGICAL_W, LOGICAL_H = 800, 400
game_surface = pygame.Surface((LOGICAL_W, LOGICAL_H))
screen = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.RESIZABLE)
pygame.display.set_caption("Jumping Farid")
is_fullscreen = False
clock = pygame.time.Clock()
running = True  # Pygame main loop, kills pygame when False
start_time = 0
score = 0
high_scores = load_highscores()
player_name = ""
name_input = ""
is_entering_name = False

# Game state variables
is_playing = False  # Whether in game or in menu
GROUND_Y = 300  # The Y-coordinate of the ground level
PLAYER_STAND_Y = GROUND_Y + 4  # Player rect.bottom when standing; +4 accounts for ~4px transparent at bottom of scaled sprite
JUMP_GRAVITY_START_SPEED = -22  # The speed at which the player jumps
players_gravity_speed = 0  # The current speed at which the player falls
is_ducking = False

# Load level assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
# 800x400 background image
menu_bg_surf = None
if os.path.exists("graphics/level/menu_bg.png"):
    _mb = pygame.image.load("graphics/level/menu_bg.png").convert()
    menu_bg_surf = pygame.transform.scale(_mb, (800, 400))
# loading new fonts, i am using verdana cuz its clean
game_font = pygame.font.SysFont("Verdana", 50, bold=True)
small_font = pygame.font.SysFont("Verdana", 32, bold=True)
tiny_font = pygame.font.SysFont("Verdana", 18)
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

# Stars for menu (seeded so they don't jump each run)
_rnd.seed(42)
STARS = [(_rnd.randint(0, 800), _rnd.randint(8, 275)) for _ in range(60)]
menu_t = 0.0

# Load assets
# legacy stickman
"""
player_walk_1 = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_walk_2 = pygame.image.load("graphics/player/player_walk_2.png").convert_alpha()
player_jump = pygame.image.load("graphics/player/player_jump.png").convert_alpha()
"""
# soldier player - 4 walk frames, idle frame as jump
_sol_walk = pygame.image.load(
    "graphics/onlineassets/Characters(100x100)/Soldier/Soldier/Soldier-Walk.png"
).convert_alpha()
_sol_idle = pygame.image.load(
    "graphics/onlineassets/Characters(100x100)/Soldier/Soldier/Soldier-Idle.png"
).convert_alpha()
# pixels live at x=41-55 y=38-56 in each 100x100 frame; crop tight so feet land at rect bottom
player_walk_1 = pygame.transform.scale(_sol_walk.subsurface(pygame.Rect(41, 38, 15, 19)), (55, 70))
player_walk_2 = pygame.transform.scale(_sol_walk.subsurface(pygame.Rect(141, 38, 15, 19)), (55, 70))
player_walk_3 = pygame.transform.scale(_sol_walk.subsurface(pygame.Rect(241, 38, 15, 19)), (55, 70))
player_walk_4 = pygame.transform.scale(_sol_walk.subsurface(pygame.Rect(341, 38, 15, 19)), (55, 70))
player_jump = pygame.transform.scale(_sol_idle.subsurface(pygame.Rect(41, 38, 15, 19)), (55, 70))
player_index = 0
player_walk = [player_walk_1, player_walk_2, player_walk_3, player_walk_4]
player_duck = pygame.transform.scale(player_walk_1, (55, 35))  # duck 

player_surf = player_walk[player_index]
player_rect = player_surf.get_rect(bottomleft=(25, PLAYER_STAND_Y))
player_gravity = 0

#Into Screen

player_stand = pygame.transform.rotozoom(player_jump, 0, 2.0)
player_stand_rect = player_stand.get_rect(center=(400, 160))

game_name = game_font.render("jumping farid", False, (111, 196, 169))
game_name_rect = game_name.get_rect(center=(400, 80))

# game_message = game_font.render("Press SPACE to run!", False, (111, 196, 169))
# game_message_rect = game_message.get_rect(center=(400, 320))
start_button_rect = pygame.Rect(0, 0, 230, 44)
start_button_rect.center = (400, 333)


#Obstacles
# legacy eggs
"""
egg_frame_1 = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()
egg_frame_2 = pygame.image.load("graphics/egg/egg_2.png").convert_alpha()
egg_frames = [egg_frame_1, egg_frame_2]
egg_frame_index = 0
egg_surf = egg_frames[egg_frame_index]

flyegg_frame_1 = pygame.image.load("graphics/flyingegg/flyegg1.png").convert_alpha()
flyegg_frame_2 = pygame.image.load("graphics/flyingegg/flyegg2.png").convert_alpha()
flyegg_frames = [flyegg_frame_1, flyegg_frame_2]
flyegg_frame_index = 0
flyegg_surf = flyegg_frames[flyegg_frame_index]
"""

# orc - 4 frames from walk sheet (each 100x100), scaled to 80x80
_orc_sheet = pygame.image.load(
    "graphics/onlineassets/Characters(100x100)/Orc/Orc/Orc-Walk.png"
).convert_alpha()
# pixels live at x=44-65 y=41-56 in each 100x100 frame; crop tight so feet land at rect bottom
orc_frame_1 = pygame.transform.flip(pygame.transform.scale(_orc_sheet.subsurface(pygame.Rect(44, 41, 22, 16)), (81, 69)), True, False)
orc_frame_2 = pygame.transform.flip(pygame.transform.scale(_orc_sheet.subsurface(pygame.Rect(144, 41, 22, 16)), (81, 69)), True, False)
orc_frame_3 = pygame.transform.flip(pygame.transform.scale(_orc_sheet.subsurface(pygame.Rect(244, 41, 22, 16)), (81, 69)), True, False)
orc_frame_4 = pygame.transform.flip(pygame.transform.scale(_orc_sheet.subsurface(pygame.Rect(344, 41, 22, 16)), (81, 69)), True, False)
orc_frames = [orc_frame_1, orc_frame_2, orc_frame_3, orc_frame_4]
orc_frame_index = 0
orc_surf = orc_frames[orc_frame_index]

# flying obstacle bottom y - hits standing player, misses ducking player
FLY_BOTTOM = GROUND_Y - 30

# Arrow obstacle surface (points left toward player)
arrow_w, arrow_h = 65, 18
arrow_surf = pygame.Surface((arrow_w, arrow_h), pygame.SRCALPHA)
_mid = arrow_h // 2
pygame.draw.rect(arrow_surf, (139, 90, 43), (15, _mid - 3, 50, 6))           # wooden shaft
pygame.draw.polygon(arrow_surf, (80, 80, 90), [(0, _mid), (18, 0), (18, arrow_h)])  # metal head
pygame.draw.polygon(arrow_surf, (200, 60, 60), [(50, _mid - 3), (65, 0), (65, _mid - 3)])  # top fletching
pygame.draw.polygon(arrow_surf, (200, 60, 60), [(50, _mid + 3), (65, arrow_h), (65, _mid + 3)])  # bottom fletching


obstacle_rect_list = []

# Timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

orc_animation_timer = pygame.USEREVENT + 2
pygame.time.set_timer(orc_animation_timer, 150)


while running:
    menu_t += 0.04
    game_mouse = screen_to_game(pygame.mouse.get_pos())
    btn_hover = start_button_rect.collidepoint(game_mouse)

    # Poll for events
    for event in pygame.event.get():
        # pygame.QUIT --> user clicked X to close your window
        if event.type == pygame.QUIT:
            running = False

        # F11 toggles fullscreen (letterboxed to preserve 2:1 aspect)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            is_fullscreen = not is_fullscreen
            if is_fullscreen:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                screen = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.RESIZABLE)

        elif is_playing:
            # jump - space or click, only on ground, not while ducking
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                or event.type == pygame.MOUSEBUTTONDOWN
            ) and player_rect.bottom >= PLAYER_STAND_Y and not is_ducking:
                players_gravity_speed = JUMP_GRAVITY_START_SPEED
            # duck - hold down arrow
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN and player_rect.bottom >= PLAYER_STAND_Y:
                is_ducking = True
            if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
                is_ducking = False
        elif is_entering_name:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and name_input:
                    player_name = name_input
                    name_input = ""
                    is_entering_name = False
                    is_playing = True
                    pygame.mixer.music.load("graphics/sounds/ncs.mp3")
                    pygame.mixer.music.play(-1)
                    start_time = int(pygame.time.get_ticks() / 1000)
                elif event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    name_input = ""
                    is_entering_name = False
                elif len(name_input) < 12 and event.unicode.isalnum():
                    name_input += event.unicode
        else:
            # space or button click → open name entry screen
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_entering_name = True
            elif event.type == pygame.MOUSEBUTTONDOWN and start_button_rect.collidepoint(screen_to_game(event.pos)):
                is_entering_name = True
        if is_playing:
            if event.type == obstacle_timer:
                if randint(0, 2):
                    obstacle_rect_list.append(orc_surf.get_rect(bottomleft=(randint(900, 1100), PLAYER_STAND_Y)))
                else:
                    arrow_x = randint(900, 1100)
                    for i in range(3):
                        obstacle_rect_list.append(arrow_surf.get_rect(midbottom=(arrow_x, FLY_BOTTOM - i * 25)))

            if event.type == orc_animation_timer:
                orc_frame_index = (orc_frame_index + 1) % len(orc_frames)
                orc_surf = orc_frames[orc_frame_index]

    if is_playing:
        # Blit the level assets
        game_surface.blit(SKY_SURF, (0, 0))
        game_surface.blit(GROUND_SURF, (0, GROUND_Y))
        """
        pygame.draw.rect(screen, "#c0e8ec", score_rect)
        pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
        screen.blit(score_surf, score_rect)
        """
        score = display_score()
        # Adjust egg's horizontal location then blit it

       # egg_rect.x -= 5
        #if egg_rect.right <= 0:
         #   egg_rect.left = 800
        #screen.blit(egg_surf, egg_rect)

        # Player movement
        players_gravity_speed += 1.5
        player_rect.y += players_gravity_speed
        if player_rect.bottom > PLAYER_STAND_Y:
            player_rect.bottom = PLAYER_STAND_Y
        player_animation()
        # shrink/restore collision rect for duck
        if is_ducking and player_rect.bottom >= PLAYER_STAND_Y:
            player_rect.height = 35
            player_rect.bottom = PLAYER_STAND_Y
        elif player_rect.bottom >= PLAYER_STAND_Y:
            player_rect.height = 70
            player_rect.bottom = PLAYER_STAND_Y
        game_surface.blit(player_surf, player_rect)

        # Obstacle movement
        obstacle_rect_list = obstacle_movement(obstacle_rect_list)

        # collisions - if player got hit go back to menu and bring the music back
        was_playing = is_playing
        is_playing = collisions(player_rect, obstacle_rect_list)
        if was_playing and not is_playing:
            pygame.mixer.music.load("graphics/sounds/candyland.mp3")
            pygame.mixer.music.play(-1)
            high_scores = update_highscores(player_name, score, high_scores)


    # Menu / game over screen
    else:
        game_surface.blit(SKY_SURF, (0, 0))
        game_surface.blit(GROUND_SURF, (0, GROUND_Y))

        # Reset player state
        obstacle_rect_list.clear()
        player_rect.height = 70
        player_rect.bottomleft = (25, PLAYER_STAND_Y)
        players_gravity_speed = 0
        is_ducking = False

        # Full-width panel (760x362, nearly the whole 800x400 canvas)
        panel = pygame.Surface((760, 362), pygame.SRCALPHA)
        panel.fill((10, 20, 50, 185))
        game_surface.blit(panel, (20, 18))
        pygame.draw.rect(game_surface, (80, 200, 165), pygame.Rect(20, 18, 760, 362), width=2)
        pygame.draw.line(game_surface, (140, 255, 215), (22, 378), (22, 20))
        pygame.draw.line(game_surface, (140, 255, 215), (22, 20), (778, 20))

        # Title across full width
        draw_shadow_text(game_surface, "jumping farid", game_font, (111, 196, 169), (0, 0, 0), (400, 55))

        # Dividers: below title | vertical column split | above bottom strip
        pygame.draw.line(game_surface, (80, 200, 165), (35, 90), (765, 90), 1)
        pygame.draw.line(game_surface, (80, 200, 165), (400, 94), (400, 298), 1)
        pygame.draw.line(game_surface, (80, 200, 165), (35, 301), (765, 301), 1)

        # Left column: player sprite + last score
        game_surface.blit(player_stand, player_stand.get_rect(center=(215, 188)))
        if score > 0:
            draw_shadow_text(game_surface, f"Score: {score}", small_font, (255, 215, 65), (0, 0, 0), (215, 272))

        # Right column: leaderboard
        draw_leaderboard(game_surface, high_scores)

        # Bottom strip: button + controls hint
        start_button_rect.center = (400, 330)
        button_label = "START" if score == 0 else "PLAY AGAIN"
        pygame.draw.rect(game_surface, (35, 110, 85), start_button_rect.move(4, 4))
        face_rect = start_button_rect.move(4, 4) if btn_hover else start_button_rect
        pygame.draw.rect(game_surface, (80, 200, 155) if btn_hover else (55, 160, 120), face_rect)
        pygame.draw.rect(game_surface, (80, 210, 165), face_rect, width=2)
        btn_text = small_font.render(button_label, False, "white")
        game_surface.blit(btn_text, btn_text.get_rect(center=face_rect.center))
        hint = tiny_font.render("SPACE / click = jump   |   DOWN = duck   |   F11 = fullscreen", False, (160, 200, 190))
        game_surface.blit(hint, hint.get_rect(center=(400, 366)))

        # Name entry overlay drawn last so it sits on top
        if is_entering_name:
            draw_name_entry(game_surface, name_input)

    # Scale game_surface to the actual window (letterboxed so fullscreen keeps aspect ratio)
    scale, ox, oy, nw, nh = get_letterbox()
    screen.fill((0, 0, 0))
    screen.blit(pygame.transform.scale(game_surface, (nw, nh)), (ox, oy))
    pygame.display.flip()

    clock.tick(60)  # Limits game loop to 60 FPS

pygame.quit()
