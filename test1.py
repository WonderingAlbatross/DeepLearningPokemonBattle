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
from poke_env.environment.status import Status
from my_player import MyPlayer
from my_random_player import RandomPlayer
from amateur_player import AmateurPlayer
from poke_env.player.battle_order import (
    BattleOrder,
    DefaultBattleOrder,
    DoubleBattleOrder,
)


import vector_converter as vc
from vector_converter import Switch
from pokemonset import PokemonSet



def my_end_item(self, item):
    self._item = "lost"                         #change 1:add lost as item 
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
    if self._item == "lost":                    #change 1:add lost as item 
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

    if request_pokemon["item"] or not self._item == "lost":
        self._item = request_pokemon["item"]                    #change 1:add lost as item

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


player_2 = AmateurPlayer(
    battle_format="gen8randombattle", max_concurrent_battles=1
)


class CheatingPlayer(MyPlayer):


    def choose_move(self, battle):
        

        #print all information
        battle2=list(player_2._battles.values())[-1]


        print("turn:",battle._turn)       
        print("player:")
        self.show_down(battle)
        print("opponent:")
        player_2.show_down(battle2)
        print("weather & field:",battle._weather,battle._fields)
        print("side:",battle._side_conditions," oppo_side:",battle._opponent_side_conditions)
        
        #self.show_opponent(battle)
        if battle2.active_pokemon is not None:
            if battle.available_moves:
                best_move = movechooser(battle,battle2)
            else:
                if battle.available_switches:
                    best_move = switchchooser(battle,battle2)
            return self.create_order(best_move)

        else:
           return self.choose_default_move(battle)
        print("\n\n")

    def teampreview(self, battle):
        mon_performance = {}

        # For each of our pokemons
        for i, mon in enumerate(battle.team.values()):
            # We store their average performance against the opponent team
            mon_performance[i] = np.mean(
                [
                    teampreview_performance(mon, opp)
                    for opp in battle.opponent_team.values()
                ]
            )

        # We sort our mons by performance
        ordered_mons = sorted(mon_performance, key=lambda k: -mon_performance[k])

        # We start with the one we consider best overall
        # We use i + 1 as python indexes start from 0
        #  but showdown's indexes start from 1
        return "/team " + "".join([str(i + 1) for i in ordered_mons])

        #winning signal changed only


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

def movechooser(battle,battle2):
    a = len(battle.available_moves)
    b = len(battle.available_switches)
    available = battle.available_moves + battle.available_switches
    choise = []
    choise_weight = []
    weight = [0 for i in range(0,a+b)]
    for i in range(0,a):
        weight[i] = simply_modified_weight(battle.available_moves[i],battle.active_pokemon,battle2.active_pokemon,battle,battle2)
        print(battle.available_moves[i]._id,weight[i])

    oppo_most_threating_move = max(battle2.active_pokemon._moves, key=lambda move: simply_modified_weight(Move(move),battle2.active_pokemon,battle.active_pokemon,battle2,battle))
    threating_rate = simply_modified_weight(Move(oppo_most_threating_move),battle2.active_pokemon,battle.active_pokemon,battle2,battle)
    print("oppo_most_threating_move",oppo_most_threating_move,threating_rate)
    for i in range(0,b):
        weight[a+i] = threating_rate
        oppo_most_threating_move_2 = max(battle2.active_pokemon._moves, key=lambda move: simply_modified_weight(Move(move),battle2.active_pokemon,battle.available_switches[i],battle2,battle))
        weight[a+i] *= simply_modified_weight(Switch(),battle.available_switches[i],battle2.active_pokemon,battle,battle2)
        weight[a+i] /= simply_modified_weight(Move(oppo_most_threating_move),battle2.active_pokemon,battle.available_switches[i],battle2,battle)
        weight[a+i] /= simply_modified_weight(Move(oppo_most_threating_move_2),battle2.active_pokemon,battle.available_switches[i],battle2,battle) ** 0.5
        for _move in battle.available_switches[i]._moves:
            most_threating_move = max(battle.available_switches[i]._moves, key=lambda move: simply_modified_weight(Move(move),battle.available_switches[i],battle2.active_pokemon,battle,battle2))
        weight[a+i] *= simply_modified_weight(Move(most_threating_move),battle.available_switches[i],battle2.active_pokemon,battle,battle2) ** 0.5
        print(battle.available_switches[i]._species,weight[a+i])
    for j in range(0,min(a+b,4)):
        k = list(weight).index(max(weight))
        choise_weight += [weight.pop(k)]
        choise += [available.pop(k)]
    _move = np.random.choice(choise, 1 , p = choise_weight/sum(choise_weight))[0]
    print("move:",_move)
    return _move

def switchchooser(battle,battle2):
    print("switchchooser calculating...")
    a = len(battle.available_switches)
    threating_rate=np.ones(a)
    for i in range(0,a):
        oppo_most_threating_move = max(battle2.active_pokemon._moves, key=lambda move: simply_modified_weight(Move(move),battle2.active_pokemon,battle.available_switches[i],battle2,battle))
        threating_rate[i] /= simply_modified_weight(Move(oppo_most_threating_move),battle2.active_pokemon,battle.available_switches[i],battle2,battle)
        threating_rate[i] *= simply_modified_weight(Switch(),battle.available_switches[i],battle2.active_pokemon,battle,battle2)
        most_threating_move = max(battle.available_switches[i]._moves, key=lambda move: simply_modified_weight(Move(move),battle.available_switches[i],battle2.active_pokemon,battle,battle2))
        threating_rate[i] *= simply_modified_weight(Move(most_threating_move),battle.available_switches[i],battle2.active_pokemon,battle,battle2) ** 0.5
        print(battle.available_switches[i]._species,threating_rate[i])
    j = list(threating_rate).index(max(threating_rate))
    return battle.available_switches[j]



def simply_modified_weight(move,mon,oppo,battle,battle2):
    v=vc.modified_move_vector(move,PokemonSet(mon),PokemonSet(oppo),battle._weather,battle._fields,battle._side_conditions,battle._opponent_side_conditions)
    w=np.zeros(100)
    w[1] = 1
    w[2] = 1
    w[5] = v[1]+v[2]
    w[6:13] = np.ones(7)*0.2
    w[13:20] = np.ones(7)*-0.1
    w[20:25] =  np.ones(5)*0.2
    w[25] = np.arctan(v[0])
    w[26] = 0.5
    w[27] = 0.5*(v[1]+v[2])
    w[28] = (1-v[4])*0.5
    w[35] = -0.5*(v[1]+v[2])
    w[36] = 0.1*(v[1]+v[2])
    w[37] = -0.5*(v[1]+v[2])
    w[41] = -0.05
    w[42] = 0.05
    w[43] = 0.05
    w[44] = 0.1
    w[45] = 0.05
    w[46] = 0.05
    w[50] = 0.1
    w[51] = 0.1
    w[52] = 0.1
    w[53] = 1
    w[54] = 0.3
    w[55] = 0.3
    w[56] = 0.1
    w[57] = 0.7
    w[58] = 0.3
    w[59] = 0.2
    w[60] = 0.2
    w[61] = 0.2
    w[62] = 0.5
    w[63] = -0.5
    w[67] = 0.5
    w[68] = 0.3
    w[69] = 0.3
    w[70:78] = np.ones(8)*0.4
    w[78] = 0.2
    w[81] = 0.3
    w[82] = 0.2
    w[83:91] = np.ones(8)*0.5
    w[93:98] = np.ones(5)*0.2
    w[98] = -0.1
    w[99] = 0.1
    t = w.dot(v) * v[4] * (np.arctan(20*v[0])+6)
    if t > 10:
        print("error!")
        vc.vectordebug(v)
        print(move,mon._species,oppo._species)
    weight = np.exp(min(t,4))

    return weight



async def main():
    fd=open("test.txt","w")
    sys.stdout=fd

    max_damage_player_1 = CheatingPlayer(
        battle_format="gen8randombattle", max_concurrent_battles=1
    )

    n_battles = 100
    await max_damage_player_1.battle_against(player_2, n_battles)

    print(
        "CheatingPlayer won %d / %d battles"
        % (max_damage_player_1.n_won_battles, n_battles)
    )
    fd.close()



if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

