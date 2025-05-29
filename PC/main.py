import asyncio  # ADD THIS LINE
import pygame
from pygame import mixer
from PC.fighter import Fighter
import random # <-- added for bot behavior

async def main():  # WRAP EVERYTHING IN ASYNC FUNCTION
    mixer.init()
    pygame.init()

    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Brawler")

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
        screen.blit(pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))

    def draw_health_bar(health, x, y):
        ratio = health / 100
        pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
        pygame.draw.rect(screen, RED, (x, y, 400, 30))
        pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))

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
            bot.pre_attack_flip = bot.flip # initialize attribute

        if bot.attacking:
            # Force bot to keep same facing while attacking
            bot.flip = bot.pre_attack_flip
            if bot.frame_index == 0:
                bot.attack_type = 0
            bot.running = False
            return
        else:
            # Only update facing when NOT attacking
            if target.rect.centerx > bot.rect.centerx:
                bot.flip = False
            else:
                bot.flip = True
            bot.pre_attack_flip = bot.flip # update locked facing for next attack

        # Tight attack range—must be basically touching
        IN_ATTACK_RANGE = abs_distance < 1 and vertical_gap < 1

        # --- JUMP if player is jumping, or randomly every 1-3s ---
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

        # If in attack range and not on cooldown, attack
        if IN_ATTACK_RANGE and bot.attack_cooldown == 0 and not bot.attacking:
            bot.attack_type = random.choice([1, 2])
            bot.attack(target)
            bot.running = False
            return

        # If NOT in attack range, move toward player
        if not IN_ATTACK_RANGE:
            bot.running = True
            if distance > 0:
                bot.rect.x += 5
            else:
                bot.rect.x -= 5
        else:
            bot.running = False # Stay put when in range

    async def select_game_mode():  # MAKE THIS ASYNC
        font = pygame.font.Font("assets/fonts/turok.ttf", 40)
        selecting = True
        while selecting:
            screen.fill((0, 0, 0))
            draw_text("Choose Game Mode", font, WHITE, 320, 100)
            draw_text("Press 1: 1 Player (vs Bot)", font, YELLOW, 300, 200)
            draw_text("Press 2: 2 Player", font, YELLOW, 300, 270)
            pygame.display.update()
            await asyncio.sleep(0)  # ADD THIS LINE
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

    game_mode = await select_game_mode()  # ADD AWAIT

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
        pygame.display.update()

    while selecting:
        draw_text("ECS to quit", score_font, WHITE, 700, 550)
        draw_selection_screen()
        await asyncio.sleep(0)  # ADD THIS LINE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
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
                    if game_mode == 1: # <-- Auto assign bot
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if quit_rect.collidepoint(event.pos):
                    pygame.quit(); exit()

    run = True
    while run:
        clock.tick(FPS)
        draw_bg()
        draw_health_bar(fighter_1.health, 20, 20)
        draw_health_bar(fighter_2.health, 580, 20)
        draw_text("P1: " + str(score[0]), score_font, RED, 20, 60)
        draw_text("P2: " + str(score[1]), score_font, RED, 580, 60)

        if intro_count <= 0:
            fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
            if game_mode == 2:
                fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
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
                    game_mode = await select_game_mode()  # ADD AWAIT
                    continue
                else:
                    round_over = False
                    intro_count = 3
                    f1 = CHARACTERS[choice1]
                    f2 = CHARACTERS[choice2]
                    fighter_1 = Fighter(1, 200, 310, False, f1["data"], pygame.image.load(f1["sheet"]).convert_alpha(), f1["steps"], f1["sound"])
                    fighter_2 = Fighter(2, 700, 310, True, f2["data"], pygame.image.load(f2["sheet"]).convert_alpha(), f2["steps"], f2["sound"])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        await asyncio.sleep(0)  # ADD THIS CRITICAL LINE
        pygame.display.update()

    pygame.quit()

# ADD THESE LINES AT THE VERY END:
if __name__ == "__main__":
    asyncio.run(main())