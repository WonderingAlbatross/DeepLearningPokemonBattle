import numpy as np

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon

import building_guesser as bg


class PokemonSet:
	__slots__ = (
		"_mon",
		"_stats",
		"_atk_range",
		"_def_range",
		"_spa_range",
		"_spd_range",
		"_hp_clues",
		"_speed_range",
		"_current_pp",
		"_already_moved",
		"_last_move"
		)

	def __init__(self, _mon:Pokemon):
		self._mon = _mon
		self._stats = [0,0,0,0,0,0,0]
		self._atk_clues: [1,999]
		self._def_hp_clues: [1,999999]
		self._spa_clues: [1,999]
		self._spd_hp_clues: [1,999999]
		self._hp_clues: List(float)
		self._speed_range = [1,1000]
		self._current_pp: Dict[Move, int]
		self._already_moved = False
		self._last_move = ""

		if _mon._last_request:
			self._stats[0] = _mon._current_hp
			self._stats[1] = _mon._max_hp
			self._stats[2:7] = _mon._last_request["stats"].values()

	def __repr__(self) -> str:
		return self.__str__()

	def __str__(self) -> str:
		return (
			f"{self._mon}"
			f"{self._stats}"
		)


	def random_possible_set(self):
		return self


	def most_possible_set(self):
		return self


	def mixed_possible_set(self):
		return self