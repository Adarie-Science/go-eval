import time
from functools import lru_cache
from typing import Sequence
from unittest.mock import Mock

from katrain.__main__ import KaTrainGui
from katrain.core.ai import generate_ai_move
from katrain.core.constants import AI_WEIGHTED
from katrain.core.engine import KataGoEngine
from katrain.core.game import Game


@lru_cache()
def star_points(size: int) -> Sequence[tuple[int, int]]:
    d = 4 if size >= 11 else 3
    s = {d - 1, size - d, (size + 1) / 2}
    return {(x, y) for x in range(size) for y in range(size) if {x, y} <= s}


def pretty_board(game: Game) -> str:
    assert game.board_size[0] == game.board_size[1]  # TODO: non-square boards
    size = game.board_size[0]
    sp = star_points(size)
    guide = "   A B C D E F G H J K L M N O P Q R S T U V W X Y Z"[: size * 2 + 2]

    cells = [["," if (x, y) in sp else "." for x in range(size)] for y in range(size)]

    for stone in game.stones:
        color = "X" if stone.player == "B" else "O"
        x, y = stone.coords
        cells[y][x] = color

    lines = [guide]
    for y in reversed(range(len(cells))):
        row = cells[y]
        row_contents = " ".join(row)
        coord_left = str(y + 1).rjust(2, " ")
        coord_right = str(y + 1)
        row_ascii = f"{coord_left} {row_contents} {coord_right}"
        lines.append(row_ascii)
    lines.append(guide)
    return "\n".join(lines)


def setup() -> tuple[KaTrainGui, KataGoEngine]:
    katrain = KaTrainGui()
    katrain.log = print
    katrain.config("engine")[
        "model"
    ] = "/Users/peter/.katrain/g170-b30c320x2-s4824661760-d1229536699.bin.gz"
    katrain.config("engine")["fast_visits"] = 1
    katrain.config("engine")["max_visits"] = 1
    print(katrain.config("engine"))
    engine = KataGoEngine(katrain, katrain.config("engine"))
    return katrain, engine


def generate_example(katrain: KaTrainGui, engine: KataGoEngine):
    game = Game(katrain, engine, analyze_fast=True)
    for i in range(10):
        move = generate_ai_move(
            game, AI_WEIGHTED, {"lower_bound": 0, "weaken_fac": 1, "pick_override": 1}
        )
        print("MOVE", move)
    print(pretty_board(game))


def main():
    katrain, engine = setup()
    generate_example(katrain, engine)


if __name__ == "__main__":
    main()
