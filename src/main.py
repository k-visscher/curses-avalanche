#!/usr/bin/env python3
import random

import curses
from curses import wrapper

import curses.ascii

BORDER_STYLE = ["|", "|", "-", "-", "+", "+", "+", "+"]
WIDTH = 80
HEIGHT = 24

UNSUPPORTED_RESOLUTION_TEXT = "curses-avalanche only supports 80×24 terminals"
HIGH_SCORE_TEXT = "high score"
YOUR_SCORE_TEXT = "your score"

PLAYER_SPRITE = r"""
 O
/|\
/ \
"""

PLAYER_SPRITE_HEIGHT = PLAYER_SPRITE.count("\n")
PLAYER_SPRITE_WIDTH = max(map(lambda line: len(line), PLAYER_SPRITE.splitlines()))

ROCK_SPRITE = r"""
\----/
 \  /
  \/
"""

ROCK_SPRITE_HEIGHT = ROCK_SPRITE.count("\n")
ROCK_SPRITE_WIDTH = max(map(lambda line: len(line), ROCK_SPRITE.splitlines()))


def clamp(minimum_value, maximum_value, value):
    return sorted((minimum_value, value, maximum_value))[1]

def main(screen):
    # ticks are 15ms long
    screen.timeout(15)

    ticks = 0
    score = 0
    high_score = 0

    # [y, x]
    player = [22, 30]

    # [[y, x]....[y, x]]
    rocks = [[0, 1 + (i * 6)] for i in range(10)]

    while True:
        screen.clear()

        height, width = screen.getmaxyx()
        if width != WIDTH or height != HEIGHT:
            screen.clear()
            center_height = int(height / 2)
            center_width = int(width / 2)
            screen.addstr(
                center_height,
                center_width - round(len(UNSUPPORTED_RESOLUTION_TEXT) / 2),
                UNSUPPORTED_RESOLUTION_TEXT,
            )
            screen.refresh()
            continue

        screen.border(*BORDER_STYLE)
        score_sub_window = screen.derwin(HEIGHT, 20, 0, 60)
        score_sub_window_y, score_sub_window_x = score_sub_window.getmaxyx()
        score_sub_window.border(*BORDER_STYLE)

        score_sub_window.addstr(
            int(score_sub_window_y / 2) - 4,
            int(score_sub_window_x / 2) - int(len(YOUR_SCORE_TEXT) / 2) + 1,
            YOUR_SCORE_TEXT,
        )
        score_sub_window.addstr(
            int(score_sub_window_y / 2) - 3,
            int(score_sub_window_x / 2) - int(len(str(score)) / 2),
            str(score),
        )

        score_sub_window.addstr(
            int(score_sub_window_y / 2) - 1,
            int(score_sub_window_x / 2) - int(len(HIGH_SCORE_TEXT) / 2) + 1,
            HIGH_SCORE_TEXT,
        )
        score_sub_window.addstr(
            int(score_sub_window_y / 2), int(score_sub_window_x / 2), str(high_score)
        )

        for index, line in zip(
            reversed(range(PLAYER_SPRITE_HEIGHT)), PLAYER_SPRITE.splitlines()
        ):
            screen.addstr(player[0] - index, player[1], line)

        for rock in rocks:
            for index, line in zip(
                range(ROCK_SPRITE_HEIGHT), ROCK_SPRITE.splitlines()
            ):
                screen.addstr(rock[0] + index, rock[1], line)

        screen.refresh()

        for index, rock in enumerate(rocks):
            if rock[0] >= 19:
                rocks[index][0] = 0

        ticks += 1

        # 15ms * 67 = ~1005ms
        if ticks % 67 == 0:
            score += 1

        if ticks % 30 == 0:
            for _ in range(random.randint(1, 10)):
                rock = random.choice(rocks)
                rock[0] = rock[0] + 1

        key = screen.getch()
        if key == curses.ascii.ESC:
            break
        elif key == curses.KEY_LEFT:
            player[1] = clamp(1, 60 - PLAYER_SPRITE_WIDTH, player[1] - 1)
        elif key == curses.KEY_RIGHT:
            player[1] = clamp(1, 60 - PLAYER_SPRITE_WIDTH, player[1] + 1)


wrapper(main)
