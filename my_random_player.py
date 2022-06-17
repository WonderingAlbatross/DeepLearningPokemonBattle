# -*- coding: utf-8 -*-
"""This module defines a random players baseline
"""
import numpy as np
from my_player import MyPlayer
from poke_env.player.battle_order import BattleOrder




class RandomPlayer(MyPlayer):
    def choose_move(self, battle) -> BattleOrder:
        available_orders = [BattleOrder(move) for move in battle.available_moves]
        available_switchs= [BattleOrder(switch) for switch in battle.available_switches]
        if np.random.uniform()<0.8:
            if available_orders:
                return available_orders[int(np.random.uniform() * len(available_orders))]
            else:
                return self.choose_default_move(battle)
        else:
            if available_switchs:
                return available_switchs[int(np.random.uniform() * len(available_switchs))]
            else:
                return self.choose_default_move(battle)
                