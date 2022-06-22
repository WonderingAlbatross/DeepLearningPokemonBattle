# -*- coding: utf-8 -*-
"""This module defines a base class for players.
"""

import asyncio
import orjson
import random



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


import vector_converter as vc
from pokemonset import PokemonSet

class MyPlayer(Player):
    async def _handle_battle_message(self, split_messages: List[List[str]]) -> None:
        """Handles a battle message.

        :param split_message: The received battle message.
        :type split_message: str
        """
        # Battle messages can be multiline

        #print(split_messages,"\n")

        if (
            len(split_messages) > 1
            and len(split_messages[1]) > 1
            and split_messages[1][1] == "init"
        ):
            battle_info = split_messages[0][0].split("-")
            battle = await self._create_battle(battle_info)
        else:
            battle = await self._get_battle(split_messages[0][0])

        for split_message in split_messages[1:]:
            if len(split_message) <= 1:
                continue
            elif split_message[1] in self.MESSAGES_TO_IGNORE:
                pass
            elif split_message[1] == "request":
                if split_message[2]:
                    request = orjson.loads(split_message[2])
                    battle._parse_request(request)
                    if battle.move_on_next_request:
                        await self._handle_battle_request(battle)
                        battle.move_on_next_request = False
            elif split_message[1] == "win" or split_message[1] == "tie":
                if split_message[1] == "win":
                    battle._won_by(split_message[2])
                    if battle._won:
                        print(split_message[2],"wins\n\n")
                else:
                    battle._tied()
                    print("tied\n")
                await self._battle_count_queue.get()
                self._battle_count_queue.task_done()
                self._battle_finished_callback(battle)
                async with self._battle_end_condition:
                    self._battle_end_condition.notify_all()
            elif split_message[1] == "error":
                self.logger.log(
                    25, "Error message received: %s", "|".join(split_message)
                )
                if split_message[2].startswith(
                    "[Invalid choice] Sorry, too late to make a different move"
                ):
                    if battle.trapped:
                        await self._handle_battle_request(battle)
                elif split_message[2].startswith(
                    "[Unavailable choice] Can't switch: The active Pokémon is "
                    "trapped"
                ) or split_message[2].startswith(
                    "[Invalid choice] Can't switch: The active Pokémon is trapped"
                ):
                    battle.trapped = True
                    await self._handle_battle_request(battle)
                elif split_message[2].startswith(
                    "[Invalid choice] Can't switch: You can't switch to an active "
                    "Pokémon"
                ):
                    await self._handle_battle_request(battle, maybe_default_order=True)
                elif split_message[2].startswith(
                    "[Invalid choice] Can't switch: You can't switch to a fainted "
                    "Pokémon"
                ):
                    await self._handle_battle_request(battle, maybe_default_order=True)
                elif split_message[2].startswith(
                    "[Invalid choice] Can't move: Invalid target for"
                ):
                    await self._handle_battle_request(battle, maybe_default_order=True)
                elif split_message[2].startswith(
                    "[Invalid choice] Can't move: You can't choose a target for"
                ):
                    await self._handle_battle_request(battle, maybe_default_order=True)
                elif split_message[2].startswith(
                    "[Invalid choice] Can't move: "
                ) and split_message[2].endswith("needs a target"):
                    await self._handle_battle_request(battle, maybe_default_order=True)
                elif (
                    split_message[2].startswith("[Invalid choice] Can't move: Your")
                    and " doesn't have a move matching " in split_message[2]
                ):
                    await self._handle_battle_request(battle, maybe_default_order=True)
                elif split_message[2].startswith(
                    "[Invalid choice] Incomplete choice: "
                ):
                    await self._handle_battle_request(battle, maybe_default_order=True)
                elif split_message[2].startswith(
                    "[Unavailable choice]"
                ) and split_message[2].endswith("is disabled"):
                    battle.move_on_next_request = True
                elif split_message[2].startswith(
                    "[Invalid choice] Can't move: You sent more choices than unfainted"
                    " Pokémon."
                ):
                    await self._handle_battle_request(battle, maybe_default_order=True)
                else:
                    self.logger.critical("Unexpected error message: %s", split_message)
            elif split_message[1] == "turn":
                battle._parse_message(split_message)

                # todo: record damage (also crit, anti-type berry) and transmit to building guesser


                await self._handle_battle_request(battle)
            elif split_message[1] == "teampreview":
                battle._parse_message(split_message)
                await self._handle_battle_request(battle, from_teampreview_request=True)
            elif split_message[1] == "bigerror":
                self.logger.warning("Received 'bigerror' message: %s", split_message)
            else:
                battle._parse_message(split_message)



    def show_info(self,_mon):
        ps = PokemonSet(_mon)
        stats = ps._stats
        moves = ps._mon._moves
        ability = ps._mon._ability
        item = ps._mon._item                        
        print(ps._mon._species,stats,ability)
        if item:
            print("item:",item)
        print("status:",_mon._status,_mon._status_counter)
        print(moves)
        print(vc.pokemon_vectorize(ps))
        if _mon.active:
            boosts = list(_mon._boosts.values())
            acc = boosts.pop(0)
            eva = boosts.pop(2)
            boosts.append(acc)
            boosts.append(eva)
            print("boosts:",boosts)
            print("effects:",_mon._effects)    
            print("protect_counter:",_mon._protect_counter) 
        


    def show_down(self,battle):
        if battle.active_pokemon:
            _mon = battle.active_pokemon
            self.show_info(_mon)
        for _mon in battle.team.values():
            if not _mon.active:
                self.show_info(_mon)
 

    def show_opponent(self,battle): 
        if battle.opponent_active_pokemon:
            print("status:",battle.opponent_active_pokemon._status,battle.opponent_active_pokemon._status_counter)
            print("boosts:",battle.opponent_active_pokemon._boosts)
            print("effects:",battle.opponent_active_pokemon._effects)    
            print("protect_counter:",battle.opponent_active_pokemon._protect_counter)
            print("_item:",battle.opponent_active_pokemon._item)
            print("_ability:",battle.opponent_active_pokemon._ability)
            print("_moves:",battle.opponent_active_pokemon._moves)

