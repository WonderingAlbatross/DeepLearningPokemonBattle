import numpy as np
from typing import Optional
from typing import Dict

from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.effect import Effect
from poke_env.environment.field import Field
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.side_condition import STACKABLE_CONDITIONS, SideCondition
from poke_env.environment.weather import Weather

from pokemonset import PokemonSet

level = 100

antitypeberry = {
	"FIRE":"occaberry",
	"WATER":"passhoberry",
	"ELECTRIC":"wacanberry",
	"GRASS":"rindoberry",
	"ICE":"yacheberry",
	"FIGHTING":"chopleberry",
	"POISON":"kebiaberry",
	"GROUND":"shucaberry",
	"FLYING":"cobaberry",
	"PSYCHIC":"payapaberry",
	"BUG":"tangaberry",
	"ROCK":"chartiberry",
	"GHOST":"kasibberry",
	"DRAGON":"habanberry",
	"DARK":"colburberry",
	"STEEL":"babiriberry",
	"NORMAL":"chilanberry",
	"FAIRY":"roseliberry"
	}
giantberry = ("aguavberry","figyberry","iapapaberry","magoberry","wikiberry")



def modified_move_vector(
		move,
		mon:PokemonSet,
		oppo:PokemonSet,
		_weather,
		_field,
		_side,_oppo_side,
		_counts_ability = True, 
		_counts_item = True,
		_counts_oppo_ability = True, 
		_counts_oppo_item = True):

	v = np.zeros(100)
	vclear = np.zeros(100)
	vclear[0] = 1
	vclear[4] = 1

	types = (mon._mon._type_1,mon._mon._type_2)
	oppo_types = (oppo._mon._type_1,oppo._mon._type_2)

	#p1. modifies ability
	counts_ability = _counts_ability
	counts_oppo_ability = _counts_oppo_ability
	if "neutralizinggas" in (ability,oppo_ability):
		if ability not in ("comatose","asone"):
			counts_ability = False
		if oppo_ability not in ("comatose","asone"):
			counts_oppo_ability = False	
	if counts_ability is True:
		ability = mon._mon._ability		
	else:
		if counts_ability:							#Test this!
			ability = counts_ability
		else:
			ability = ""
	if counts_oppo_ability is True:
		oppo_ability = oppo._mon._ability
	else:
		if counts_oppo_ability:
			oppo_ability = counts_oppo_ability
		else:
			oppo_ability = ""
	if ability == "trace":
		ability = oppo_ability
	if oppo_ability == "trace":
		oppo_ability = ability

	#p2. modifies item
	counts_item = _counts_item
	counts_oppo_item = _counts_oppo_item

	if ability == "klutz" or Effect.EMBARGO in mon._mon._effects:
		counts_item = False
	if oppo_ability == "klutz" or Effect.EMBARGO in oppo._mon._effects:
		counts_oppo_item = False

	if Field.WONDER_ROOM in field: 
		counts_item = False
		counts_oppo_item = False

	if counts_item is True:
		item = mon._mon._item		
	else:
		if counts_item:
			item = counts_item
		else:
			item = ""
	if counts_oppo_item is True:
		oppo_item = oppo._mon._item
	else:
		if counts_oppo_item:
			oppo_item = counts_oppo_item
		else:
			oppo_item = ""



	#p3.modifies weathers.etc, move types, pokemontype
	weather = _weather
	oppo_weather = _weather
	field = _field
	oppo_field = _field
	movetype = move.type
	types = mon._mon.types
	oppo_types = oppo._mon.types
	effects = mon._mon._effects 
	oppo_effects = oppo._mon._effects 

	if item == "utilityumbrella":
		weather = {}
	if oppo_item == "utilityumbrella":
		oppo_weather = {}
	if "cloudnine" in (ability,oppo_ability):
		weather = {}
		oppo_weather = {}
	if "airlock" in (ability,oppo_ability):
		weather = {}
		oppo_weather = {}	

	if _is_grounded(mon,field) == False:
		for f in field:
			if f.is_terrain():
				field.remove(f)	
	if _is_grounded(oppo,field) == False:
		for f in oppo_field:
			if f.is_terrain():
				oppo_field.remove(f)								#test it



	if item == "protectivepads" or ability == "longreach":
		v[31] = 0




	#p4. modifies stats
	m_stats = np.zeros(5)
	m_stats = pokemon_vectorize(mon,weather,field,_counts_ability = counts_ability, _counts_item = counts_item)[17:22]
	o_stats = np.zeros(5)
	o_stats = pokemon_vectorize(oppo,oppo_weather,oppo_field,_counts_ability = oppo_counts_ability, _counts_item = oppo_counts_item)[17:22]

	speed_ratio = (m_stats[4]+0.1) / (o_stats[4]+0.1)

	if speed_ratio >1:
		speed_ratio = 1 / speed_ratio
	else:
		speed_ratio = - speed_ratio
	if Field.TRICK_ROOM in _field:
		speed_ratio = - speed_ratio

	#p5 modifies if this is a switch
	if move == "switch":
		v[0] = 7 + speed_ratio
		if ability == "intimidate":
			if oppo_ability not in ("scrappy","owntempo","innerfocus","oblivious",):
				v[13] = -1
				if oppo_ability == "rattled":
					v[17] = 2
		if ability == "shadowtag" and oppo_ability != "shadowtag":	
			v[42] = 2
		if ability == "magnetpull" and PokemonType.STELL in oppo_types:
			v[42] = 2
		if ability == "arenatrap" and _is_grounded(oppo,field):
			v[42] = 2
		if ability == "drought":
			v[83] = 1
		if ability == "drizzle":
			v[84] = 1
		if ability == "sandstream":
			v[85] = 1
		if ability == "snowwarning":
			v[86] = 1
		if ability == "electricsurge": 
			v[87] = 1
		if ability == "grassysurge": 
			v[88] = 1
		if ability == "mistysurge": 
			v[89] = 1
		if ability == "psychicsurge": 
			v[90] = 1

		#spikes
		if item != "heavydutyboots":
			if SideCondition.STEALTH_ROCK in side:
				if ability != "magicguard":
					v[26] -= PokemonType.ROCK.damage_multiplier(*types) / 8
			if _is_grounded(mon,field):
				if SideCondition.SPIKES in side:
					if ability != "magicguard":
						v[26] -= 1 / ( 10- 2 * side[SideCondition.SPIKES] )
				if SideCondition.SPIKES in side:
					if PokemonType.POISON in types:
						v[78] = 0.5
					else:
						if PokemonType.STEEL not in types:
							v[23] = side[SideCondition.TOXIC_SPIKES]
				if SideCondition.STICKY_WEB in side:
					if ability not in ("clearbody","whitesmoke","fullmetalbody"):
						if ability == "contrary":
							v[10] += 1
						else:
							if ability == "mirrorarmor":		# regard as by self move, not by target
								v[17] -= 1
							else:
								v[10] -= 1
								if ability == "competitive":
									v[8] += 2							
								if ability == "defiant":
									v[6] += 2		
								if ability == "simple":
									v[10] -= 1



	#p6. modiefies if has no effect and accurancy

	if "damp" in (ability,oppo_ability):
		if move._id in ("selfdestruct","explosion","mindblown","mistyexplosion"):
			return v
	if "soundproof" in oppo_ability:
		if move.entry.get("target",{}) != "self":
			return v
	if item == "assaultvest":
		if v[1] == 0 and v[2] == 0:
			return v

	if move._id == "rest":
		if ability in ("insomnia","vitalspirit","comatose"):
			return v
		if Field.ELECTRIC_TERRAIN in field or Field.MISTY_TERRAIN in field:
			return v

	if oppo_ability == "wonderguard":
		if v[1] or v[2] or v[53]:
			if movetype.damage_multiplier(*types) < 1.5:
				return v



	#if opponent can change weather, weather = ...
	#!! if already ingrain, ingrain is not useful, etc
	if move != "switch":
		v = move_vectorize(move)


	


	#p7. modifies priority

	v[0] += speed_ratio






	#p8. modiefies power and acc and 

	acc_rate = mon._mon._boosts["accuracy"] - oppo._mon._boosts["evasion"]
	if acc_rate > 0:
		acc_rate = ( acc_rate + 3 ) / 3
	else:
		acc_rate = 3 / ( acc_rate + 3 )

	v[4] *= acc_rate
	if ability == "compoundeyes":
		v[4] *= 1.3
	if ability == "hustle" and v[1]:
		v[4] *= 0.8

	v[4] = max(v[4],1)

	#0ko




		
	if PokemonType.FLYING in oppo_types and move._id == "thousandarrows":
		damage_multiplier = 1
	else:
		if _is_grounded(oppo,field) and movetype == PokemonType.GROUND and PokemonType.FLYING in oppo_types:
			oppo_types.remove(PokemonType.FLYING)
		damage_multiplier = movetype.damage_multiplier(*oppo_types)

	if move._id == "flyingpress":
		damage_multiplier *= PokemonType.FLYING.damage_multiplier(*oppo_types)

	if move._id == "knockoff":
		if item:
			if item != "lost" and oppo_ability != "stickyhold":
				damage_multiplier *= 1.5

	if mon._stats[0] / mon._stats[1] < 1/3:
		if movetype == PokemonType.GRASS and ability == "overgrow":
			damage_multiplier *= 1.5
		if movetype == PokemonType.FIRE and ability == "blaze":
			damage_multiplier *= 1.5		
		if movetype == PokemonType.WATER and ability == "torrent":
			damage_multiplier *= 1.5
		if movetype == PokemonType.BUG and ability == "swarm":
			damage_multiplier *= 1.5

	if movetype == PokemonType.WATER:
		if ability == "waterbubble":
			damage_multiplier *= 2
		if oppo_ability == "waterbubble":
			damage_multiplier *= 0.5

	if movetype in (PokemonType.FIRE,PokemonType.ICE):
		if oppo_ability == "thickfat":
			damage_multiplier *= 0.5

	#is stab
	if movetype in types:
		if ability == "adaptability":
			damage_multiplier *= 2
		else:
			damage_multiplier *= 1.5



	if v[1] or v[2] or v[53] or move._id == "thunderwave":

		if damage_multiplier == 0:
			v = v * vclear 

		if oppo_ability == "voltabsorb" and movetype == PokemonType.ELECTRIC:
			v = v * vclear 
			v[53] = -1/2
		if oppo_ability == "waterabsorb" and movetype == PokemonType.WATER:
			v = v * vclear 
			v[53] = -1/2
		if oppo_ability == "flashfire" and movetype == PokemonType.WATER:
			v = v * vclear 
			v[13] = 0.5
			v[15] = 0.5
		if oppo_ability == "lightningrod" and movetype == PokemonType.ELECTRIC:
			v = v * vclear 
			v[15] = 1




	#p9. modifies side effect
	if move._id == "yawn":
		if Effect.YAWN in oppo_effects:
			v[69] = 0
	#effects
	if Effect.YAWN in effects:
		v[97] = 1
	if Effect.YAWN in oppo_effects:
		v[24] = 1



	#contact
	if v[31] == 1:

		if oppo_ability in ("roughskin","ironbarbs"):
			v[26] += 1/8 * ( 1 + v[30] )
		if oppo_item ==  "rockyhelmet":
			v[26] += 1/6 * ( 1 + v[30] )

		if oppo_ability == "flamebody":
			v[93] += 1 - 0.7 ** ( 1 + v[30] )
		if oppo_ability == "static":
			v[95] += 1 - 0.7 ** ( 1 + v[30] )
		if oppo_abiliy == "effectspore":
			if item != "safetygoggles" and ability != "overcoat" and PokemonType.GRASS not in types:
				v[93] += 1 - 0.9 ** ( 1 + v[30] )
				v[95] += 1 - 0.9 ** ( 1 + v[30] )
				v[96] += 1 - 0.9 ** ( 1 + v[30] )

	if oppo_ability == "synchronize":
		v[93] += v[20]
		v[95] += v[22]
		v[96] += v[23]
	
#	if deal damage
	if v[1] or v[2] or v[53]:
		if ability == "stench" or item in ("kingsrock","razorfang"):
			v[55] += 0.1 * ( 1 + v[30] )
		if ability == "speedboost":
			v[10] += 1
		if ability == "serenegrace":
			v[13:25] *= 2 							#test this
			v[55:70] *= 2



#side-effect-inmune

	if oppo_ability in ("battlearmor","shellarmor"):
		v[5] = -6



	if oppo_ability == "shielddust":
		if v[1] or v[2]:
			v[13:25] *= 0
			v[55:70] *= 0


	if Effect.HEAL_BLOCK in mon_effects:
		if v[26] > 0:
			v[26] = 0
		if v[27] > 0:
			v[27] = 0
	if oppo_ability == "rockhead":
		if v[27] < 0:
			v[27] = 0
	if oppo_ability == "liquidooze":
		if v[27] > 0:
			v[27] *= -1
	if ability == "magicguard":
		if v[27] < 0:
			v[27] = 0

	if ability == "truant":
		v[39] = 0
	if oppo_ability == "suctioncups":
		v[39] = 0
	if PokemonType.GHOST in oppo_types:
		v[42] = 0
	if oppo_ability == "innerfocus":
		v[55] = 0
	if oppo_ability == "owntempo":
		v[56] = 0
	if oppo_ability == "oblivious" or Effect.TAUNT in oppo_effects:
		v[68] = 0
	if ability == "shedskin":
		v[80] += 1/3


	if oppo_ability == "hypercutter":
		if v[13] < 0:
			v[13] = 0
	if oppo_ability == "keeneye":
		if v[18] < 0:
			v[18] = 0
	if oppo_ability in ("clearbody","whitesmoke","fullmetalbody"):
		for i in range(0,7):
			if v[13+i] < 0:
				v[13+i] = 0

	if oppo_ability in ("waterveil","waterbubble"):
		v[20] = 0
	if ability in ("waterveil","waterbubble"):
		v[93] = 0
	if oppo_ability == "magmaarmor":
		v[21] = 0
	if ability == "magmaarmor":
		v[94] = 0
	if oppo_ability == "limber" or PokemonType.ELECTRIC in oppo_types:
		v[22] = 0
	if ability == "limber" or PokemonType.ELECTRIC in types:
		v[95] = 0
	if oppo_ability in ("immunity","pastelveil"):
		v[23] = 0
	if PokemonType.POISON in oppo_types or PokemonType.STEEL in oppo_types:
		if ability != "corrosion":
			v[23] = 0
	if ability in ("immunity","pastelveil"):
		v[96] = 0
	if PokemonType.POISON in types or PokemonType.STEEL in types:
		v[96] = 0
	if oppo_ability in ("insomnia","vitalspirit"):
		v[24] = 0
		v[69] = 0
	if ability in ("insomnia","vitalspirit"):
		v[97] = 0	
	if mon._mon_status:
		v[93:97] *= 0


	#weather,field
	if Field.ELECTRIC_TERRAIN in field:
		if movetype == PokemonType.ELECTRIC:
			v[1:3] *= 1.3
			v[97] = 0					
	if Field.ELECTRIC_TERRAIN in oppo_field:
		v[24] = 0
		v[69] = 0
		if move._id == "risingvoltage":
			v[1:3] *= 2

	if Field.MISTY_TERRAIN in field:
		v[93:97] *= 0
	if Field.MISTY_TERRAIN in oppo_field:		
		v[20:25] *= 0
		v[56] = 0
		v[69] = 0
		if movetype == PokemonType.DRAGON:
			v[1:3] *= 0.5

	if Effect.SAFEGUARD in oppo_effects or oppo_ability == "comatose":
		v[20:25] *= 0
		v[56] = 0
		v[69] = 0
	if Effect.SAFEGUARD in mon_effects or ability == "comatose":
		v[93:97] *= 0
	
	


	if move._id == "rest":
		v[97] = 1

	#p10 modifies one-time effect (berry,beserker,etc)
	if v[1] or v[2] or v[53]:
		if oppo_item == "redcard" and ability != "suctioncups":
			v[38] = 1
		if oppo_item == "ejectbutton":
			v[39] = 1
			v[38] = 0
	if item == "ejectpack":
		for i in range(0,7):
			if v[6+i]<0:
				v[38] = 1
	if oppo_item == "ejectpack":
		for i in range(0,7):
			if v[13+i]<0:
				v[39] = 1


	return v

def modified_switch_vectorize(
		mon:PokemonSet,
		oppo:PokemonSet,
		_weather,
		_field,
		_side,oppo_side,
		_counts_ability = True, 
		_counts_item = True,
		_counts_oppo_ability = True, 
		_counts_oppo_item = True):
	v = modified_move_vector(
		"switch",mon,oppo,_weather,_field,_side,_oppo_side,
		_counts_ability = _counts_ability, 
		_counts_item = _counts_item,
		_counts_oppo_ability = _counts_oppo_ability, 
		_counts_oppo_item = _counts_oppo_item)
	return v

def modified_get_ability_vectorize(						#**** Neutralizing Gas
		mon:PokemonSet,
		oppo:PokemonSet,
		_weather,_field,_side,_oppo_side,
		_gets_ability = True, 
		_oppo_gets_ability = True):
	v1 = modified_switch_vectorize(mon,oppo,_weather,_field,_side,_oppo_side,_counts_ability = _gets_ability, _counts_oppo_ability = True)
	v2 = modified_switch_vectorize(mon,oppo,_weather,_field,_side,_oppo_side,_counts_ability = False, _counts_oppo_ability = 1 - _oppo_gets_ability)
	return v1-v2


	


def pokemon_vectorize(mon:PokemonSet,weather,field, _counts_ability = True, _counts_item = True):
	v = np.zeros(30)
	counts_ability = _counts_ability
	counts_item = _counts_item
	if counts_ability is True:
		ability = mon._mon._ability		
	else:
		if counts_ability:
			ability = counts_ability
		else:
			ability = ""
	counts_item = _counts_ability

	if ability == "klutz" or Effect.EMBARGO in mon._mon._effects:
		counts_item = False
	if Field.WONDER_ROOM in field: 
		counts_item = False

	if counts_item is True:
		item = mon._mon._item		
	else:
		if counts_item:
			item = counts_item
		else:
			item = ""

	types = (mon._mon._type_1,mon._mon._type_2)
	dpt = 0 
	hpt = 0 								#heal 1/16 per turn
	v[0] = mon._stats[0] / mon._stats[1]
	v[1:6] = mon._stats[2:7]
	v[17:22] = mon._stats[2:7]
	if ability == "regenerator":
		v[7] = 2
	if ability == "naturalcure":
		v[7] = 1
	if mon._mon._status:
		if ability == "guts":
			v[17] *= 1.5 							#test this
		if ability == "marvelscale":
			v[18] *= 1.5 	
		_status = mon._mon._status.name
		v[6] = 1
		if _status == "BRN":
			v[10] = 1
			dpt += 1							
		if _status == "FRZ":
			v[9] = 4
		if _status == "PAR":			
			v[9] = 1/4
			v[11] = 1
		if _status == "PSN":
			if ability == "poisonheal":
				hpt += 2
			else:
				dpt = 2
		if _status == "SLP":
			v[9] = 3 - mon._mon._status_counter
		if _status == "TOX":
			if ability == "poisonheal":
				hpt += 2
			else:
				dpt += ( 1 + mon._mon._status_counter )

	if item in ("leftover","blacksludge"):
		hpt += 1	
	if item == "stickybarb":
		dpt += 2	
	if item == "choiceband" or ability == "gorillatactics":
		v[17] *= 1.5
		v[12] = 10
	if item == "choicespecs":
		v[19] *= 1.5
		v[12] = 10
	if item == "choicescarf":
		v[21] *= 1.5
		v[12] = 10
	if item == "assaultvest":
		v[20] *= 1.5
	if item == "eviolite":
		v[18] *= 1.5
		v[20] *= 1.5
	if item == "focussash" or ability == "sturdy":
		v[13] = 1
	if mon._mon._species in ("mimikyu","eiscue"): #test it
		v[14] = 1

	if ability != "overcoat" and item != "safetygoggles":
		if Weather.SANDSTORM in weather:
			if PokemonType.ROCK not in types:
				if PokemonType.STEEL not in types:
					if PokemonType.GROUND not in types:
						if ability not in ("sandforce","sandveil","sandrush"):
							dpt += 1
		if Weather.HAIL in weather:
			if PokemonType.ICE not in types:
				if ability not in ("icebody","snowcloak"):
					dpt += 1
	if Field.GRASSY_TERRAIN in field:
		if _is_grounded(mon,field):
			hpt += 1

	effects = mon._mon._effects 
	if mon._mon.active:

		if Effect.AQUA_RING in effects:
			hpt += 1
		if Effect.BIND in effects:
			dpt += 2
			v[15] = 5 - effects[Effect.BIND]
		if Effect.CLAMP in effects:
			dpt += 2
			v[15] = 5 - effects[Effect.CLAMP]
		if Effect.CONFUSION in effects:
			v[9] += 1/3
			dpt += 1
		if Effect.CURSE in effects:
			v[8] -= 4 
	#	if Effect.DESTINY_BOND in effects: -200%hp side effect
		if Effect.ENCORE in effects:
			if v[12] == 0:
				v[12] = 3 - effects[Effect.ENCORE]
		if Effect.FIRE_SPIN in effects:
			dpt += 2
			v[15] = 5 - effects[Effect.FIRE_SPIN]		
		if Effect.INFESTATION in effects:
			dpt += 2
			v[15] = 5 - effects[Effect.INFESTATION]
		if Effect.INGRAIN in effects:
			hpt += 1
		if Effect.LEECH_SEED in effects:
			dpt += 2
		if Effect.MAGMA_STORM in effects:
			dpt += 2
			v[15] = 5 - effects[Effect.MAGMA_STORM]
		if Effect.NO_RETREAT in effects:
			v[15] = 10
		if Effect.OCTOLOCK in effects:
			v[15] = 10	
		if Effect.PERISH0 in effects:
			v[16] = 1	
		if Effect.PERISH1 in effects:
			v[16] = 2
		if Effect.PERISH2 in effects:
			v[16] = 3
		if Effect.PERISH3 in effects:
			v[16] = 4
		if Effect.SAND_TOMB in effects:
			dpt += 2
			v[15] = 5 - effects[Effect.SAND_TOMB]
		if Effect.SNAP_TRAP in effects:
			dpt += 2
			v[15] = 5 - effects[Effect.SNAP_TRAP]
		if Effect.SUBSTITUTE in effects:
			v[14] = 1
		if Effect.THUNDER_CAGE in effects:
			dpt += 2
			v[15] = 5 - effects[Effect.THUNDER_CAGE]
		if Effect.TRAPPED in effects:
			v[15] = 10	
		if Effect.WHIRLPOOL in effects:
			dpt += 2
			v[15] = 5 - effects[Effect.WHIRLPOOL]
		if Effect.WRAP in effects:
			dpt += 2
			v[15] = 5 - effects[Effect.WRAP]
		
		boosts = list(mon._mon._boosts.values())
		v[22] = boosts.pop(0)		#acc
		v[23] = boosts.pop(2)		#eva
		for i in range(0,5):
			v[17+i] = v[1+i]*boosts_to_multi(boosts[i])

	if Weather.RAINDANCE in weather:
		if ability == "swiftswim":
			v[21] *= 2
		if ability == "raindish":
			hpt += 1
	if Weather.SUNNYDAY in weather:
		if ability == "chlorophyll":
			v[21] *= 2
	if ability in ("hugepower","purepower"):
		v[17] *= 2
	if ability == "hustle":
		v[17] *= 1.5
	if item == "laggingtail":
		if Field.TRICK_ROOM in field:
			v[21] = 2000
		else:
			v[21] = 1

	if Effect.HEAL_BLOCK not in effects:
		v[8] += hpt / 16
	if ability != "magicguard":
		v[8] -= dpt / 16




	return(v[:24])





	#locked move/encore/choise: only counts for lastmove when calc advantage credit
	#difficult to deal with: Libero,Protean: use move when calc advantage credit
	"""
	Speed Boost,:show in advantage credit (spd+1)
	Intimidate(to Competitive),Download,Intrepid Sword,Dauntless Shield :show in advantage credit
	Swift Swim, Chlorophyll,Sand Veil,Rain Dish,Snow Cloak,Dry Skin,Hydration,Solar Power,Leaf Guard,Storm Drain,Ice Body,Sand Rush,Sand Force,Slush Rush
	Trace,
	Cloud Nine,Air Lock,utility umbrella,Sand Stream,Drizzle,Drought,Snow Warning 
	Truant,Defeatist
	Unburden,
	ingrain,aquaring
	Mold Breaker,Turboblaze,Teravolt,Neutralizing Gas
	Unaware,
	Contrary,
	Unnerve,
	Multiscale = hp%,Shadow Shield,Gale Wings
	Moody,
	Overcoat,
	Infiltrator, 
	Moxie,Soul-Heart,Beast Boost,Chilling Neigh,Grim Neigh :show in advantage credit (spd+1)
	Magic Bounce,
	Magic Guard,
	Berserk,
	Disguise,Ice Face: hit and recover (like substitute)
	Electric Surge,Psychic Surge,Misty Surge,Grassy Surge 
	Unseen Fist,
	Gorilla Tactics, Choice Item
	

	heavy-duty boots
	Shed Shell
		"""
	#specific types



	#knock off, itemswitch,tailwind,weather/field(contains trickroom) change, etc:see how advantage credit change after changing
#	if item == "safetygoggles": if ability == "overcoat":
#	if item == "assaultvest": only relates to trick
#	if item == "rockyhelmet": if ability in ("roughskin","ironbarbs"): hit side effect 	
#	if item == "lifeorb" and ability != "magicguard": hit side effect	
'''
	#let switch act as a move!
	v[20] = PokemonType.ROCK.damage_multiplier(*mon._mon.types)
	if _is_grounded(mon,None):
		v[18] = 1
		v[19] = 1
		v[21] = 1
		if "STEEL" in types:
			v[19] = 0	
		if "POISON" in types:
			v[19] = -1
		if ability in ("competitive","defiant","contrary"):
			v[21] = -1
	if item == "heavydutyboots" or ability == "magicguard":
		v[18] = 0
		v[19] = 0
		v[20] = 0
		v[21] = 0
'''



#	if ability == "regenerator": natural cure: heal after switch

















def move_vectorize(move:Move):
	v = np.zeros(100)

	v[0] = move.priority
	
	if move.entry["category"] == "Physical":
		v[1] = move.base_power
	if move.entry["category"] == "Special":
		v[2] = move.base_power	
	if "ohko" in move.entry:
		v[1] = 10000
	if move._id == "fling":
		v[1] = 130
	if move._id == "beatup":
		v[1] = 13
		v[3] = 1
		v[30] = 5
	if move._id in ("heavyslam","heatcrash","gyroball","lowkick","reversal","flail"):
		v[1] = 90
	if move._id in ("grassknot","electroball"):
		v[2] = 90
	if move._id == "facade":
		v[1] = 140

	v[3] = np.amax(v[1:2]) * 0.04 #std error
	if isinstance(move.entry.get("multihit",{}),list):
		v[3] = np.amax(v[1:2]) * 1.07
		v[1:3] *= 19/6
		v[30] = 2
	else:
		if move.entry.get("multihit",{}) == 2:
			v[3] = np.amax(v[1:2]) * 0.06
			v[1:3] *= 2
			v[30] = 1
		else:
			if move.entry.get("multihit",{}) == 3:
				if move._id == "surgingstrikes":
					v[3] = np.amax(v[1:2]) * 0.07
					v[1:3] *= 3
					v[30] = 2
				else:
					v[3] = np.amax(v[1:2]) * 1.67
					v[1:3] *= 5.23
					v[30] = 2

	v[4] = move.accuracy
	if move.entry["accuracy"] is True:
		v[4] = 6
	
	v[5] = move.crit_ratio

	
	#selfboosts												#Spectral Thief
	_chance = 1
	_boosts = {}
	if move.entry.get("selfBoost",{}):
		_boosts = move.entry.get("selfBoost",{}).get("boosts",{})	
	if move.entry.get("boosts",{}) and move.entry.get("target",{}) == "self":
		_boosts = move.entry.get("boosts",{})
	if move.entry.get("self",{}):
		if move.entry.get("self",{}).get("boosts",{}):
			_boosts = move.entry.get("self",{}).get("boosts",{})
	if move.entry.get("secondary",{}):
		if move.entry.get("secondary",{}).get("self",{}):
			if move.entry.get("secondary",{}).get("self",{}).get("boosts",{}):
				_boosts = move.entry.get("secondary",{}).get("self",{}).get("boosts",{})
				_chance = move.entry.get("secondary",{}).get("chance",100)/100			

	if _boosts:	
		v[6] = _boosts.get("atk",0)
		v[7] = _boosts.get("def",0)
		v[8] = _boosts.get("spa",0)
		v[9] = _boosts.get("spd",0)
		v[10] = _boosts.get("spe",0)
		v[11] = _boosts.get("accuracy",0)
		v[12] = _boosts.get("evasion",0)
		v[6:13] *= _chance
	#acupressure is the only move targets adjacentAllyOrSelf
	if move._id == "acupressure":
		v[6:13] = np.ones(7)*2/7
	if move._id == "bellydrum":
		v[6] = 12	
	if move._id == "skullbash":
		v[7] = 1	
	if move._id == "meteorbeam":
		v[8] = 1	

	#enemyboosts
	_chance = 1
	_boosts = {}
	if move.entry.get("boosts",{}):
		if move.entry.get("target",{}) in ("normal","allAdjacent","allAdjacentFoes","any"):
			_boosts = move.entry.get("boosts",{})
	if move.entry.get("secondary",{}):
		_boosts = move.entry.get("secondary",{}).get("boosts",{})
		_chance = move.entry.get("secondary",{}).get("chance",100)/100

	if _boosts:	
		v[13] = _boosts.get("atk",0)
		v[14] = _boosts.get("def",0)
		v[15] = _boosts.get("spa",0)
		v[16] = _boosts.get("spd",0)
		v[17] = _boosts.get("spe",0)
		v[18] = _boosts.get("accuracy",0)
		v[19] = _boosts.get("evasion",0)
		v[13:20] *= _chance

	if move._id == "defog":
		v[19] = -1
	if move._id == "partingshot":
		v[13] = -1
		v[15] = -1
	if move._id == "strengthsap":
		v[13] = -1
	if move._id == "octolock":
		v[14] = -1.5
		v[16] = -1.5
	if move._id == "kingsshield":
		v[13] = -0.3
	if move._id == "obstruct":
		v[14] = -0.6

	#status condition
	_chance = 1
	_status = move.entry.get("status","")
	if move.entry.get("secondary",{}):
		_status = move.entry.get("secondary",{}).get("status","")
		_chance = move.entry.get("secondary",{}).get("chance",100)/100
	if move.entry.get("secondaries",{}):
		for _secondary in move.entry.get("secondaries",{}):
			if _secondary.get("status",""):
				_status = _secondary.get("status","")
				_chance = _secondary.get("chance",100)/100
	
	
	if _status == "brn":
		v[20] = _chance
	if _status == "frz":
		v[21] = _chance
	if _status == "par":
		v[22] = _chance
	if _status == "psn":
		v[23] = _chance
	if _status == "slp":
		v[24] = _chance
	if _status == "tox":
		v[23] = 2 * _chance

	if move._id == "triattack":
		v[20] = 1/15
		v[21] = 1/15
		v[22] = 1/15
	if move._id == "banefulbunker":
		v[23] = 0.3

	if move._id in ("boltbeak","fishiousrend"):
		v[25] = 1

	# heal, absorb and recoil            ! pollenpuff / healpulse / floralhealing
	#self%
	if "heal" in move.entry and move.entry.get("target",{}) in ("self","allies"):
		v[26] = move.entry["heal"][0]/move.entry["heal"][1]
	if move._id in ("synthesis","morningsun","moonlight","strengthsap","shoreup"):
		v[26] = 1/2
	if move._id == "rest":
		v[26] = 1
	if "mindBlownRecoil" in move.entry or move._id in ("bellydrum","curse"):
		v[26] = -1/2
	if move._id == "substitute":
		v[26] = -1/4
	if move._id == "clangoroussoul":
		v[26] = -1/3
	if "selfdestruct" in move.entry:
		v[26] = -1
	
	#damage%
	if "drain" in move.entry:
		v[27] = move.entry["drain"][0]/move.entry["drain"][1]
	if move._id == "painsplit": 
		v[27] = 1
	if "recoil" in move.entry:
		v[27] = -move.entry["recoil"][0]/move.entry["recoil"][1]
	# highjumpkick
	if "hasCrashDamage" in move.entry:
		v[28] = -1/2
	# strengthsap
	if move._id in ("strengthsap","foulplay"):
		v[29] = 1

	#flags 30: "multihit"
	if "flags" in move.entry:
		if "contact" in move.entry["flags"]:
			v[31] = 1
		if "sound" in move.entry["flags"]:
			v[32] = 1
		if "powder" in move.entry["flags"]:
			v[33] = 1		
		if "defrost" in move.entry["flags"]:
			v[34] = 1
		if "charge" in move.entry["flags"]:
			v[35] = 1
			if "condition" in move.entry:
				v[36] = 1
		if "recharge" in move.entry["flags"]:
			v[37] = 1
	if "selfSwitch" in move.entry:
		v[38] = 1
	if "forceSwitch" in move.entry:
		v[39] = 1
	if move._id in ("fakeout","firstimpression","matblock"):
		v[40] = 1
	if move._id in ("ingrain","noretreat","jawlock"):
		v[41] = 1
	if move._id in ("meanlook","block","spiderweb","jawlock","octolock","thousandwaves","spiritshackle","anchorshot"):
		v[42] = 2	
	if move._id in ("ingrain","aquaring"):
		v[43] = 1
	if move._id in ("protect","detect","endure","spikyshield","kingsshield","banefulbunker","obstruct"):
		v[44] = 1
	if move._id == "endure":
		v[45] = 1
	if move._id in ("protect","detect","spikyshield","banefulbunker","craftyshield"):
		v[46] = 1
	if "breaksProtect" in move.entry:
		v[47] = 1
	if move._id == "painsplit": 
		v[48] = 1
	if move._id == "endeavor": 
		v[48] = 2
	if "ignoreDefensive" in move.entry:
		v[49] = 1
	if "isFutureMove" in move.entry:
		v[50] = 1

	if move._id == "counter":
		v[51] = 2
	if move._id == "mirrorcoat":
		v[52] = 2
	if move._id == "metalburst":
		v[51] = 1.5
		v[52] = 1.5
	if "damage" in move.entry:
		if move.entry["damage"] == "level":
			v[53] = level
		else:
			v[53] = move.entry["damage"]
	if move._id == "finalgambit":
		v[53] = 2*level
	if move._id in ("naturesmadness","superfang"):
		v[53] = 1.2*level

# this slot53 for passive damage side effects	slot54 empty







	#volatile status
	_chance = 1
	_volatilestatus = move.entry.get("volatileStatus","")
	if move.entry.get("secondary",{}):
		_volatilestatus = move.entry.get("secondary",{}).get("volatileStatus","")
		_chance = move.entry.get("secondary",{}).get("chance",100)/100
	if move.entry.get("secondaries",{}):
		for _secondary in move.entry.get("secondaries",{}):
			if _secondary.get("volatileStatus",""):
				_volatilestatus = _secondary.get("volatileStatus","")
				_chance = _secondary.get("chance",100)/100

	if _volatilestatus == "flinch":
		v[55] = _chance
	if _volatilestatus == "partiallytrapped":			
		v[42] = 1
		v[53] = 0.3*level
	if _volatilestatus == "confusion":
		v[56] = _chance
	if _volatilestatus == "curse":
		v[57] = _chance
	if _volatilestatus == "destinybond":
		v[58] = _chance
	if _volatilestatus in ("disable","torment","imprison"):
		v[59] = _chance
	if _volatilestatus == "encore":
		v[60] = _chance
	if _volatilestatus == "focusenergy":
		v[61] = _chance
	if _volatilestatus == "leechseed":
		v[62] = _chance
	if _volatilestatus == "magnetrise":
		v[63] = _chance
	if _volatilestatus == "lockedmove":
		v[64] = _chance
	if _volatilestatus == "roost":
		v[65] = _chance
	if _volatilestatus == "smackdown":
		v[66] = _chance
	if _volatilestatus == "substitute":
		v[67] = _chance
	if _volatilestatus == "taunt":
		v[68] = _chance
	if _volatilestatus == "yawn":
		v[69] = _chance

	#trickroom, tailwind, wall and spikes. ~no one change weather/field by move, so as changing ability, one tag for each is enough
	if move._id == "auroraveil":
		v[70] = 1
		v[71] = 1
	if move._id == "reflect":
		v[70] = 1
	if move._id == "lightscreen":
		v[71] = 1
	if move._id == "spikes":
		v[72] = 1
	if move._id == "stealthrock":
		v[73] = 1
	if move._id == "stickyweb":
		v[74] = 1
	if move._id == "toxicspikes":
		v[75] = 1
	if move._id == "tailwind":
		v[76] = 1
	if move._id == "trickroom":
		v[77] = 1
	if move._id == "gravity":
		v[66] = 1


	if move._id == "rapidspin":
		v[78] = 1
	if move._id == "defog":
		v[78] = 2
		v[79] = 2

	if move._id in ("healbell","aromatherapy","junglehealing"):
		v[80] = 2
	if move._id in ("refresh","rest"):
		v[80] = 1
	if move.id == "psychoshift":
		v[80] = 0.5

	if move._id in ("knockoff","trick","switcheroo"):
		v[81] = 1
	if move._id in ("gastroacid","coreenforcer","worryseed","simplebeam","entrainment","skillswap"):
		v[82] = 1
	#also mummy

	if move._id == "sunnyday":
		v[83] = 1
	if move._id == "raindance":
		v[84] = 1
	if move._id == "sandstorm":
		v[85] = 1
	if move._id == "hail":
		v[86] = 1
	if move._id == "electricterrain": 
		v[87] = 1
	if move._id == "grassyterrain": 
		v[88] = 1
	if move._id == "mistyterrain": 
		v[89] = 1
	if move._id == "psychicterrain": 
		v[90] = 1


	if move._id == "bodypress":
		v[91] = 1
	if move._id in ("psychick","psystrike","secretsword"):
		v[92] = 1
	if move._id in ("shellsidearm","photongeyser"):
		v[92] = 0.5


#93"brn":#94"frz":#95"par":#96"psn":#97"slp":

	if move._id == "rest":
		v[97] = 1
	
	
	return v
'''
	if move.entry.get("type","") == "Fire" and move.entry.get("category",{}) in ("Physical","Special"):
		v[83] = 1
		v[84] = -1
	if move._id == "sunnyday":
		v[83] = -2
	if move.entry.get("type","") == "Water" and move.entry.get("category",{}) in ("Physical","Special"):
		v[83] = -1
		v[84] = 1
	if move._id == "raindance":
		v[84] = -2
	if move._id == "sandstorm":
		v[85] = -2
	if move._id == "hail":
		v[86] = -2
	if move._id in ("solarblade","solarbeam"):
		v[83] = 2
		v[84] = -1
		v[85] = -1
		v[86] = -1
	if move._id in ("thunder","hurricane"):
		v[83] = -0.5
		v[84] = 0.5
	if move._id == "blizzard":
		v[86] = 0.5
	if move._id == "weatherball":
		v[83:87] = np.ones(4)*2

	if move.entry.get("type","") == "Electric" and move.entry.get("category",{}) in ("Physical","Special"):
		v[87] = 1
		if move._id == "risingvoltage": 
			v[87] = 2
		if move._id == "electricterrain": 
			v[87] = -2			
	if move.entry.get("type","") == "Grass" and move.entry.get("category",{}) in ("Physical","Special"):
		v[88] = 1
	if move._id == "grassyglide": 
		v[88] = 3
	if move._id == "grassyterrain": 
		v[88] = -2		
	if move._id in ("bulldoze","earthquake"): 
		v[88] = -1		
	if move.entry.get("type","") == "Dragon" and move.entry.get("category",{}) in ("Physical","Special"):
		v[89] = -1
	if move._id == "mistyexplosion":
		v[89] = 1
	if move._id == "mistyterrain": 
		v[89] = -2
	if move.entry.get("type","") == "Psychic" and move.entry.get("category",{}) in ("Physical","Special"):
		v[90] = 1
	if move._id == "expandingforce": 
		v[90] = 2
	if move._id == "psychicterrain": 
		v[90] = -2
	if v[0] > 0 and move.entry.get("target",{}) in ("normal","allAdjacent","allAdjacentFoes","any"):
		v[90] = -1
	if move._id == "terrainpulse":
		v[87:91] = np.ones(4)*2
	if move._id == "steelroller":
		v[87:91] = np.ones(4)*50
'''


def weather_field_vectorize(weather,field,turn):
	v = np.zeros(10)
	if weather:
		if Weather.SUNNYDAY in weather:
			v[0] = 8 - turn + weather[Weather.SUNNYDAY]
		if Weather.RAINDANCE in weather:
			v[1] = 8 - turn + weather[Weather.RAINDANCE]
		if Weather.SANDSTORM in weather:
			v[2] = 8 - turn + weather[Weather.SANDSTORM]
		if Weather.HAIL in weather:
			v[3] = 8 - turn + weather[Weather.HAIL]

	if field:
		if Field.ELECTRIC_TERRAIN in field:
			v[4] = 8 - turn + field[Field.ELECTRIC_TERRAIN]
		if Field.GRASSY_TERRAIN in field:
			v[5] = 8 - turn + field[Field.GRASSY_TERRAIN]
		if Field.MISTY_TERRAIN in field:
			v[6] = 8 - turn + field[Field.MISTY_TERRAIN]
		if Field.PSYCHIC_TERRAIN in field:
			v[7] = 8 - turn + field[Field.PSYCHIC_TERRAIN]
		if Field.GRAVITY in field:
			v[8] = 5 - turn + field[Field.GRAVITY]
		if Field.TRICK_ROOM in field:
			v[9] = 5 - turn + field[Field.TRICK_ROOM]
	return v

def side_condition_vectorize(side,turn):
	v = np.zeros(10)
	if side:
		if SideCondition.AURORA_VEIL in side:
			v[0] = 8 - turn + side[SideCondition.AURORA_VEIL]
			v[1] = 8 - turn + side[SideCondition.AURORA_VEIL]
		if SideCondition.REFLECT in side:
			v[0] = 8 - turn + side[SideCondition.REFLECT]
		if SideCondition.LIGHT_SCREEN in side:
			v[1] = 8 - turn + side[SideCondition.LIGHT_SCREEN]
		if SideCondition.SPIKES in side:
			v[2] = side[SideCondition.SPIKES]
		if SideCondition.STEALTH_ROCK in side:
			v[3] = 1	
		if SideCondition.STICKY_WEB in side:
			v[4] = 1	
		if SideCondition.TOXIC_SPIKES in side:
			v[5] = side[SideCondition.TOXIC_SPIKES]
		if SideCondition.TAILWIND in side:
			v[6] = 4 - turn + side[SideCondition.TAILWIND]
	return v[:7]


def _is_grounded(mon:PokemonSet,field:Optional[Dict]):
	if field:
		if Field.GRAVITY in field:
			return True
	if Effect.INGRAIN in mon._mon._effects:
		return True
	if Effect.SMACK_DOWN in mon._mon._effects:
		return True
	if mon._mon._item == "ironball":
		return True
	if mon._mon._type_1.name == "FLYING":
		return False
	if mon._mon._type_2.name == "FLYING":
		return False
	if mon._mon._ability == "levitate":
		return False
	if mon._mon._item == "airballoon":
		return False
	if Effect.MAGNET_RISE in mon._mon._effects:
		return False
	if Effect.TELEKINESIS in mon._mon._effects:
		return False
	return True

def boosts_to_multi(n):
	if n > 0:
		k = 1 + n / 2
	else:
		k = 1 / (1 - n / 2)
	return k
