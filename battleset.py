import numpy as np
import copy
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.effect import Effect
from poke_env.environment.field import Field
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.side_condition import STACKABLE_CONDITIONS, SideCondition
from poke_env.environment.weather import Weather



from poke_env.environment.battle import Battle
from vector_converter import Switch
from pokemonset import PokemonSet
import building_guesser as bg

class BattleSet():
	__slots__ = (
		"_team",
		"_oppo_team",
		"_weather",
		"_fields",
		"_side",
		"_oppo_side",
		"_active_monset",
		"_active_opposet"
		)
	def __init__(self, battle):
		self._team = {}
		self._oppo_team = {}
		self._weather = {}
		self._fields = {}
		self._side = {}
		self._oppo_side = {}
		self._active_monset = None
		self._active_opposet = None		
		self.updatefrombattle(battle)



	def updatefrombattle(self,battle):
		self._weather = {}
		self._fields = {}
		self._side = {}
		self._oppo_side = {}
		self._active_monset = None
		self._active_opposet = None			
		for _mon in battle._team:
			if battle._team[_mon] not in self._team:
				self._team[battle._team[_mon]] = PokemonSet(battle._team[_mon])
			else:
				if battle._team[_mon].fainted:
					del _team[battle._team[_mon]]
				else:
					self._team[battle._team[_mon]]._mon = copy.deepcopy(battle._team[_mon])
			if battle._team[_mon].active:
				_active_monset = _team[battle._team[_mon]]
		for _oppo in battle._oppo_team:
			if battle._oppo_team[_oppo] not in self._oppo_team:
				self._oppo_team[battle._oppo_team[_oppo]] = PokemonSet(battle._team[_oppo])
			else:
				if battle._oppo_team[_oppo].fainted:
					del _oppo_team[battle._oppo_team[_oppo]]
				else:
					self._oppo_team[battle._oppo_team[_oppo]]._mon = copy.deepcopy(battle._team[_oppo])
			if battle.oppo_team[_oppo].active:
				_active_opposet = _team[battle._oppo_team[_oppo]]
		for _weather in battle._weather:
			self._weather[_weather] = battle._weather[_weather]
		for _field in battle._fields:
			self._fields[_field] = battle._fields[_field]
		for _side in battle._side_conditions:
			self._side[_side] = battle._side_conditions[_side]
		for _side in battle._opponent_side_conditions:
			self._oppo_side[_side] = battle._opponent_side_conditions[_side]

	def deduct(self,move,oppo_move):								#deepcopy and return a new battleset
		pass

	def usemove(move,monset,opposet,_weather,_fields,_side,_oppo_side):
		pass



