# -*- coding: utf-8 -*-
import asyncio
import orjson
import numpy as np
import vector_converter as vc
import sys
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.battle import Battle
from poke_env.environment.move import Move
from my_player import MyPlayer
from my_random_player import RandomPlayer
from poke_env.player.battle_order import (
    BattleOrder,
    DefaultBattleOrder,
    DoubleBattleOrder,
)


player_2 = RandomPlayer(
    battle_format="gen8randombattle", max_concurrent_battles=1
)


class MaxDamagePlayer(MyPlayer):


    def choose_move(self, battle):
        battle2=list(player_2._battles.values())[-1]

        #print all information
        
        print("turn:",battle._turn)
        print("player:")
        self.show_down(battle)
        print("opponent:")
        player_2.show_down(battle2)
        print("field:",battle._fields,battle._weather)
        print("side:",battle._side_conditions," oppo_side:",battle._opponent_side_conditions)
        
        

        if battle.available_moves and np.random.uniform() < 0.8:
            if np.random.uniform() < 0.75:
                best_move = max(battle.available_moves, key=lambda move: move.base_power * move.type.damage_multiplier(*battle.opponent_active_pokemon.types) )
            else:
                best_move = battle.available_moves[int(np.random.uniform() * len(battle.available_moves))]
            print("move",best_move._id)
            return self.create_order(best_move)

        else:
            if battle.available_switches:
                switch = battle.available_switches[int(np.random.uniform() * len(battle.available_switches))]
                print("switch",switch._species)
                return self.create_order(switch)
            else:
                return self.choose_default_move(battle)


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






async def main():
    fd=open("test.txt","w")
#    sys.stdout=fd

    max_damage_player_1 = MaxDamagePlayer(
        battle_format="gen8randombattle", max_concurrent_battles=1
    )

    n_battles = 1
    await max_damage_player_1.battle_against(player_2, n_battles)

    print(
        "Max damage player won %d / %d battles"
        % (max_damage_player_1.n_won_battles, n_battles)
    )




if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
