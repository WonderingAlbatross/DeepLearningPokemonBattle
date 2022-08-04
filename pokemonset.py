import numpy as np
import copy
import orjson

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.data import POKEDEX



import building_guesser as bg


EXP_LEARNSET: Dict[str, Any] = {}
LEARNSET: Dict[str, Any] = {}



with open("exp_learnset.json") as exp_learnset:
	EXP_LEARNSET = orjson.loads(exp_learnset.read())
with open("new_learnset.json") as learnset:
	LEARNSET = orjson.loads(learnset.read())



class PokemonSet:
	__slots__ = (
		"_mon",
		"_stats",
		"_atk_range",
		"_def_hp_range",
		"_spa_range",
		"_spd_hp_range",
		"_hp_range",
		"_spe_range",
		"_current_pp",
		"_already_moved",							#todo: rewrite safely switch
		"_last_move",
		"_item",
		"_ability",
		"_possible_moves"
		)

	def __init__(self, _mon:Pokemon):
		self._mon = copy.deepcopy(_mon)			
		self._stats = [0,0,0,0,0,0,0]
		self._atk_range = [10,500]
		self._def_hp_range = [100,200000]
		self._spa_range = [10,500]
		self._spd_hp_range = [100,200000]
		self._hp_range = [10,500]
		self._spe_range = [10,500]
		self._current_pp: Dict[str, int] = {}
		self._already_moved = False
		self._last_move = None
		self._possible_moves: List[str] = []

		if _mon._species in POKEDEX:
			basestats = POKEDEX[_mon._species]["baseStats"]
			lv = _mon._level
			if _mon._species == "shedinja":
				self._hp_range = [1,1]
				self._def_hp_range = [1,1]
				self._spd_hp_range = [1,1]
			else:
				self._hp_range = [int((basestats["hp"]*2+31)*lv/100+10+lv),int((basestats["hp"]*2+94)*lv/100+10+lv)]
				self._def_hp_range = [_hp_range[0]*int((basestats["def"]*2+31)*lv/100+5),_hp_range[1]*int(((basestats["def"]*2+94)*lv/100+5)*1.1)]
				self._spd_hp_range = [_hp_range[0]*int((basestats["spd"]*2+31)*lv/100+5),_hp_range[1]*int(((basestats["spd"]*2+94)*lv/100+5)*1.1)]
			self._atk_range = [int(((basestats["atk"]*2)*lv/100+5)*0.9),int(((basestats["atk"]*2+94)*lv/100+5)*1.1)]
			self._spa_range = [int(((basestats["spa"]*2)*lv/100+5)*0.9),int(((basestats["spa"]*2+94)*lv/100+5)*1.1)]
			self._spe_range = [int(((basestats["spe"]*2)*lv/100+5)*0.9),int(((basestats["spe"]*2+94)*lv/100+5)*1.1)]

		if _mon._last_request:
			self._stats[0] = _mon._current_hp
			self._stats[1] = _mon._max_hp
			self._stats[2:7] = _mon._last_request["stats"].values()
		else:
			self.predict()

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

	def predict(self):
		pass

	def clear_predict(self):
		self._mon = copy.deepcopy(_mon)


