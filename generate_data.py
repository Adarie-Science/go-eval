from unittest.mock import Mock

from katrain.__main__ import KaTrainGui
from katrain.core.ai import generate_ai_move
from katrain.core.constants import AI_WEIGHTED
from katrain.core.engine import KataGoEngine
from katrain.core.game import Game

# katrain = Mock()
katrain = KaTrainGui()
katrain.log = print
katrain.config("engine")[
    "model"
] = "/Users/peter/.katrain/g170-b30c320x2-s4824661760-d1229536699.bin.gz"
print(katrain.config("engine"))
engine = KataGoEngine(katrain, katrain.config("engine"))
game = Game(katrain, engine, analyze_fast=True)
generate_ai_move(game, AI_WEIGHTED, {"lower_bound": 0, "weaken_fac": 1})
