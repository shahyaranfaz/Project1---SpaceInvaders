from __future__ import annotations
import sys
from character import UserPlayer
from interface import Button, ScrollArea
from constants import *


def handle_events(buttons: list[Button], player: UserPlayer = None,
                  scroll: ScrollArea=None) -> None:
    """"""
    mouse_pos = pygame.mouse.get_pos()
    for button in buttons:
        button.change_color(mouse_pos)
        button.draw(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_actions()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.check_for_input(mouse_pos):
                    button.action()
        if player and event.type in (pygame.KEYDOWN, pygame.KEYUP):
            is_keydown = event.type == pygame.KEYDOWN
            if event.key in KEY_STROKES:
                player.set_user_input(event.key, is_keydown)
            elif event.key == pygame.K_SPACE:
                player.set_shooting(is_keydown)
        if scroll:
            scroll.handle_event(event)


def update_screen():
    pygame.display.update()
    clock.tick(60)


def quit_actions():
    pygame.quit()
    sys.exit()


def main_menu():
    buttons = [play_button, quit_button, high_score_button]
    screen.fill("Black")
    rendered_text = FONT_LOGO.render("SPACE INVADERS", True, "White")
    screen.blit(rendered_text, rendered_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
    while True:
        handle_events(buttons)
        update_screen()


def show_high_scores():
    buttons = [return_button]
    rendered_text = pygame.font.Font("assets/fonts/logo_font.ttf", 100).render("SPACE INVADERS", True, "White")
    screen.blit(rendered_text, rendered_text.get_rect(center=(SCREEN_WIDTH // 2, 50)))
    with open("assets/scores.txt") as scores:
        lines = scores.readlines()
    high_scores = ScrollArea(0,100, SCREEN_WIDTH, SCREEN_HEIGHT - 100, len(lines) * 50)
    for i, line in enumerate(lines):
        text_surface = FONT_50.render(line.replace('\n', ''), True, "White")
        text_rect = text_surface.get_rect(center=(high_scores.rect.width // 2, i * 50 + 25))
        high_scores.surface.blit(text_surface, text_rect)
    while True:
        high_scores.draw(screen)
        handle_events(buttons, scroll=high_scores)
        update_screen()


def play():
    buttons = [press_to_quit_button]
    player = UserPlayer(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    enemies = []
    tokens = []
    while True:
        screen.blit(pygame.image.load("assets/game_background.png"), (0, 0))
        display_hud(player)
        handle_events(buttons, player)
        if player.shooting:
            player.shoot()
        for bullet in player.bullets.copy():
            bullet.place(screen)

        for enemy in enemies.copy():
            if enemy.check_for_death(player):
                game_over(player, enemies + player.bullets + tokens)
                return None
            enemy.place(screen)
        for token in tokens.copy():
            token.draw(screen)
            token.collect(player, tokens)

        player.place(screen)
        player.check_for_kills(enemies)
        player.set_enemy_count(enemies)
        player.update_tokens(tokens)
        player.update_score()
        update_screen()
        if player.score >= 999999:
            game_over(player, enemies + player.bullets + tokens)


def display_hud(player: UserPlayer) -> None:
    score_text = FONT_25.render(f"SCORE: {player.score:06}", True, (255, 255, 255))
    screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15)))
    ammo_text = FONT_85.render(f"{player.ammo:3}", True, AMMO_COLOURS.get(player.ammo, (255, 255, 255)))
    screen.blit(ammo_text, ammo_text.get_rect(topright=(SCREEN_WIDTH - 10, 10)))
    if player.power_up is not None:
        power_up_text = FONT_40.render(str(player.power_up), True, (255, 255, 255))
        screen.blit(power_up_text, ammo_text.get_rect(topleft=(10, 10)))


def game_over(player, objects):
    new_high_score = record_score(str(player.score), str(player.kills))
    if player.score >= 999999:
        display_msg, colour = "You Won!", "Gold"
    elif new_high_score:
        display_msg, colour = "New High Score!", "Green"
    else:
        display_msg, colour = "You Lost!", "Red"
    buttons = [main_menu_button]
    screen.blit(pygame.image.load("assets/game_background.png"), (0, 0))
    for obj in objects:
        obj.draw(screen)
    player.draw(screen)
    while True:
        rendered_text = FONT_100.render(display_msg, True, colour)
        screen.blit(rendered_text, rendered_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        handle_events(buttons)
        update_screen()


def record_score(score: str, kills: str) -> bool:
    import datetime
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").split(" ")
    text = score + " " * (9 - len(score)) + kills + " " * (6 - len(kills)) + f"   {time[0]}   {time[1]}"
    with open("assets/scores.txt") as scores:
        entries = scores.readlines()
    if entries:
        entries.pop(0)
    entries.append(text + "\n")
    entries.sort(reverse=True, key=lambda line: int(line.split(" ")[0]))
    with open("assets/scores.txt", "w") as scores:
        scores.write("Score    Kills    Date         Time    \n")
        for entry in entries:
            scores.write(entry)
    if text == entries[0].strip():
        return True
    return False

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()
    play_button = Button(
        (SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 100),
        "PLAY",
        FONT_50,
        "White",
        "Green",
        play
    )
    quit_button = Button(
        (SCREEN_WIDTH / 2 + 100, SCREEN_HEIGHT / 2 + 100),
        "QUIT",
        FONT_50,
        "White",
        "Red",
        quit_actions
    )
    main_menu_button = Button(
        (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100),
        "MAIN MENU",
        FONT_60,
        "White",
        "Green",
        main_menu
    )
    high_score_button = Button(
        (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20),
        "VIEW HIGH SCORES",
        FONT_40,
        "White",
        "Gold",
        show_high_scores
    )
    press_to_quit_button = Button(
        (SCREEN_WIDTH / 2, 25),
        "PRESS TO QUIT",
        FONT_25,
        "White",
        "Red",
        quit_actions
    )
    return_button = Button(
        (SCREEN_WIDTH - 72, SCREEN_HEIGHT - 17),
        "RETURN",
        FONT_50,
        "White",
        "GREEN",
        main_menu
    )
    main_menu()
