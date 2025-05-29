import asyncio
import pygame
from pygame import mixer
from PC.fighter import Fighter
import random

async def main():
    mixer.init()
    pygame.init()

    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Brawler Mobile")

    # Touch control variables
    touch_controls = {
        'left': False,
        'right': False,
        'up': False,
        'punch': False,
        'sword': False
    }
    
    # Touch button rectangles (bottom of screen)
    button_size = 80
    button_margin = 20
    button_y = SCREEN_HEIGHT - button_size - 10
    
    # Movement buttons (left side)
    left_btn = pygame.Rect(button_margin, button_y, button_size, button_size)
    right_btn = pygame.Rect(button_margin + button_size + 10, button_y, button_size, button_size)
    up_btn = pygame.Rect(button_margin + (button_size + 10) * 2, button_y, button_size, button_size)
    
    # Action buttons (right side)
    punch_btn = pygame.Rect(SCREEN_WIDTH - button_margin - button_size * 2 - 10, button_y, button_size, button_size)
    sword_btn = pygame.Rect(SCREEN_WIDTH - button_margin - button_size, button_y, button_size, button_size)
    
    # Button colors
    btn_color = (70, 70, 70, 180)  # Semi-transparent gray
    btn_active_color = (120, 120, 120, 180)  # Lighter when pressed
    btn_border_color = (200, 200, 200)

    # Quit button
    quit_font = pygame.font.Font(None, 36)
    quit_img = quit_font.render("X", True, (255, 0, 0))
    quit_rect = quit_img.get_rect(topright=(SCREEN_WIDTH - 10, 10))

    clock = pygame.time.Clock()
    FPS = 60

    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)

    intro_count = 3
    last_count_update = pygame.time.get_ticks()
    score = [0, 0]
    round_over = False
    ROUND_OVER_COOLDOWN = 2000

    bg_image = pygame.image.load("assets/images/background/background.jpg").convert_alpha()
    victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()
    count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
    score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
    button_font = pygame.font.Font("assets/fonts/turok.ttf", 40)

    pygame.mixer.music.load("assets/audio/music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, 0.0, 5000)
    sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
    magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")

    # Character config
    CHARACTERS = {
        "captain": {
            "sheet": "assets/images/warrior/Sprites/warrior.png",
            "data": [162, 0.86, [0, -44]],
            "steps": [1, 6, 1, 6, 6, 1, 1],
            "sound": sword_fx
        },
        "ironman": {
            "sheet": "assets/images/ironman/Sprites/ironman.png",
            "data": [162, 0.87, [0, -43]],
            "steps": [1, 6, 1, 6, 6, 1, 1],
            "sound": magic_fx
        },
        "thanos": {
            "sheet": "assets/images/wizard/Sprites/wizard.png",
            "data": [162, 0.9, [112, -38]],
            "steps": [1, 6, 1, 6, 6, 1, 1],
            "sound": magic_fx
        },
        "loki": {
            "sheet": "assets/images/loki/Sprites/loki.png",
            "data": [162, 1.02, [112, -26]],
            "steps": [1, 6, 1, 6, 6, 1, 1],
            "sound": sword_fx
        }
    }

    def draw_text(text, font, color, x, y):
        screen.blit(font.render(text, True, color), (x, y))

    def draw_bg():
        screen.blit(pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT - 100)), (0, 0))

    def draw_health_bar(health, x, y):
        ratio = health / 100
        pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
        pygame.draw.rect(screen, RED, (x, y, 400, 30))
        pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))

    def draw_touch_controls():
        # Create semi-transparent overlay for controls
        overlay = pygame.Surface((SCREEN_WIDTH, 100))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, SCREEN_HEIGHT - 100))
        
        # Draw movement buttons
        # Left arrow
        color = btn_active_color if touch_controls['left'] else btn_color
        pygame.draw.rect(screen, color, left_btn)
        pygame.draw.rect(screen, btn_border_color, left_btn, 3)
        draw_text("←", button_font, WHITE, left_btn.centerx - 15, left_btn.centery - 20)
        
        # Right arrow
        color = btn_active_color if touch_controls['right'] else btn_color
        pygame.draw.rect(screen, color, right_btn)
        pygame.draw.rect(screen, btn_border_color, right_btn, 3)
        draw_text("→", button_font, WHITE, right_btn.centerx - 15, right_btn.centery - 20)
        
        # Up arrow (jump)
        color = btn_active_color if touch_controls['up'] else btn_color
        pygame.draw.rect(screen, color, up_btn)
        pygame.draw.rect(screen, btn_border_color, up_btn, 3)
        draw_text("↑", button_font, WHITE, up_btn.centerx - 15, up_btn.centery - 20)
        
        # Punch button
        color = btn_active_color if touch_controls['punch'] else btn_color
        pygame.draw.rect(screen, color, punch_btn)
        pygame.draw.rect(screen, btn_border_color, punch_btn, 3)
        draw_text("👊", button_font, WHITE, punch_btn.centerx - 20, punch_btn.centery - 20)
        
        # Sword button
        color = btn_active_color if touch_controls['sword'] else btn_color
        pygame.draw.rect(screen, color, sword_btn)
        pygame.draw.rect(screen, btn_border_color, sword_btn, 3)
        draw_text("⚔️", button_font, WHITE, sword_btn.centerx - 20, sword_btn.centery - 20)

    def handle_touch_input(pos, pressed):
        """Handle touch/mouse input for mobile controls"""
        if left_btn.collidepoint(pos):
            touch_controls['left'] = pressed
        elif right_btn.collidepoint(pos):
            touch_controls['right'] = pressed
        elif up_btn.collidepoint(pos):
            touch_controls['up'] = pressed
        elif punch_btn.collidepoint(pos):
            touch_controls['punch'] = pressed
        elif sword_btn.collidepoint(pos):
            touch_controls['sword'] = pressed

    def get_mobile_keys():
        """Convert touch controls to pygame key presses"""
        keys = pygame.key.get_pressed()
        # Create a mutable copy
        mobile_keys = list(keys)
        
        # Override with touch controls for Player 1
        if touch_controls['left']:
            mobile_keys[pygame.K_a] = True
        if touch_controls['right']:
            mobile_keys[pygame.K_d] = True
        if touch_controls['up']:
            mobile_keys[pygame.K_w] = True
        if touch_controls['punch']:
            mobile_keys[pygame.K_r] = True
        if touch_controls['sword']:
            mobile_keys[pygame.K_t] = True
            
        return mobile_keys

    def control_bot(bot, target, round_over):
        if round_over or not bot.alive or not target.alive:
            return

        # Always decrement cooldown
        if bot.attack_cooldown > 0:
            bot.attack_cooldown -= 1

        distance = target.rect.centerx - bot.rect.centerx
        abs_distance = abs(distance)
        vertical_gap = abs(target.rect.bottom - bot.rect.bottom)

        # --- LOCK FACING for bot during attack only ---
        if not hasattr(bot, 'pre_attack_flip'):
            bot.pre_attack_flip = bot.flip

        if bot.attacking:
            bot.flip = bot.pre_attack_flip
            if bot.frame_index == 0:
                bot.attack_type = 0
            bot.running = False
            return
        else:
            if target.rect.centerx > bot.rect.centerx:
                bot.flip = False
            else:
                bot.flip = True
            bot.pre_attack_flip = bot.flip

        IN_ATTACK_RANGE = abs_distance < 1 and vertical_gap < 1

        # JUMP logic
        if target.jump and not bot.jump:
            bot.vel_y = -30
            bot.jump = True
        else:
            if not hasattr(bot, 'last_jump'):
                bot.last_jump = pygame.time.get_ticks()
                bot.next_jump_delay = random.randint(1200, 3000)
            now = pygame.time.get_ticks()
            if now - bot.last_jump > bot.next_jump_delay:
                if not bot.jump:
                    bot.vel_y = -30
                    bot.jump = True
                bot.last_jump = now
                bot.next_jump_delay = random.randint(1200, 3000)

        if IN_ATTACK_RANGE and bot.attack_cooldown == 0 and not bot.attacking:
            bot.attack_type = random.choice([1, 2])
            bot.attack(target)
            bot.running = False
            return

        if not IN_ATTACK_RANGE:
            bot.running = True
            if distance > 0:
                bot.rect.x += 5
            else:
                bot.rect.x -= 5
        else:
            bot.running = False

    async def select_game_mode():
        font = pygame.font.Font("assets/fonts/turok.ttf", 40)
        selecting = True
        while selecting:
            screen.fill((0, 0, 0))
            draw_text("Choose Game Mode", font, WHITE, 320, 100)
            draw_text("Press 1: 1 Player (vs Bot)", font, YELLOW, 300, 200)
            draw_text("Press 2: 2 Player", font, YELLOW, 300, 270)
            draw_text("Mobile Version - Touch Controls Added", score_font, WHITE, 250, 350)
            pygame.display.update()
            await asyncio.sleep(0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return 1
                    elif event.key == pygame.K_2:
                        return 2

    HEROES = ["captain", "ironman"]
    VILLAINS = ["thanos", "loki"]

    fighter_1 = fighter_2 = None
    selecting = True
    player1_done = False
    player2_side = None

    game_mode = await select_game_mode()

    def draw_selection_screen(p1_choice=None):
        draw_bg()
        draw_text("Player 1: Choose Hero or Villain (Q/W/E/R)", score_font, WHITE, 50, 30)
        draw_text("Press Enter to Start (unlocks sound)", score_font, YELLOW, 50, 90)
        y = 120
        draw_text("Heroes:", score_font, WHITE, 50, y)
        for i, h in enumerate(HEROES):
            draw_text(f"{chr(ord('Q') + i)}: {h.capitalize()}", score_font, YELLOW, 70, y + 30 + (i * 30))
        y += 100
        draw_text("Villains:", score_font, WHITE, 50, y)
        for i, v in enumerate(VILLAINS):
            draw_text(f"{chr(ord('E') + i)}: {v.capitalize()}", score_font, YELLOW, 70, y + 30 + (i * 30))
        if player1_done and game_mode == 2:
            draw_text("Player 2: Choose Opponent (U/I/O/P)", score_font, WHITE, 50, 60)
        pygame.draw.rect(screen, (0, 0, 0), quit_rect.inflate(10, 10))
        screen.blit(quit_img, quit_rect)
        draw_touch_controls()  # Show touch controls during selection too
        pygame.display.update()

    while selecting:
        draw_text("ESC to quit", score_font, WHITE, 700, 450)
        draw_selection_screen()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_touch_input(event.pos, True)
                if quit_rect.collidepoint(event.pos):
                    pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONUP:
                handle_touch_input(event.pos, False)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); exit()
                if event.key == pygame.K_RETURN:
                    pygame.mixer.music.play(-1, 0.0, 5000)
                if not player1_done:
                    if event.key == pygame.K_q:
                        choice1 = "captain"
                    elif event.key == pygame.K_w:
                        choice1 = "ironman"
                    elif event.key == pygame.K_e:
                        choice1 = "thanos"
                    elif event.key == pygame.K_r:
                        choice1 = "loki"
                    else:
                        continue
                    side1 = "hero" if choice1 in HEROES else "villain"
                    player2_side = "villain" if side1 == "hero" else "hero"
                    c1 = CHARACTERS[choice1]
                    img1 = pygame.image.load(c1["sheet"]).convert_alpha()
                    fighter_1 = Fighter(1, 200, 310, False, c1["data"], img1, c1["steps"], c1["sound"])
                    player1_done = True
                    if game_mode == 1:
                        options = VILLAINS if player2_side == "villain" else HEROES
                        options = [c for c in options if c != choice1]
                        choice2 = random.choice(options)
                        c2 = CHARACTERS[choice2]
                        img2 = pygame.image.load(c2["sheet"]).convert_alpha()
                        fighter_2 = Fighter(2, 700, 310, True, c2["data"], img2, c2["steps"], c2["sound"])
                        selecting = False
                elif not fighter_2 and game_mode == 2:
                    if event.key == pygame.K_u:
                        choice2 = "captain"
                    elif event.key == pygame.K_i:
                        choice2 = "ironman"
                    elif event.key == pygame.K_o:
                        choice2 = "thanos"
                    elif event.key == pygame.K_p:
                        choice2 = "loki"
                    else:
                        continue
                    if choice2 == choice1:
                        continue
                    if (player2_side == "hero" and choice2 not in HEROES) or (player2_side == "villain" and choice2 not in VILLAINS):
                        continue
                    c2 = CHARACTERS[choice2]
                    img2 = pygame.image.load(c2["sheet"]).convert_alpha()
                    fighter_2 = Fighter(2, 700, 310, True, c2["data"], img2, c2["steps"], c2["sound"])
                    selecting = False

    # Override fighter movement to use mobile keys
    original_move = fighter_1.move
    def mobile_move(screen_width, screen_height, surface, target, round_over):
        # Temporarily override pygame.key.get_pressed
        original_get_pressed = pygame.key.get_pressed
        pygame.key.get_pressed = get_mobile_keys
        original_move(screen_width, screen_height, surface, target, round_over)
        pygame.key.get_pressed = original_get_pressed
    
    fighter_1.move = mobile_move

    run = True
    while run:
        clock.tick(FPS)
        
        # Handle touch events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_touch_input(event.pos, True)
            elif event.type == pygame.MOUSEBUTTONUP:
                handle_touch_input(event.pos, False)
        
        draw_bg()
        draw_health_bar(fighter_1.health, 20, 20)
        draw_health_bar(fighter_2.health, 580, 20)
        draw_text("P1: " + str(score[0]), score_font, RED, 20, 60)
        draw_text("P2: " + str(score[1]), score_font, RED, 580, 60)

        if intro_count <= 0:
            fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT - 100, screen, fighter_2, round_over)
            if game_mode == 2:
                fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT - 100, screen, fighter_1, round_over)
            else:
                control_bot(fighter_2, fighter_1, round_over)
        else:
            draw_text(str(intro_count), count_font, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
            if pygame.time.get_ticks() - last_count_update >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        fighter_1.update()
        fighter_2.update()
        fighter_1.draw(screen)
        fighter_2.draw(screen)

        if not round_over:
            if not fighter_1.alive:
                score[1] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
            elif not fighter_2.alive:
                score[0] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
        else:
            screen.blit(victory_img, (360, 150))
            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                if score[0] == 3 or score[1] == 3:
                    winner = "Player 1" if score[0] == 3 else "Player 2"
                    screen.fill((0, 0, 0))
                    draw_text(f"{winner} Wins The Match!", count_font, YELLOW, 170, 200)
                    pygame.display.update()
                    pygame.time.delay(3000)
                    fighter_1 = fighter_2 = None
                    score = [0, 0]
                    intro_count = 3
                    round_over = False
                    selecting = True
                    player1_done = False
                    player2_side = None
                    game_mode = await select_game_mode()
                    continue
                else:
                    round_over = False
                    intro_count = 3
                    f1 = CHARACTERS[choice1]
                    f2 = CHARACTERS[choice2]
                    fighter_1 = Fighter(1, 200, 310, False, f1["data"], pygame.image.load(f1["sheet"]).convert_alpha(), f1["steps"], f1["sound"])
                    fighter_2 = Fighter(2, 700, 310, True, f2["data"], pygame.image.load(f2["sheet"]).convert_alpha(), f2["steps"], f2["sound"])
                    # Re-apply mobile controls
                    fighter_1.move = mobile_move

        # Draw touch controls
        draw_touch_controls()
        
        await asyncio.sleep(0)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())