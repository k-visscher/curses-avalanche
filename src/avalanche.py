#!/usr/bin/env python3
import random

import time

import json

import curses
from curses import wrapper
import curses.ascii

from pathlib import Path as path
from os.path import dirname


BORDER_STYLE = ["|", "|", "-", "-", "+", "+", "+", "+"]
WIDTH = 80
HEIGHT = 24

PLAY_AREA_SIZE = 60

HIGH_SCORE_PATH = "/var/games/avalanche/high-score.json"
try:
    path(dirname(HIGH_SCORE_PATH)).mkdir(parents=True, exist_ok=True)
except:
    pass

UNSUPPORTED_RESOLUTION_TEXT = "curses-avalanche only supports 80×24 terminals"
HIGH_SCORE_TEXT = "high score"
YOUR_SCORE_TEXT = "your score"

ARROW_KEYS_TEXT = "use <- -> keys to move"
ESCAPE_KEY_TEXT = "escape key to quit"

PLAYER_SPRITE = "\n".join(
    filter(
        lambda line: line,
        r"""
 O
/|\
/ \
""".splitlines(),
    )
)
PLAYER_SPRITE_HEIGHT = len(PLAYER_SPRITE.splitlines())
PLAYER_SPRITE_WIDTH = max(map(lambda line: len(line), PLAYER_SPRITE.splitlines()))

ROCK_SPRITE = "\n".join(
    filter(
        lambda line: line,
        r"""
\----/
 \  /
  \/
""".splitlines(),
    )
)
ROCK_SPRITE_HEIGHT = len(ROCK_SPRITE.splitlines())
ROCK_SPRITE_WIDTH = max(map(lambda line: len(line), ROCK_SPRITE.splitlines()))


def clamp(minimum_value: int, maximum_value: int, value: int) -> int:
    return sorted((minimum_value, value, maximum_value))[1]


def read_high_score() -> int:
    high_score = 0

    try:
        with open(HIGH_SCORE_PATH, "r") as file:
            high_score = json.load(file)["high_score"]
    except:
        high_score = 0

    return high_score


def write_high_score(score: int) -> None:
    try:
        with open(HIGH_SCORE_PATH, "w") as file:
            json.dump({"high_score": score}, file)
    except:
        pass


def game_loop(screen) -> None:
    running = True
    # ticks are 15ms long.
    screen.timeout(15)

    ticks = 0
    score = 0
    high_score = read_high_score()

    # [y, x].
    player = [HEIGHT - 1 - PLAYER_SPRITE_HEIGHT, int(PLAY_AREA_SIZE / 2)]

    # [[y, x]...[y, x]].
    rocks = [
        [0, 1 + (i * ROCK_SPRITE_WIDTH)]
        for i in range(int(PLAY_AREA_SIZE / ROCK_SPRITE_WIDTH))
    ]

    while running:
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
            time.sleep(0.015)
            continue

        screen.border(*BORDER_STYLE)
        score_sub_window = screen.derwin(HEIGHT, 20, 0, PLAY_AREA_SIZE)
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

        # draw the player sprite.
        for index, line in zip(range(PLAYER_SPRITE_HEIGHT), PLAYER_SPRITE.splitlines()):
            screen.addstr(player[0] + index, player[1], line)

        # draw the rock sprites.
        for rock in rocks:
            for index, line in zip(range(ROCK_SPRITE_HEIGHT), ROCK_SPRITE.splitlines()):
                # check to see if the rock sprite is out of bounds, if it is, reset its position.
                if rock[0] >= HEIGHT - ROCK_SPRITE_HEIGHT:
                    rock[0] = 0
                screen.addstr(rock[0] + index, rock[1], line)

        # check for collisions
        for rock in rocks:
            if (
                player[1] < rock[1] + ROCK_SPRITE_WIDTH
                and player[1] + PLAYER_SPRITE_WIDTH > rock[1]
                and player[0] < rock[0] + ROCK_SPRITE_HEIGHT
                and player[0] + PLAYER_SPRITE_WIDTH > rock[0]
            ):
                running = False

        screen.refresh()

        ticks += 1

        # 15ms * 67 = ~1005ms.
        if ticks % 67 == 0:
            score += 1
            if score > high_score:
                high_score = score

        # move a random amount of rocks, approximately twice a second.
        if ticks % 30 == 0:
            for _ in range(random.randint(1, 10)):
                rock = random.choice(rocks)
                rock[0] += 1

        key = screen.getch()
        if key == curses.ascii.ESC:
            running = False
        elif key == curses.KEY_LEFT:
            player[1] = clamp(1, 60 - PLAYER_SPRITE_WIDTH, player[1] - 1)
        elif key == curses.KEY_RIGHT:
            player[1] = clamp(1, 60 - PLAYER_SPRITE_WIDTH, player[1] + 1)

    write_high_score(high_score)


wrapper(game_loop)
