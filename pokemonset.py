import numpy as np

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon


class PokemonSet:
	__slots__ = (
		"_mon",
		"_stats",
		"_atk_clues",
		"_def_clues",
		"_spa_clues",
		"_spd_clues",
		"_hp_clues",
		"_speed_range",
		"_current_pp"
		)

	def __init__(self, _mon:Pokemon):
		self._mon = _mon
		self._stats = [0,0,0,0,0,0,0]
		self._atk_clues: List(float)
		self._def_clues: List(float)
		self._spa_clues: List(float)
		self._spd_clues: List(float)
		self._hp_clues: List(float)
		self._speed_range = [1,999]
		self._current_pp: Dict[str, int]

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