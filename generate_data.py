from __future__ import annotations

import os
import random
import time
from functools import lru_cache
from typing import TYPE_CHECKING, Sequence, TypedDict
from unittest.mock import Mock

import requests
import tqdm

if TYPE_CHECKING:
    from katrain.__main__ import KaTrainGui
    from katrain.core.engine import KataGoEngine
    from katrain.core.game import Game

KATAGO_MODEL = "kata1-b28c512nbt-s8536703232-d4684449769.bin.gz"
URL_BASE = "https://media.katagotraining.org/uploaded/networks/models/kata1/"

MODELS_DIR = "katago_files"

TURN_STRINGS = {"B": "Black (X) to play.", "W": "White (O) to play."}


def download_model(url, output_dir=MODELS_DIR):
    os.makedirs(output_dir, exist_ok=True)
    local_filename = os.path.join(output_dir, url.split("/")[-1])

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(local_filename, "wb") as f, tqdm.tqdm(
            desc=local_filename,
            total=total,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            leave=True,
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))

    print(f"Downloaded to: {local_filename}")
    return local_filename


def get_model() -> str:
    """Returns path to model file."""
    dest = os.path.join(MODELS_DIR, KATAGO_MODEL)
    if os.path.exists(dest):
        return dest
    return download_model(URL_BASE + KATAGO_MODEL)


class Example(TypedDict):
    prompt: str
    policy: dict[str, float]


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


def get_prompt(game: Game):
    top_prompt = "This is a position from a game of Go. X represents a black stone and O represents a white stone."
    board_string = pretty_board(game)
    turn_string = TURN_STRINGS[game.current_node.next_player]
    bottom_prompt = "Please try to find the best move. Enter the coordinates in GTP format (letter followed by number).\nYour move:"
    return "\n".join([top_prompt, board_string, turn_string, bottom_prompt])


def setup() -> tuple[KaTrainGui, KataGoEngine]:
    model_path = get_model()

    from katrain.__main__ import KaTrainGui
    from katrain.core.engine import KataGoEngine

    katrain = KaTrainGui()
    katrain.log = Mock()
    katrain.config("engine")["model"] = model_path
    katrain.config("engine")["fast_visits"] = 1
    katrain.config("engine")["max_visits"] = 1
    print(katrain.config("engine"))
    engine = KataGoEngine(katrain, katrain.config("engine"))
    return katrain, engine


def generate_example(katrain: KaTrainGui, engine: KataGoEngine) -> Example:
    from katrain.core.ai import generate_ai_move
    from katrain.core.constants import AI_WEIGHTED
    from katrain.core.game import Game

    game = Game(katrain, engine, analyze_fast=True)
    for i in tqdm.tqdm(range(random.randint(0, 10))):
        generate_ai_move(
            game, AI_WEIGHTED, {"lower_bound": 0, "weaken_fac": 1, "pick_override": 1}
        )
    while not game.current_node.policy:
        time.sleep(0.01)
    policy_dict = {
        move.gtp(): policy
        for policy, move in game.current_node.policy_ranking
        if policy >= 0
    }
    return {
        "prompt": get_prompt(game),
        "policy": policy_dict,
    }


def main():
    katrain, engine = setup()
    print(generate_example(katrain, engine))


if __name__ == "__main__":
    main()
