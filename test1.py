# -*- coding: utf-8 -*-
import asyncio
import orjson
import numpy as np
import time
import csv
import os

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
from poke_env.environment.effect import Effect
from poke_env.environment.field import Field
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.side_condition import STACKABLE_CONDITIONS, SideCondition
from poke_env.environment.weather import Weather
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


scorelist = []
vectorlist = []
traceback_factor_1 = 0.9
traceback_factor_2 = 0.7
traceback_factor_3 = 0.3
fainting_score = 0
value_score = 200
winning_score = 500
filename = "test.csv"
debug_mode = True



def my_won_by(self, player_name: str):

    global scorelist
    global vectorlist
    battle2=list(player_2._battles.values())[-1]
    if player_name == self._player_username:
        self._won = True
        if self != battle2:
            if scorelist:
                scorelist += [getscore(self,battle2,scorelist[-1] + winning_score)]
    else:
        self._won = False
        if self != battle2:
            if scorelist:
                scorelist += [getscore(self,battle2,scorelist[-1] - winning_score)]

    if self != battle2:
        if scorelist:
            v = np.array(vectorlist)
            s0 = np.array([tracebacked_scorelist(scorelist,1)[1:]]).T
            s1 = np.array([tracebacked_scorelist(scorelist,traceback_factor_1)[1:]]).T
            s2 = np.array([tracebacked_scorelist(scorelist,traceback_factor_2)[1:]]).T
            s3 = np.array([tracebacked_scorelist(scorelist,traceback_factor_3)[1:]]).T     
            u = np.append(v,s0,axis=1)
            u = np.append(u,s1,axis=1)
            u = np.append(u,s2,axis=1)
            u = np.append(u,s3,axis=1)
            with open(filename,"a",newline = "") as data:
                writer = csv.writer(data) 
                writer.writerows(u.astype(np.float32()).tolist()[1:])
        scorelist = []
        vectorlist = []
    self._finish_battle()


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
Pokemon._update_from_request = my_update_from_request
AbstractBattle._won_by = my_won_by

team_2 = """
Chansey (F) @ Eviolite  
Ability: Natural Cure  
EVs: 252 HP / 252 SpD  
IVs: 0 Atk  
- Dazzling Gleam
"""
'''
player_2 = RandomPlayer(
    battle_format="gen8ubers", team=team_2, max_concurrent_battles=1
)

'''
player_2 = AmateurPlayer(
    battle_format="gen8randombattle", max_concurrent_battles=1
)


class CheatingPlayer(MyPlayer):


    def choose_move(self, battle):
        battle2=list(player_2._battles.values())[-1]
        if isinstance(battle2.active_pokemon,type(None)):
            battle._finish_battle()

#        start_time = time.time()    
        if debug_mode:   
            print("turn:",battle._turn)
#        if self.oppohaveactioned[battle]:
            #print("safeswitch")   
        global scorelist
        global vectorlist
        
        score = 0

        
        alive_mon = {}                                                        
        alive_oppo = {}
        for _mon in battle._team:
            if _mon in ("p1: Zoroark","p1: Ditto"):
                return self.choose_default_move()
            if not battle._team[_mon].fainted:
                alive_mon[_mon] = vc.pokemon_vectorize(PokemonSet(battle._team[_mon]),battle._weather,battle._fields)
        for _oppo in battle2._team:
            if _oppo in ("p2: Zoroark","p2: Ditto"):
                return self.choose_default_move()
            if not battle2._team[_oppo].fainted:
                alive_oppo[_oppo] = vc.pokemon_vectorize(PokemonSet(battle2._team[_oppo]),battle._weather,battle._fields)
        if not (alive_mon and alive_oppo):
            return self.choose_default_move()



        mon_vector_dict = vc.vector_dict(battle,battle2,alive_mon,alive_oppo)
        oppo_vector_dict = vc.vector_dict(battle2,battle,alive_oppo,alive_mon)
        mon_switch_dict = vc.switch_dict(battle,battle2,alive_mon,alive_oppo)
        threating_rate = vc.threating_rate_dict(mon_vector_dict,oppo_vector_dict,alive_mon,alive_oppo)
        threating_rate_matrix = np.zeros((len(alive_mon),len(alive_oppo)))

        i = 0
        for _mon in threating_rate:
            j = 0
            for _oppo in threating_rate[_mon]:
                threating_rate_matrix[i,j] = threating_rate[_mon][_oppo]
                j += 1
            i += 1

        temp_matrix = np.reciprocal(threating_rate_matrix).T.dot(threating_rate_matrix)
        temp_eigenvalues = np.linalg.eig(temp_matrix)
        temp_e_list = np.real(temp_eigenvalues[0]).tolist()
        _k = np.real(temp_eigenvalues[0][temp_e_list.index(max(temp_e_list))]) ** 0.5
        oppo_value = np.real(temp_eigenvalues[1][:,temp_e_list.index(max(temp_e_list))])
        mon_value = threating_rate_matrix.dot(oppo_value)
        oppo_value = np.abs(oppo_value) * _k
        mon_value = np.abs(mon_value)

        score += (sum(mon_value)-sum(oppo_value))*value_score
        if debug_mode:   
            print(alive_mon.keys(),mon_value)
            print(alive_oppo.keys(),oppo_value)
            print("score:",score)
            print("player:")
            self.show_down(battle)
            print("opponent:")
            player_2.show_down(battle2)
 #       #print("weather & field:",battle._weather,battle._fields)
 #       #print("side:",battle._side_conditions," oppo_side:",battle._opponent_side_conditions)
        
        #self.show_opponent(battle)

        #print(battle.active_pokemon._species,"->",battle2.active_pokemon._species)
        if self.oppohaveactioned[battle]:
            i = 0
            for _oppo in alive_oppo:
                if battle2._team[_oppo].active:
                    _trm = threating_rate_matrix[:,i]
                    j = 0
                    for _mon in alive_mon:
                        if j ==  np.argmax(_trm):
                            if debug_mode:   
                                print("safely switch",battle._team[_mon])
                            return self.create_order(battle._team[_mon])
                        j += 1
                i += 1
            j = 0
            for _mon in alive_mon:
                if j == np.argmax(mon_value):
                    print("safely switch",battle._team[_mon])
                    return self.create_order(battle._team[_mon])
                j += 1

            
        if battle.available_moves:
            best_move = movechooser(battle,battle2)
        else:
            if battle.available_switches:
                best_move = switchchooser(battle,battle2)
        
        #print("choose move:",best_move)
        moto = np.zeros(100)
        mott = np.zeros(100)
        motn = np.zeros(100)
        oetm = np.zeros(100)
        obtm = np.zeros(100)
        ms = np.zeros(19)
        os = np.zeros(19)
        wh = np.zeros(9)
        wh = vc.weather_field_vectorize(battle._weather,battle._fields,battle._turn)
        sc = np.zeros(7)
        sc = vc.side_condition_vectorize(battle._side_conditions,battle._turn)[:7]
        oc = np.zeros(7)
        oc = vc.side_condition_vectorize(battle._opponent_side_conditions,battle._turn)[:7]
        tr = 1
        mtr = 1
        otr = 1




        if best_move in battle.available_moves:
            if best_move._id == "struggle":
                return self.choose_default_move()
            j = 0
            for _mon in alive_mon:
                if battle._team[_mon].active:
                    i = 0
                    mtr = mon_value[j]
                    ms += alive_mon[_mon][6:]
                    motn += mon_vector_dict[_mon][min(alive_oppo, key=lambda _oppo: mon_vector_dict[_mon][_oppo][best_move._id][1]+mon_vector_dict[_mon][_oppo][best_move._id][2]+mon_vector_dict[_mon][_oppo][best_move._id][3])][best_move._id]
                    for _oppo in alive_oppo:
                        mott += mon_vector_dict[_mon][_oppo][best_move._id] * oppo_value[i]                       
                        moveset = mon_vector_dict[_mon][_oppo]
                        if battle2._team[_oppo].active:
                            otr = oppo_value[i]
                            moveset = mon_vector_dict[_mon][_oppo]
                            tr = threating_rate[_mon][_oppo]
                            moto += moveset[best_move._id]
                            os += alive_oppo[_oppo][6:]                       
                            oppo_moveset = oppo_vector_dict[_oppo][_mon]
                            deadly_moves = {}
                            for _move in oppo_moveset:                                              #todo: if choiseband 
                                oetm += oppo_moveset[_move] / len(oppo_moveset)
                                if oppo_moveset[_move][1]+oppo_moveset[_move][2]+oppo_moveset[_move][3] > alive_mon[_mon][7]:
                                    deadly_moves[_move] = oppo_moveset[_move]
                            if deadly_moves:
                                obtm += deadly_moves[max(deadly_moves, key=lambda _move: deadly_moves[_move][0])]
                            else:
                                obtm += oppo_moveset[max(oppo_moveset, key=lambda _move: oppo_moveset[_move][1]+oppo_moveset[_move][2]+oppo_moveset[_move][3])]
                        i += 1
                j += 1
                
            mott /= sum(oppo_value)
            learning_vector = np.append(np.append(np.append(np.append(np.append(moto,[mott,motn,oetm,obtm]),[ms,os]),[wh]),[sc,oc]),[tr,mtr,otr])
        
        if best_move in battle.available_switches:
            active_mon = ""
            for _mon in alive_mon:
                if battle._team[_mon].active:
                    active_mon = _mon
            j = 0
            for _mon in alive_mon:
                if best_move == battle._team[_mon]:
                    i = 0
                    mtr = mon_value[j]
                    ms += alive_mon[_mon][6:]
                    motn += mon_switch_dict[_mon][max(alive_oppo, key=lambda _oppo: sum(mon_switch_dict[_mon][_oppo][13:20]))]
                    for _oppo in alive_oppo:
                        mott += mon_switch_dict[_mon][_oppo] * oppo_value[i]
                        moveset = mon_vector_dict[_mon][_oppo]
                        if battle2._team[_oppo].active:
                            otr = oppo_value[i]
                            moveset = mon_vector_dict[_mon][_oppo]
                            tr = threating_rate[_mon][_oppo]
                            moto += mon_switch_dict[_mon][_oppo]
                            os += alive_oppo[_oppo][6:]
                            if active_mon and self.oppohaveactioned[battle] == False:
                                oppo_moveset = oppo_vector_dict[_oppo][active_mon]
                                deadly_moves = {}
                                for _move in oppo_moveset:
                                    oetm += oppo_vector_dict[_oppo][_mon][_move] / len(oppo_moveset)
                                    if oppo_moveset[_move][1]+oppo_moveset[_move][2]+oppo_moveset[_move][3] > alive_mon[_mon][7]:
                                        deadly_moves[_move] = oppo_moveset[_move]
                                if deadly_moves:
                                    obtm += oppo_vector_dict[_oppo][_mon][max(deadly_moves, key=lambda _move: deadly_moves[_move][0])]
                                else:
                                    obtm += oppo_vector_dict[_oppo][_mon][max(oppo_moveset, key=lambda _move: oppo_moveset[_move][1]+oppo_moveset[_move][2]+oppo_moveset[_move][3])]
                            else:
                                for _move in oppo_vector_dict[_oppo][_mon]:
                                    oetm += oppo_vector_dict[_oppo][_mon][_move] / len(oppo_vector_dict[_oppo][_mon])                                
                        i += 1
                j += 1

            mott /= sum(oppo_value)
            learning_vector = np.append(np.append(np.append(np.append(np.append(moto,[mott,motn,oetm,obtm]),[ms,os]),[wh]),[sc,oc]),[tr,mtr,otr])
        vectorlist += [learning_vector.tolist()]
        scorelist += [score]
        print("choose", best_move)
        return self.create_order(best_move)

        



def movechooser(battle,battle2):
    global scorelist
    global vectorlist
    a = len(battle.available_moves)
    b = len(battle.available_switches)
    available = battle.available_moves + battle.available_switches
    choise = []
    choise_weight = []
    weight = [0 for i in range(0,a+b)]
    for i in range(0,a):
        weight[i] = simply_modified_weight(battle.available_moves[i],battle.active_pokemon,battle2.active_pokemon,battle,battle2)
        if debug_mode:        
            print("use",battle.available_moves[i]._id,weight[i])
            vc.vectordebug(vc.modified_move_vector(battle.available_moves[i],PokemonSet(battle.active_pokemon),PokemonSet(battle2.active_pokemon),battle._weather,battle._fields,battle._side_conditions,battle._opponent_side_conditions))


    oppo_most_threating_move = max(battle2.active_pokemon._moves, key=lambda move: simply_modified_weight(Move(move),battle2.active_pokemon,battle.active_pokemon,battle2,battle))
    threating_rate = simply_modified_weight(Move(oppo_most_threating_move),battle2.active_pokemon,battle.active_pokemon,battle2,battle)
    for i in range(0,b):
        weight[a+i] = threating_rate
        oppo_most_threating_move_2 = max(battle2.active_pokemon._moves, key=lambda move: simply_modified_weight(Move(move),battle2.active_pokemon,battle.available_switches[i],battle2,battle))
        weight[a+i] *= simply_modified_weight(Switch(),battle.available_switches[i],battle2.active_pokemon,battle,battle2)
        weight[a+i] /= simply_modified_weight(Move(oppo_most_threating_move),battle2.active_pokemon,battle.available_switches[i],battle2,battle) + 0.0001
        weight[a+i] /= simply_modified_weight(Move(oppo_most_threating_move_2),battle2.active_pokemon,battle.available_switches[i],battle2,battle) ** 0.5 +0.0001
        most_threating_move = max(battle.available_switches[i]._moves, key=lambda move: simply_modified_weight(Move(move),battle.available_switches[i],battle2.active_pokemon,battle,battle2))
        weight[a+i] *= simply_modified_weight(Move(most_threating_move),battle.available_switches[i],battle2.active_pokemon,battle,battle2) ** 0.5
        if debug_mode:        
            print("switch",battle.available_switches[i]._species,weight[a+i])
 #       vc.vectordebug(vc.modified_move_vector(Switch(),PokemonSet(battle.available_switches[i]),PokemonSet(battle2.active_pokemon),battle._weather,battle._fields,battle._side_conditions,battle._opponent_side_conditions))
    for j in range(0,min(a+b,5)):
        k = list(weight).index(max(weight))
        choise_weight += [weight.pop(k)]
        choise += [available.pop(k)]
    if sum(choise_weight):
        _move = np.random.choice(choise, 1 , p = choise_weight/sum(choise_weight))[0]
    else:
        _move = np.random.choice(choise, 1)[0]
    return _move

def switchchooser(battle,battle2):
    global scorelist
    global vectorlist
    a = len(battle.available_switches)
    threating_rate=[1 for i in range(0,a)]
    available = [] + battle.available_switches
    choise = []
    choise_weight = []
    for i in range(0,a):
        oppo_most_threating_move = Move(max(battle2.active_pokemon._moves, key=lambda move: simply_modified_weight(Move(move),battle2.active_pokemon,battle.available_switches[i],battle2,battle)))
        threating_rate[i] /= simply_modified_weight(oppo_most_threating_move,battle2.active_pokemon,battle.available_switches[i],battle2,battle) ** 0.5
        threating_rate[i] *= simply_modified_weight(Switch(),battle.available_switches[i],battle2.active_pokemon,battle,battle2) ** 0.5
        most_threating_move = Move(max(battle.available_switches[i]._moves, key=lambda move: simply_modified_weight(Move(move),battle.available_switches[i],battle2.active_pokemon,battle,battle2)))
        threating_rate[i] *= simply_modified_weight(most_threating_move,battle.available_switches[i],battle2.active_pokemon,battle,battle2) ** 0.5
        if debug_mode:
            print("switch",battle.available_switches[i]._species,threating_rate[i])
#       vc.vectordebug(vc.modified_move_vector(Switch(),PokemonSet(battle.available_switches[i]),PokemonSet(battle2.active_pokemon),battle._weather,battle._fields,battle._side_conditions,battle._opponent_side_conditions))
    for j in range(0,min(a,3)):
        k = list(threating_rate).index(max(threating_rate))
        choise_weight += [threating_rate.pop(k)]
        choise += [available.pop(k)]
    _switch = np.random.choice(choise, 1 , p = choise_weight/sum(choise_weight))[0]  

    return _switch



def simply_modified_weight(move,mon,oppo,battle,battle2):
    v=vc.modified_move_vector(move,PokemonSet(mon),PokemonSet(oppo),battle._weather,battle._fields,battle._side_conditions,battle._opponent_side_conditions)
    w=np.zeros(100)
    w[1] = (oppo._current_hp/oppo._max_hp+1)/1.5
    w[2] = (oppo._current_hp/oppo._max_hp+1)/1.5 
    w[3] = (oppo._current_hp/oppo._max_hp+1)/1.5                          
    w[5] = v[1]+v[2]
    w[6:13] = np.ones(7)*0.1*(oppo._current_hp/oppo._max_hp+1)
    w[13:20] = np.ones(7)*-0.1*(oppo._current_hp/oppo._max_hp+1)
    w[20:25] =  np.ones(5)*0.2
    w[25] = np.arctan(v[0])
    w[26] = 0.2*(1.2-mon._current_hp/mon._max_hp)
    w[27] = 0.2*(1.2-mon._current_hp/mon._max_hp)
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
    w[70:78] = np.ones(8)*0.6
    w[78] = 0.2
    w[81] = 0.3
    w[82] = 0.2
    w[83:91] = np.ones(8)*0.5
    w[93:98] = np.ones(5)*0.2
    w[98] = -0.1
    w[99] = 0.1
    
    t = w.dot(v) * v[4] * (np.arctan(20*min(1.5,v[0]))+6)
    
    if t > 100:
        print("error!",move)
        vc.vectordebug(v)
        print(move,mon._species,oppo._species)
    
    weight = np.exp(min(t,4))

    return weight



def getscore(battle,battle2,winning_score):
    s = 0
    '''
    for _oppo in battle._opponent_team:
        oppo = battle._opponent_team[_oppo]
        if oppo.fainted:
            s += 2 * fainting_score
        else:
            s += ( 1 - oppo._current_hp/oppo._max_hp ) * fainting_score
    for _mon in battle._team:
        mon = battle._team[_mon]
        if mon.fainted:
            s -= 2 * fainting_score
        else:
            s -= ( 1 - mon._current_hp/mon._max_hp ) * fainting_score
    
    side = battle._side_conditions
    oppo_side = battle._opponent_side_conditions
    if SideCondition.SPIKES in side:
        s -= side[SideCondition.SPIKES] * 30
    if SideCondition.STEALTH_ROCK in side:
        s -= 50   
    if SideCondition.STICKY_WEB in side:
        if Field.TRICK_ROOM in battle._fields:
            s += 40 
        else:
            s -= 40
    if SideCondition.TOXIC_SPIKES in side:
        s -= side[SideCondition.TOXIC_SPIKES] * 30

    if SideCondition.SPIKES in oppo_side:
        s += oppo_side[SideCondition.SPIKES] * 30
    if SideCondition.STEALTH_ROCK in oppo_side:
        s += 50   
    if SideCondition.STICKY_WEB in oppo_side:
        if Field.TRICK_ROOM in battle._fields:
            s -= 40 
        else:
            s += 40
    if SideCondition.TOXIC_SPIKES in oppo_side:
        s += oppo_side[SideCondition.TOXIC_SPIKES] * 30
    '''
    s += winning_score
    
    return s

def tracebacked_scorelist(score:list,traceback_factor):
    k = len(score)
    s = [0 for i in range(len(score))]
    for i in range(k-1,0,-1):
        s[i] = score[i]-score[i-1]
    for i in range(k-1,0,-1):      
        s[i-1] += (1-traceback_factor)*s[i]
        s[i] *= traceback_factor
    return s




async def main():

    if os.path.isfile(filename) == False:
        with open(filename,"w",newline = "") as data:
            writer = csv.writer(data) 
            writer.writerows([[i for i in range(569)]])

    team_1 = """
Slowbro  
Ability: Oblivious  
EVs: 252 HP  
IVs: 0 Atk  
- Teleport

Rotom-Wash  
Ability: Levitate  
EVs: 252 HP  
IVs: 0 Atk  
- Volt Switch

Corviknight @ Iron Ball  
Ability: Pressure  
EVs: 252 HP  
IVs: 0 Spe  
- U-turn

"""
    debug = open("debug.txt","w")
    sys.stdout = debug
    

    cheating_player_1 = CheatingPlayer(
        battle_format="gen8randombattle", max_concurrent_battles=1
    )

    n_battles = 1
    await cheating_player_1.battle_against(player_2, n_battles)

    print("CheatingPlayer won %d / %d battles"% (cheating_player_1.n_won_battles, n_battles))
    debug.close()



if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

