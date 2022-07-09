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
    __slots__ = (                                       #add forceswitchrequest
        "forceswitchrequest",
        "oppohaveactioned"                                       
    )
    def __init__(
        self,
        player_configuration: Optional[PlayerConfiguration] = None,
        *,
        avatar: Optional[int] = None,
        battle_format: str = "gen8randombattle",
        log_level: Optional[int] = None,
        max_concurrent_battles: int = 1,
        save_replays: Union[bool, str] = False,
        server_configuration: Optional[ServerConfiguration] = None,
        start_timer_on_battle_start: bool = False,
        start_listening: bool = True,
        team: Optional[Union[str, Teambuilder]] = None,
    ) -> None:
        if player_configuration is None:
            player_configuration = _create_player_configuration_from_player(self)

        if server_configuration is None:
            server_configuration = LocalhostServerConfiguration

        super(Player, self).__init__(
            player_configuration=player_configuration,
            avatar=avatar,
            log_level=log_level,
            server_configuration=server_configuration,
            start_listening=start_listening,
        )

        self._format: str = battle_format
        self._max_concurrent_battles: int = max_concurrent_battles
        self._save_replays = save_replays
        self._start_timer_on_battle_start: bool = start_timer_on_battle_start

        self._battles: Dict[str, AbstractBattle] = {}
        self._battle_semaphore: Semaphore = Semaphore(0)

        self._battle_start_condition: Condition = Condition()
        self._battle_count_queue: Queue = Queue(max_concurrent_battles)
        self._battle_end_condition: Condition = Condition()
        self._challenge_queue: Queue = Queue()

        if isinstance(team, Teambuilder):
            self._team = team
        elif isinstance(team, str):
            self._team = ConstantTeambuilder(team)
        else:
            self._team = None

        self.logger.debug("Player initialisation finished")
        self.forceswitchrequest = {}
        self.oppohaveactioned = {}


    async def _handle_battle_message(self, split_messages: List[List[str]]) -> None:

                # todo: record damage (also crit, anti-type berry) and transmit to building guesser
                # todo: find if enemy have attacked (!focus punch)
                # todo: add outrage/... as encore effect


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
                    if "forceSwitch" in request and request["forceSwitch"][0] is True:            #nvm with "upkeep"
                        self.forceswitchrequest[battle] = 1
                        await self._handle_battle_request(battle)
                    else:
                        if battle.move_on_next_request:
                            await self._handle_battle_request(battle)
                            battle.move_on_next_request = False
            elif split_message[1] == "win" or split_message[1] == "tie":
                if split_message[1] == "win":
                    battle._won_by(split_message[2])                                        #nvm
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
                self.oppohaveactioned[battle] = False                                                         #oppohaveactioned
                battle._parse_message(split_message)
                await self._handle_battle_request(battle)
            elif split_message[1] == "teampreview":
                battle._parse_message(split_message)
                await self._handle_battle_request(battle, from_teampreview_request=True)
            elif split_message[1] == "bigerror":
                self.logger.warning("Received 'bigerror' message: %s", split_message)
            else:
                #battle._parse_message(split_message)
                if split_messages.index(split_message) == len(split_messages)-1 and self.forceswitchrequest.get(battle,0) == 1:
                    self.forceswitchrequest[battle] += 1   
                              
                await self.my_parse_message(battle,split_message)

                
                
            

    async def my_parse_message(self,battle,split_message):
        # ignore things like "['', '-weather', 'RainDance', '[upkeep]']"
        if split_message[1] == "move" and split_message[2].startswith("p2"):
            self.oppohaveactioned[battle] = True 
        if split_message[1] == "-weather":
            if "[upkeep]" in split_message:
                return 0       
        if self.forceswitchrequest.get(battle,0) == 2:
            battle._parse_message(split_message)
            self.forceswitchrequest[battle] = 0
            if battle.move_on_next_request:         
                await self._handle_battle_request(battle)
                battle.move_on_next_request = False                
            return 0
        battle._parse_message(split_message)

    async def _handle_battle_request(
        self,
        battle: AbstractBattle,
        from_teampreview_request: bool = False,
        maybe_default_order=False,
    ):
        if maybe_default_order and random.random() < self.DEFAULT_CHOICE_CHANCE:
            message = self.choose_default_move(battle).message
        elif battle.teampreview:
            if not from_teampreview_request:
                return
            message = self.teampreview(battle)
        else:
            if self.forceswitchrequest.get(battle,0) != 0 :
                message = ""
            else:
                message = self.choose_move(battle).message

        await self._send_message(message, battle.battle_tag)


    def show_info(self,_mon,battle):
        mon = PokemonSet(_mon)
        stats = mon._stats
        moves = mon._mon._moves
        ability = mon._mon._ability
        item = mon._mon._item                        
        print(mon._mon._species,stats,ability,item)
        vc.vectordebug(vc.pokemon_vectorize(mon,battle._weather,battle._fields))
        if _mon.active:
            print("effects:",_mon._effects)    
            #print("protect_counter:",_mon._protect_counter) 


    def show_down(self,battle):
        if battle.active_pokemon:
            _mon = battle.active_pokemon
            self.show_info(_mon,battle)
    #    for _mon in battle.team.values():
    #        if not _mon.active:
    #            self.show_info(_mon,battle)
 

    def show_opponent(self,battle): 
        if battle.opponent_active_pokemon:
            print("status:",battle.opponent_active_pokemon._status,battle.opponent_active_pokemon._status_counter)
            print("boosts:",battle.opponent_active_pokemon._boosts)
            print("effects:",battle.opponent_active_pokemon._effects)    
            print("protect_counter:",battle.opponent_active_pokemon._protect_counter)
            print("_item:",battle.opponent_active_pokemon._item)
            print("_ability:",battle.opponent_active_pokemon._ability)
            print("_moves:",battle.opponent_active_pokemon._moves)

