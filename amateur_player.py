import numpy as np
from my_player import MyPlayer
import asyncio
import orjson
import random

import vector_converter as vc

from abc import ABC
from abc import abstractmethod
from asyncio import Condition
from asyncio import Event
from asyncio import Queue
from asyncio import Semaphore
from time import perf_counter
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.battle import Battle
from poke_env.environment.double_battle import DoubleBattle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.exceptions import ShowdownException
from poke_env.player.player import Player
from poke_env.player.player_network_interface import PlayerNetwork
from poke_env.player.battle_order import (
    BattleOrder,
    DefaultBattleOrder,
    DoubleBattleOrder,
)
from poke_env.player_configuration import _create_player_configuration_from_player
from poke_env.player_configuration import PlayerConfiguration
from poke_env.server_configuration import LocalhostServerConfiguration
from poke_env.server_configuration import ServerConfiguration
from poke_env.teambuilder.teambuilder import Teambuilder
from poke_env.teambuilder.constant_teambuilder import ConstantTeambuilder
from poke_env.utils import to_id_str


class AmateurPlayer(MyPlayer):
    def choose_move(self, battle):
        available = [] + battle.available_moves
        if available: 
            best_move = max(available, key=lambda move: move.base_power * move.type.damage_multiplier(*battle.opponent_active_pokemon.types))
            if best_move.base_power * best_move.type.damage_multiplier(*battle.opponent_active_pokemon.types) <= 60:
                if battle.available_switches:
                    switch = self.choose_switch(battle)
                    if switch:
                        return self.create_order(switch)
                    else:
                        random_move = available[int(np.random.uniform() * len(available))]
                        return self.create_order(random_move)
                else:
                    random_move = available[int(np.random.uniform() * len(available))]
                    return self.create_order(random_move)                    
            else:
                if np.random.uniform() < 0.8:
                    return self.create_order(best_move)
                else: 
                    random_move = available[int(np.random.uniform() * len(available))]
                    return self.create_order(random_move)
        else:
            switch = self.choose_switch(battle)
            if switch:
                return self.create_order(switch)
            else:
                random_switch = battle.available_switches[int(np.random.uniform() * len(battle.available_switches))]
                return self.create_order(random_switch)

       
        

    def choose_switch(self, battle):
        possible_switches = []
        for switch in battle.available_switches:
            best_move = Move(max(switch._moves, key=lambda move: Move(move).base_power * Move(move).type.damage_multiplier(*battle.opponent_active_pokemon.types)))
            if best_move.base_power * best_move.type.damage_multiplier(*battle.opponent_active_pokemon.types) >= 60:
                possible_switches += [switch]
        if possible_switches:
            best_switch = possible_switches[int(np.random.uniform() * len(possible_switches))]
            return best_switch
        else:
            return False
