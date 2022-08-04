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
from poke_env.data import POKEDEX, UNKNOWN_ITEM



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
		"_range"
		"_clue"
		"_current_pp",
		"_already_moved",							#todo: rewrite safely switch
		"_last_move",
		"_item",
		"_ability",
		"_possible_moves",
		)

	def __init__(self, _mon:Pokemon):
		self._mon = copy.deepcopy(_mon)			
		self._stats = [0,0,0,0,0,0,0]
		self._range = {}
		self._clue = {}
		self._current_pp: Dict[str, int] = {}
		self._already_moved = False
		self._last_move = None
		self._item = "unknown"
		self._ability = "unknown"										#todo exclusive method to find ability
		self._possible_moves: List[str] = []


		if self._mon._species in POKEDEX:
			basestats = POKEDEX[self._mon._species]["baseStats"]
			lv = self._mon._level
			if self._mon._species == "shedinja":
				self._range["def"] = [1,1]
				self._range["spd"] = [1,1]
			else:
				self._range["hp"] = [int((basestats["hp"]*2+31)*lv/100+10+lv),int((basestats["hp"]*2+94)*lv/100+10+lv)]
				self._range["def"] = [self._range["hp"][0]*int((basestats["def"]*2+31)*lv/100+5),self._range["hp"][1]*int(((basestats["def"]*2+94)*lv/100+5)*1.1)]
				self._range["spd"] = [self._range["hp"][0]*int((basestats["spd"]*2+31)*lv/100+5),self._range["hp"][1]*int(((basestats["spd"]*2+94)*lv/100+5)*1.1)]
			self._range["atk"] = [int(((basestats["atk"]*2)*lv/100+5)*0.9),int(((basestats["atk"]*2+94)*lv/100+5)*1.1)]
			self._range["spa"] = [int(((basestats["spa"]*2)*lv/100+5)*0.9),int(((basestats["spa"]*2+94)*lv/100+5)*1.1)]
			self._range["spe"] = [int(((basestats["spe"]*2)*lv/100+5)*0.9),int(((basestats["spe"]*2+94)*lv/100+5)*1.1)]
			self._clue = copy.deepcopy(self._range)


		if self._mon._last_request:
			self._stats[0] = self._mon._current_hp
			self._stats[1] = self._mon._max_hp
			self._stats[2:7] = self._mon._last_request["stats"].values()
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
		if self._clue["spe"][1] < 200:
			self._stats[6] = self._clue["spe"][0]
		elif self._clue["spe"][1] < 240:
			self._stats[6] = self._clue["spe"][0]
		elif self._clue["spe"][1] > 300:
			self._stats[6] = self._clue["spe"][1]
		else:
			self._stats[6] = 0.7 * self._clue["spe"][1] + 0.3 * self._clue["spe"][0]

		if self._clue["atk"][1] > 300:
			self._stats[2] = self._clue["atk"][1]
		else:
			self._stats[2] = 0.7 * self._clue["atk"][1] + 0.3 * self._clue["atk"][0]
		if self._clue["spa"][1] > 300:
			self._stats[4] = self._clue["spa"][1]
		else:
			self._stats[4] = 0.7 * self._clue["spa"][1] + 0.3 * self._clue["spa"][0]

		dr = (self._clue["def"][0] - self._range["def"][0])/(self._range["def"][1] - self._range["def"][0])
		sr = (self._clue["spd"][0] - self._range["spd"][0])/(self._range["spd"][1] - self._range["spd"][0])
		if dr > 0.4 or sr > 0.4:
			self._stats[1] = self._range["hp"][1]
		else:
			self._stats[1] = 0.3 * self._range["hp"][1] + 0.7 * self._range["hp"][0]
		self._stats[3] = (0.3 * self._clue["def"][1] + 0.7 * self._clue["def"][0]) / self._stats[1]
		self._stats[5] = (0.3 * self._clue["spd"][1] + 0.7 * self._clue["spd"][0]) / self._stats[1]
		self._stats[0] = self._mon._current_hp * self._stats[1]

		self._item = self._mon._item
		if self._item == "unknown":								#test this
			if "evos" in POKEDEX[self._mon._species]:
				self._item = "eviolite"								#supplement needed

		self._item = self._mon._ability
		if self._ability == "unknown":								#test this
			abilities = {}
			for a in POKEDEX[self._mon._species]["abilities"]:
				pass




	def clear_predict(self):
		self._mon = copy.deepcopy(_mon)


