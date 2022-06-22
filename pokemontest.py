# -*- coding: utf-8 -*-
import asyncio
import orjson
import numpy as np

import sys
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from typing import Any
from typing import Tuple
from typing import Union

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.battle import Battle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from my_player import MyPlayer
from my_random_player import RandomPlayer
from poke_env.player.battle_order import (
    BattleOrder,
    DefaultBattleOrder,
    DoubleBattleOrder,
)
from poke_env.environment.status import Status

import vector_converter as vc
from pokemonset import PokemonSet



def my_end_item(self, item):
    self._item = "lost"
    print(self._item)
    if item == "powerherb":
        self._preparing_move = False
        self._preparing_target = False

def my_switch_out(self):
    self._active = False
    self._clear_boosts()
    self._clear_effects()
    self._first_turn = False
    self._must_recharge = False
    self._preparing_move = None
    self._preparing_target = None
    self._protect_counter = 0
    if self._item == "lost":
        self._item = None

    if self._status == Status.TOX:
        self._status_counter = 0

def my_update_from_request(self, request_pokemon: Dict[str, Any]) -> None:
    self._active = request_pokemon["active"]

    if request_pokemon == self._last_request:
        return

    if "ability" in request_pokemon:
        self.ability = request_pokemon["ability"]
    elif "baseAbility" in request_pokemon:
        self.ability = request_pokemon["baseAbility"]

    self._last_request = request_pokemon

    condition = request_pokemon["condition"]
    self._set_hp_status(condition)

    if request_pokemon["item"] or self._item != "lost":
        self._item = request_pokemon["item"]

    details = request_pokemon["details"]
    self._update_from_details(details)

    for move in request_pokemon["moves"]:
        self._add_move(move)

    if len(self._moves) > 4:
        moves_to_keep = {
            self.MOVE_CLASS.retrieve_id(move_id)
            for move_id in request_pokemon["moves"]
        }
        self._moves = {
            move_id: move
            for move_id, move in self._moves.items()
            if move_id in moves_to_keep
        }


Pokemon._end_item = my_end_item
Pokemon._switch_out = my_switch_out
Pokemon._update_from_request= my_update_from_request

team_2 = """
Drifblim @ Heavy-Duty Boots  
Ability: Unburden  
EVs: 252 HP / 252 Atk  
- Acrobatics
"""

player_2 = RandomPlayer(
        battle_format="gen8ubers", team=team_2, max_concurrent_battles=10
    )

class MaxDamagePlayer(MyPlayer):


    def choose_move(self, battle):
        battle2=list(player_2._battles.values())[-1]

        #print all information
        
        print("\n","turn:",battle._turn)       
        print("player:")
        self.show_down(battle)
        print("opponent:")
        player_2.show_down(battle2)
        print("field:",battle._fields,battle._weather)
        print("side:",battle._side_conditions," oppo_side:",battle._opponent_side_conditions)
        
        #self.show_opponent(battle)

        if battle.available_moves and np.random.uniform() < 0.8:
            if np.random.uniform() < 0.75:
                best_move = max(battle.available_moves, key=lambda move: move.base_power * move.type.damage_multiplier(*battle.opponent_active_pokemon.types) )
            else:
                best_move = battle.available_moves[int(np.random.uniform() * len(battle.available_moves))]
        #    print("move",best_move._id)
            return self.create_order(best_move)

        else:
            if battle.available_switches:
                switch = battle.available_switches[int(np.random.uniform() * len(battle.available_switches))]
            #    print("switch",switch._species)
                return self.create_order(switch)
            else:
                return self.choose_default_move(battle)


def teampreview_performance(mon_a, mon_b):
    # We evaluate the performance on mon_a against mon_b as its type advantage
    a_on_b = b_on_a = -np.inf
    for type_ in mon_a.types:
        if type_:
            a_on_b = max(a_on_b, type_.damage_multiplier(*mon_b.types))
    # We do the same for mon_b over mon_a
    for type_ in mon_b.types:
        if type_:
            b_on_a = max(b_on_a, type_.damage_multiplier(*mon_a.types))
    # Our performance metric is the different between the two
    return a_on_b - b_on_a


async def main():
    team_1 = """
Amoonguss  @  Eject Button  
Ability: Regenerator  
EVs: 252 HP / 252 Def / 4 Spe  
IVs: 0 Atk  
- Spore


Treecko @ Coba Berry 
Ability: Overgrow  
EVs: 252 SpA / 252 SpD / 4 Spe  
IVs: 0 Atk  
- Agility  

"""
    fd=open("test.txt","w")
    sys.stdout=fd

    max_damage_player = MaxDamagePlayer(
        battle_format="gen8ubers", team=team_1, max_concurrent_battles=10
    )

    n_battles = 1
    await max_damage_player.battle_against(player_2, n_battles)

    fd.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
