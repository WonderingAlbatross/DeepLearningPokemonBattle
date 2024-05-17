from models.pokemon import Pokemon
from models.player import Player
from models.battle import Battle
from models.move import Move

import pandas as pd
import os
import json

col_order = ['battle_id', 'turn', 'total_turn', 'rank', 'weather', 'field', 'condition', 'p1_side', 'p1a_ability', 'p1a_form', 'p1a_hp', 'p1a_item', 'p1a_move', 'p1a_stat_boost', 'p1a_status', 'p1a_status_other', 'p1a_tera', 'p1b_ability', 'p1b_form', 'p1b_hp', 'p1b_item', 'p1b_move', 'p1b_stat_boost', 'p1b_status', 'p1b_status_other', 'p1b_tera', 'p1c_ability', 'p1c_form', 'p1c_hp', 'p1c_item', 'p1c_move', 'p1c_status', 'p1c_tera', 'p1d_ability', 'p1d_form', 'p1d_hp', 'p1d_item', 'p1d_move', 'p1d_status', 'p1d_tera', 'p2_side', 'p2a_ability', 'p2a_form', 'p2a_hp', 'p2a_item', 'p2a_move', 'p2a_stat_boost', 'p2a_status', 'p2a_status_other', 'p2a_tera', 'p2b_ability', 'p2b_form', 'p2b_hp', 'p2b_item', 'p2b_move', 'p2b_stat_boost', 'p2b_status', 'p2b_status_other', 'p2b_tera', 'p2c_ability', 'p2c_form', 'p2c_hp', 'p2c_item', 'p2c_move', 'p2c_status', 'p2c_tera', 'p2d_ability', 'p2d_form', 'p2d_hp', 'p2d_item', 'p2d_move', 'p2d_status', 'p2d_tera', 'win']
sto_dict = {'Taunt':3,'Encore':3,'confusion':4,'Throat Chop':2,'Heal Block':2,'Slow Start':5}

def write_error(string, line, num):
    with open('error.txt', 'a') as file:
        file.write(string+'\t'+num+'\n')
        for item in line:
            file.write(item + '\t')  
        file.write('\n')      



def read_battle_log(file_path):
    with open(file_path, 'r',encoding='utf-8') as file:
        lines = file.readlines()
    battle_log = list(filter(None,[list(filter(None, [item.strip() for item in line.split('|')])) for line in lines]))

    return battle_log

def split_battle_data(battle_log):
    turn_log = []
    current_turn = []
    for line in battle_log:
        if line[0] in ['start', 'turn']:
            if current_turn:
                turn_log.append(current_turn)
                current_turn = [line]
        else:
            current_turn.append(line)
    turn_log.append(current_turn)
    return turn_log

def seperate_pokemon_position(battle,string):
    player_code = string[:2]              #p1
    player = battle.player[player_code]
    position_code = string[2]             #a
    if position_code not in 'ab':
        position_code = None
    pokemon_name = string.split(': ')[1]
    pokemon = player.pokemon[pokemon_name]
    return player, position_code, pokemon_name, pokemon

def get_hp(string):
    if string == '0 fnt':
        return 0
    else:
        return int(string.split('/')[0])
def is_consumable(string):
    if string.endswith('Berry'):
        return True
    if string.endswith('Herb'):
        return True    
    if string.endswith('Policy'):        
        return True
    if string.endswith('Seed'):        
        return True
    if string in ['Throat Spray','Room Service','Adrenaline Orb']:  # more items consumable but no one would bring them      
        return True
    return False
def bt_switch(battle,line):     
    player_code = line[1][:2]              #p1
    player = battle.player[player_code]
    position_code = line[1][2]             #a
    pokemon_name = line[1][5:]              
    pokemon_form = line[2].split(', ')[0]
    if pokemon_name in player.pokemon:
        pokemon = player.pokemon[pokemon_name]
    else:
        player.pokemon[pokemon_name] = Pokemon(pokemon_name)
        pokemon = player.pokemon[pokemon_name]    
    if pokemon_name in player.backup:
        player.backup.remove(pokemon_name)    

    pokemon.form = pokemon_form
    if line[0] != 'replace':
        pokemon_hp = get_hp(line[3])
        pokemon.hp = pokemon_hp
    if len(player.pokemon) > 4:
        write_error('pokemon number error',player.pokemon.keys(),battle.num)
    
    switched_out_pokemon_name = player.position[position_code]
    if switched_out_pokemon_name:                #switch out pokemon if exist
        player.backup.add(switched_out_pokemon_name)
        switched_out_pokemon = player.pokemon[switched_out_pokemon_name]
        if line[-1] in ['[from] Shed Tail','[from] Baton Pass'] and 'Substitute' in switched_out_pokemon.status_other:
            pokemon.status_other['Substitute'] = switched_out_pokemon.status_other['Substitute']
        if 'endability' in switched_out_pokemon.status_other:
            switched_out_pokemon.ability = switched_out_pokemon.status_other['endability']
        if 'ditto' in switched_out_pokemon.status_other:
            switched_out_pokemon.form = 'Ditto'
            switched_out_pokemon.ability = 'Imposter'
            switched_out_pokemon.move = {'Transform':16}
        switched_out_pokemon.status_other = {}
        switched_out_pokemon.stat_boost = {}
        if switched_out_pokemon.status[0] == "tox":
            switched_out_pokemon.status[1] = 1

    player.position[position_code] = pokemon_name












def bt_move(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    move = line[2]
    if move != 'Struggle':
        if move in pokemon.move:
            pokemon.move[move] -= 1
        else:
            pokemon.move[move] = Move(move).get_info('pp')
            pokemon.move[move] -= 1
            if len(pokemon.move) > 4:
                write_error('move error',pokemon.move,battle.num)

def bt_damage(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    pokemon_hp = get_hp(line[2])
    pokemon.hp = pokemon_hp
    if line[-1] == '[from] move: Revival Blessing':
        pokemon.status = [None,0]
        for p in player.position:
            if player.position[p] == pokemon_name:
                player.position[p] = None


def bt_faint(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    pokemon.status = ['fnt',0]
    pokemon.hp = 0
    pokemon.status_other = {}        
    pokemon.stat_boost = {} 



def bt_ability(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    if pokemon.ability != 'As One':
        pokemon.ability = line[2]
    

def bt_item(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    pokemon.item = line[2]

def bt_enditem(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    pokemon.item = None

def bt_activate(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    if line[2].startswith('ability: '):                                                             
        pokemon.ability = line[2][9:]
    if line[2].startswith('item: '):                                 #skill swap also use activate, fix that later
        pokemon.item = line[2][6:]
    if line[2].startswith('move: ') and line[2][6:] in ['Bind','Wrap','Fire Spin','Clamp','Whirlpool','Sand Tomb','Magma Storm','Infestation','Snap Trap','Thunder Cage']:
        pokemon.status_other['partiallytrapped'] = 4 



def bt_boost(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    stat_type = line[2]
    if stat_type in pokemon.stat_boost:
        pokemon.stat_boost[stat_type] += int(line[3])
        if pokemon.stat_boost[stat_type] == 0:
            del pokemon.stat_boost[stat_type]
    else:
        pokemon.stat_boost[stat_type] = int(line[3])


def bt_unboost(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    stat_type = line[2]
    if stat_type in pokemon.stat_boost:
        pokemon.stat_boost[stat_type] -= int(line[3])
        if pokemon.stat_boost[stat_type] == 0:
            del pokemon.stat_boost[stat_type]
    else:
        pokemon.stat_boost[stat_type] = -int(line[3])

def bt_weather(battle,line):
    if '[upkeep]' in line:
        battle.weather[1] -= 1
    else:
        if line[1] == 'none':
            battle.weather = [None,0]
        else:
            battle.weather = [line[1],5]

def bt_terastallize(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    player.has_teraed = True
    pokemon.tera = True
    pokemon.tera_type = line[2] 

def bt_start(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    if line[2].startswith('quarkdrive'):
        pokemon.status_other['Quark Drive'] = line[2]
    elif line[2].startswith('protosynthesis'):
        pokemon.status_other['Protosynthesis'] = line[2]
    else:
        if line[2].startswith('ability: '):
            sto = line[2][9:]
        elif line[2].startswith('move: '):
            sto = line[2][6:]
        else:
            sto = line[2]
        if sto == 'Disable':
            pokemon.status_other[sto] = line[3]
        elif sto in sto_dict:
            pokemon.status_other[sto] = sto_dict[sto]
        elif sto.startswith('perish'):
            pokemon.status_other['perish'] = 4 - int(sto[-1])             # perish song, larger means closer to death
        else:
            pokemon.status_other[sto] = 1

def bt_end(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    if line[-1] == '[partiallytrapped]':
        del pokemon.status_other['partiallytrapped']
    elif line[-1] != '[silent]':
        item = line[2]
        if item.startswith('ability: '):  
            item = item[9:]
        elif item.startswith('move: '):
            item = item[6:]
        if item not in ['Neutralizing Gas','Illusion']:
            if item not in pokemon.status_other:
                write_error('end error',line,battle.num)
            else:
                del pokemon.status_other[item]


def bt_fieldstart(battle,line):
    field = line[1]
    if field.startswith('move: '):
        field = field[6:]
    if field.endswith('Terrain'):
        battle.field = [field,5]
    else:
        battle.condition[field] = 5

def bt_fieldend(battle,line):
    field = line[1]
    if field.startswith('move: '):
        field = field[6:]
    if field.endswith('Terrain'):
        battle.field = [None,0]
    else:
        del battle.condition[field]

def bt_status(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    status = line[2]
    pokemon.status = [status,1]
    if status == 'slp':
        pokemon.status[1] = 3

def bt_curestatus(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    status = line[2]
    if status != pokemon.status[0]:
        write_error('curestatus error',line,battle.num)
    pokemon.status = [None,0]

def bt_sidestart(battle,line):
    player = battle.player[line[1][:2]]
    side = line[2]
    if side.startswith('move: '):
        side = side[6:]
    if side in ['Reflect','Light Screen','Aurora Veil']:
        player.side[side] = 8
    elif side in ['Safeguard','Mist']:
        player.side[side] = 5    
    elif side == 'Tailwind' or side.endswith("Pledge"):   
        player.side[side] = 4
    elif side in ['Spikes','Toxic Spikes','Stealth Rock','Sticky Web']:
        if side in player.side:
            player.side[side] += 1
        else:
            player.side[side] = 1 
    else:
        write_error('sidestart error',line,battle.num)
        player.side[side] = 1    

def bt_sideend(battle,line):
    player = battle.player[line[1][:2]]
    side = line[2]
    if side.startswith('move: '):
        side = side[6:]
    if side not in player.side:
        write_error('sideend error',line,battle.num)
    del player.side[side]

def bt_detailschange(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    pokemon.form = line[2].split(', ')[0]

def bt_transform(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    opponent, target_position_code, target_name, target = seperate_pokemon_position(battle,line[2])
    pokemon.status_other['ditto'] = 1 
    pokemon.form = target.form
    pokemon.ability = target.ability
    for mv in target.move:
        pokemon.move[mv] = 5
    pokemon.stat_boost = {}
    for stat_type in target.stat_boost:
        pokemon.stat_boost[stat_type] = target.stat_boost[stat_type]
#    pokemon.exact_stat = target.exact_stat        #except hp!

def bt_copyboost(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    opponent, target_position_code, target_name, target = seperate_pokemon_position(battle,line[2])
    pokemon.stat_boost = {}
    for stat_type in target.stat_boost:
        pokemon.stat_boost[stat_type] = target.stat_boost[stat_type]

def bt_clearboost(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    pokemon.stat_boost = {}

def bt_clearnegativeboost(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    del_list = []
    for stat_type in pokemon.stat_boost:
        if pokemon.stat_boost[stat_type] < 0:
            del_list.append(stat_type)
    for stat_type in del_list:
        del pokemon.stat_boost[stat_type]

def bt_clearallboost(battle,line):
    for pokemon in battle.player['p1'].pokemon.values():
        pokemon.stat_boost = {} 
    for pokemon in battle.player['p2'].pokemon.values():
        pokemon.stat_boost = {} 

def bt_setboost(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    stat_type = line[2]
    pokemon.stat_boost[stat_type] = int(line[3])

def bt_invertboost(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    for stat_type in  pokemon.stat_boost:
        pokemon.stat_boost[stat_type] *= -1 

def bt_swapboost(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    opponent, target_position_code, target_name, target = seperate_pokemon_position(battle,line[2])
    pokemon.stat_boost,target.stat_boost = target.stat_boost,pokemon.stat_boost

def bt_swap(battle,line):
    player = battle.player[line[1][:2]]
    player.position['a'],player.position['b'] = player.position['b'],player.position['a'] 

def bt_endability(battle,line):
    player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
    pokemon.status_other['endability'] = line[2]


def line_handler(battle,line):
    global erroritem
    if line[0] == 'turn':
        if battle.turn != int(line[1]):
            write_error('turn not match!',line,battle.num)
    elif line[0] in ['switch','drag','replace']:    #'replace' is for Zoroark, fix this later
        bt_switch(battle,line)
    elif line[0] in ['move','-prepare']:                #anim: call another move
        bt_move(battle,line)
    elif line[0] in ['-damage','-heal','-sethp']:
        bt_damage(battle,line)
    elif line[0] == 'faint':
        bt_faint(battle,line)
    elif line[0] == '-ability':               #add ability trace back
        bt_ability(battle,line)
    elif line[0] == '-item':                  #add item trace back (by trick)
        bt_item(battle,line)
    elif line[0] == '-enditem':
        bt_enditem(battle,line)
    elif line[0] == '-activate':
        bt_activate(battle,line)        
    elif line[0] == '-boost':
        bt_boost(battle,line) 
    elif line[0] == '-unboost':
        bt_unboost(battle,line) 
    elif line[0] == '-terastallize':
        bt_terastallize(battle,line)         
    elif line[0] == '-weather':
        bt_weather(battle,line)  
    elif line[0] == '-start':
        bt_start(battle,line) 
    elif line[0] == '-end':
        bt_end(battle,line) 
    elif line[0] == '-fieldstart':
        bt_fieldstart(battle,line)              
    elif line[0] == '-fieldend':
        bt_fieldend(battle,line)
    elif line[0] == '-sidestart':
        bt_sidestart(battle,line)              
    elif line[0] == '-sideend':
        bt_sideend(battle,line)    
    elif line[0] == '-status':
        bt_status(battle,line) 
    elif line[0] == '-curestatus':
        bt_curestatus(battle,line)
    elif line[0] == 'detailschange':
        bt_detailschange(battle,line)         
    elif line[0] == '-transform':
        bt_transform(battle,line) 
    elif line[0] == '-copyboost':
        bt_copyboost(battle,line)
    elif line[0] == '-clearboost':
        bt_clearboost(battle,line)
    elif line[0] == '-clearnegativeboost':
        bt_clearnegativeboost(battle,line)
    elif line[0] == '-clearallboost':
        bt_clearallboost(battle,line)
    elif line[0] == '-setboost':
        bt_setboost(battle,line)
    elif line[0] == '-invertboost':
        bt_invertboost(battle,line)
    elif line[0] == '-swapboost':
        bt_swapboost(battle,line)
    elif line[0] == 'swap':
        bt_swap(battle,line)
    elif line[0] == '-endability':
        bt_endability(battle,line)

    #         'waiting': for xx Pledge
    for n, string in enumerate(line):
        if string.startswith('[from] ability: '):
            if line[-1].startswith('[of] '):
                player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[-1][5:])    
            else:
                player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
            pokemon.ability = string[16:]
        if string.startswith('ability: '):
            player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
            pokemon.ability = string[9:]
        if string.startswith('[from] item: '):
            if line[-1].startswith('[of] '):
                player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[-1][5:])
            else:
                player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
            item = string[13:]
            if not is_consumable(item):
                pokemon.item = item   
        if string.startswith('item: '):
            player, position_code, pokemon_name, pokemon = seperate_pokemon_position(battle,line[1])
            pokemon.item = string[6:]

def get_battle_situation(battle):
    situation = {}
    situation['turn'] = battle.turn
    if battle.weather[0]:
        situation['weather'] = battle.weather[0] + ':' + str(battle.weather[1])
    if battle.field[0]:
        situation['field'] = battle.field[0] + ':' + str(battle.field[1])
    condition = []
    for cdt in battle.condition:
        condition.append(cdt+':'+str(battle.condition[cdt]))
    if condition:
        situation['condition'] = ','.join(condition)
    for pc in ["p1","p2"]:
        player = battle.player[pc]
        side = []
        for sd in player.side:
            side.append(sd+':'+str(player.side[sd]))
        if side:
            situation[pc+'_side'] = ','.join(side)
        for s in ["a","b"]:
            pokemon_name = player.position[s]
            pcs = pc+s
            pokemon = player.pokemon[pokemon_name]
            situation[pcs+'_form'] = pokemon.form
            situation[pcs+'_hp'] = pokemon.hp
            if pokemon.status[0] in ['tox','slp']:
                situation[pcs+'_status'] = pokemon.status[0]+':'+str(pokemon.status[0])
            elif pokemon.status[0]:
                situation[pcs+'_status'] = pokemon.status[0]
            status_others = []
            for sto in pokemon.status_other:
                status_others.append(sto+":"+str(pokemon.status_other[sto]))
            if status_others:
                situation[pcs+'_status_other'] = ','.join(status_others)
            stat_boost = []
            for bst in pokemon.stat_boost:
                stat_boost.append(bst+":"+str(pokemon.stat_boost[bst]))
            if stat_boost:
                situation[pcs+'_stat_boost'] = ','.join(stat_boost)
            situation[pcs+'_item'] = pokemon.item
            situation[pcs+'_ability'] = pokemon.ability
            move = []
            for mv in pokemon.move:
                move.append(mv+":"+str(pokemon.move[mv]))
            if move:
                situation[pcs+'_move'] = ','.join(move)
            if pokemon.tera:
                situation[pcs+'_tera'] = pokemon.tera_type
            else:
                if not player.has_teraed:
                    situation[pcs+'_tera'] = 'unknown'
        sec = 0
        for pokemon_name in player.backup:
            pokemon = player.pokemon[pokemon_name]
            if sec == 0:
                sec += 1
                pcs = pc + 'c'
            elif sec == 1:
                sec += 1
                pcs = pc + 'd'
            else:
                write_error("p1e error",[],battle.num)
                pcs = pc + 'e'
            situation[pcs+'_form'] = pokemon.form
            situation[pcs+'_hp'] = pokemon.hp
            if pokemon.status[0] in ['tox','slp']:
                situation[pcs+'_status'] = pokemon.status[0]+':'+str(pokemon.status[0])
            elif pokemon.status[0]:
                situation[pcs+'_status'] = pokemon.status[0]
            situation[pcs+'_item'] = pokemon.item
            situation[pcs+'_ability'] = pokemon.ability
            move = []
            for mv in pokemon.move:
                move.append(mv+":"+str(pokemon.move[mv]))
            if move:
                situation[pcs+'_move'] = ','.join(move)
            else:
                situation[pcs+'_move'] = 'unknown'
            if pokemon.tera:
                situation[pcs+'_tera'] = pokemon.tera_type
            else:
                if not player.has_teraed:
                    situation[pcs+'_tera'] = 'unknown'                         
        unknown_pokemon_num = 4-len(player.pokemon)
        for i in range(unknown_pokemon_num):
            if sec == 0:
                sec += 1
                pcs = pc + 'c'
            elif sec == 1:
                sec += 1
                pcs = pc + 'd'
            else:
                write_error("p1e error-unknown",[],battle.num)
                pcs = pc + 'e' 
            pokemon = Pokemon('unknown')
            situation[pcs+'_form'] = pokemon.form
            situation[pcs+'_hp'] = pokemon.hp
            situation[pcs+'_item'] = pokemon.item
            situation[pcs+'_ability'] = pokemon.ability
            situation[pcs+'_move'] = 'unknown'
            if not player.has_teraed:
                situation[pcs+'_tera'] = 'unknown'                      



    #print(situation)
    return(situation)

    

def modify_battle_situation(situation_list):
    pass
    #situation['rank'] = battle.rank()
    #situation['turn_total']

def log_process(file_path):
    file_name = file_path.split('/')[-1]
    battle_log = read_battle_log(file_path)
    turn_log = split_battle_data(battle_log)

    #initialize battle
    reg_num = file_name.split('.')[0].split('-')
    battle = Battle(reg_num[0],reg_num[1])
    for line in turn_log[0]:
        if line[0] == 'player':
            battle.player[line[1]] = Player(line[1],line[2],line[4])
        if line[0] == 'poke':
            pokemon_name = line[2].split(',')[0]
            if 'Zoroark' in pokemon_name:
                return 0
            battle.player[line[1]].team.add(pokemon_name)
        if line[0] == 'teampreview':
            break


    battle_situations = []
    item_traceback = []                                         #to do : add tracebacks
    ability_traceback = []
    for turn in turn_log[1:]:
        for line in turn:
            if line[0] == 'win':
                winner = line[1]
                if winner == battle.player['p1'].name:
                    win = 1
                elif winner == battle.player['p2'].name:
                    win = 0
                else:
                    win = 0.5
                    write_error('winner error',line,battle.num)
                break
            elif line[0] == 'tie':
                win = 0.5
                break
            else:
                line_handler(battle,line)



        #print(battle.player['p1'].show_all_pokemon())
        #print(battle.player['p1'].position,battle.player['p1'].backup)
        #print(battle.player['p2'].show_all_pokemon())
        #print(battle.player['p2'].position,battle.player['p2'].backup)
        #print(battle.turn,battle.player['p1'].alive_number(),battle.player['p2'].alive_number())
        battle_situations.append(get_battle_situation(battle))

        battle.end_turn()

    for situation in battle_situations:
        situation['win'] = win
        situation['total_turn'] = battle.turn
        situation['battle_id'] = battle.num
        situation['rank'] = battle.rank()
    #print(battle_situations)
    return(battle_situations)

''
directory = './log'
dfs = []
for file_name in os.listdir(directory):
    if file_name.endswith('txt'):
        file_path = os.path.join(directory, file_name)
        battle_situations = log_process(file_path)
        if battle_situations:
            dfs.append(pd.DataFrame(battle_situations))
df = pd.concat(dfs, sort=False)
df = df[col_order]
df.to_csv('output.csv', index=False)


'''

log_process('./log/gen9vgc2024regg-2113252505.txt')
'''