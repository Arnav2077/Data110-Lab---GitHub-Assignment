#!/usr/bin/env python3
"""
🚀 ASTEROID DASH 🚀
A terminal arcade game - dodge asteroids and survive as long as you can!
Controls: A/D or ←/→ to move | Q to quit
"""

import curses
import random
import time

# Game constants
PLAYER = "▲"
ASTEROID_CHARS = ["✦", "◆", "★", "●", "◉"]
TRAIL_CHAR = "·"
EXPLOSION_FRAMES = ["✸", "✺", "✻", "✼", " "]
STARS = [".", "·", "˙", "*"]

def draw_border(stdscr, height, width):
    """Draw a stylish game border."""
    try:
        for y in range(height):
            stdscr.addstr(y, 0, "║", curses.color_pair(3))
            stdscr.addstr(y, width - 1, "║", curses.color_pair(3))
        for x in range(1, width - 1):
            stdscr.addstr(0, x, "═", curses.color_pair(3))
            stdscr.addstr(height - 1, x, "═", curses.color_pair(3))
        stdscr.addstr(0, 0, "╔", curses.color_pair(3))
        stdscr.addstr(0, width - 1, "╗", curses.color_pair(3))
        stdscr.addstr(height - 1, 0, "╚", curses.color_pair(3))
        stdscr.addstr(height - 1, width - 1, "╝", curses.color_pair(3))
    except curses.error:
        pass

def main(stdscr):
    # Setup
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(80)
    curses.start_color()
    curses.use_default_colors()

    # Color pairs
    curses.init_pair(1, curses.COLOR_CYAN, -1)      # Player
    curses.init_pair(2, curses.COLOR_RED, -1)        # Asteroids
    curses.init_pair(3, curses.COLOR_YELLOW, -1)     # Border / UI
    curses.init_pair(4, curses.COLOR_WHITE, -1)      # Stars
    curses.init_pair(5, curses.COLOR_GREEN, -1)      # Score
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)    # Explosion
    curses.init_pair(7, curses.COLOR_BLUE, -1)       # Trail

    height, width = stdscr.getmaxyx()
    game_width = min(width, 60)
    game_height = min(height, 28)
    offset_x = (width - game_width) // 2
    offset_y = (height - game_height) // 2

    def gx(x): return x + offset_x
    def gy(y): return y + offset_y

    def safe_addstr(y, x, text, attr=0):
        try:
            if 0 <= y < game_height and 0 <= x < game_width - 1:
                stdscr.addstr(gy(y), gx(x), text, attr)
        except curses.error:
            pass

    def show_screen(title, lines, prompt="Press SPACE to start  |  Q to quit"):
        stdscr.clear()
        draw_border(stdscr, game_height, game_width)
        ty = game_height // 2 - len(lines) // 2 - 2
        tx = (game_width - len(title)) // 2
        safe_addstr(ty, tx, title, curses.color_pair(3) | curses.A_BOLD)
        for i, line in enumerate(lines):
            lx = (game_width - len(line)) // 2
            safe_addstr(ty + 2 + i, lx, line, curses.color_pair(5))
        px = (game_width - len(prompt)) // 2
        safe_addstr(ty + 2 + len(lines) + 2, px, prompt, curses.color_pair(1))
        stdscr.refresh()
        while True:
            key = stdscr.getch()
            if key == ord(' '):
                return True
            if key in (ord('q'), ord('Q')):
                return False

    # Title screen
    title_art = "🚀  ASTEROID DASH  🚀"
    intro_lines = [
        "Dodge the asteroids. Survive.",
        "",
        "  A / D  or  ← / →  :  Move  ",
        "         Q  :  Quit          ",
    ]
    if not show_screen(title_art, intro_lines):
        return

    # ── Game loop ──────────────────────────────────────────────
    while True:
        # State
        player_x = game_width // 2
        player_y = game_height - 3
        asteroids = []    # (x, y, char, speed_mod)
        explosions = []   # (x, y, frame)
        bg_stars = [(random.randint(1, game_width - 2),
                     random.randint(1, game_height - 2),
                     random.choice(STARS)) for _ in range(25)]
        score = 0
        speed = 1.0
        lives = 3
        asteroid_interval = 18
        tick = 0
        trail = []
        game_over = False
        last_time = time.time()
        frame_budget = 0.08

        while not game_over:
            frame_start = time.time()
            key = stdscr.getch()

            # Input
            if key in (ord('q'), ord('Q')):
                return
            if key in (ord('a'), curses.KEY_LEFT) and player_x > 2:
                player_x -= 2
            if key in (ord('d'), curses.KEY_RIGHT) and player_x < game_width - 3:
                player_x += 2

            tick += 1
            score += 1

            # Difficulty ramp
            if tick % 150 == 0:
                speed = min(speed + 0.15, 3.0)
                asteroid_interval = max(6, asteroid_interval - 1)

            # Spawn asteroids
            if tick % asteroid_interval == 0:
                ax = random.randint(2, game_width - 3)
                achar = random.choice(ASTEROID_CHARS)
                spd_mod = random.uniform(0.7, 1.3)
                asteroids.append([ax, 1, achar, spd_mod, 0.0])

            # Move asteroids
            new_asteroids = []
            for a in asteroids:
                a[4] += speed * a[3]
                a[1] = int(a[4]) + 1
                if a[1] >= game_height - 2:
                    pass  # gone off screen
                else:
                    new_asteroids.append(a)
            asteroids = new_asteroids

            # Collision detection
            hit = False
            for a in asteroids[:]:
                if abs(a[0] - player_x) <= 1 and abs(a[1] - player_y) <= 1:
                    explosions.append([player_x, player_y, 0])
                    asteroids.remove(a)
                    lives -= 1
                    hit = True
                    if lives <= 0:
                        game_over = True
                    break

            # Trail
            trail.append((player_x, player_y + 1))
            if len(trail) > 5:
                trail.pop(0)

            # Draw
            stdscr.clear()
            draw_border(stdscr, game_height, game_width)

            # Background stars
            for sx, sy, sc in bg_stars:
                safe_addstr(sy, sx, sc, curses.color_pair(4) | curses.A_DIM)

            # HUD
            hud = f" SCORE: {score:06d}   LIVES: {'♥ ' * lives}{'♡ ' * (3 - lives)}  SPEED: {'▮' * int(speed)}"
            safe_addstr(1, 2, hud[:game_width - 4], curses.color_pair(3) | curses.A_BOLD)
            safe_addstr(2, 2, "─" * (game_width - 4), curses.color_pair(3) | curses.A_DIM)

            # Trail
            for i, (tx2, ty2) in enumerate(trail):
                alpha = curses.A_DIM if i < 3 else 0
                safe_addstr(ty2, tx2, TRAIL_CHAR, curses.color_pair(7) | alpha)

            # Player
            safe_addstr(player_y, player_x, PLAYER,
                        curses.color_pair(1) | curses.A_BOLD)

            # Asteroids
            for a in asteroids:
                safe_addstr(a[1], a[0], a[2], curses.color_pair(2) | curses.A_BOLD)

            # Explosions
            new_exp = []
            for e in explosions:
                if e[2] < len(EXPLOSION_FRAMES):
                    safe_addstr(e[1], e[0], EXPLOSION_FRAMES[e[2]],
                                curses.color_pair(6) | curses.A_BOLD)
                    e[2] += 1
                    new_exp.append(e)
            explosions = new_exp

            stdscr.refresh()

            # Frame timing
            elapsed = time.time() - frame_start
            sleep_t = max(0, frame_budget - elapsed)
            time.sleep(sleep_t)

        # Game over screen
        stdscr.clear()
        draw_border(stdscr, game_height, game_width)
        go_lines = [
            f"  Final Score: {score:,}  ",
            "",
            f"  Speed reached: {'▮' * int(speed)}  ",
        ]
        again = show_screen("💥  GAME OVER  💥", go_lines,
                            "SPACE to play again  |  Q to quit")
        if not again:
            break


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("\nThanks for playing 🚀 Asteroid Dash!")
