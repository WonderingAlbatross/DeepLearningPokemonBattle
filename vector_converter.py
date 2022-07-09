import numpy as np
import copy
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
	"occaberry":PokemonType.FIRE,
	"passhoberry":PokemonType.WATER,
	"wacanberry":PokemonType.ELECTRIC,
	"rindoberry":PokemonType.GRASS,
	"yacheberry":PokemonType.ICE,
	"chopleberry":PokemonType.FIGHTING,
	"kebiaberry":PokemonType.POISON,
	"shucaberry":PokemonType.GROUND,
	"cobaberry":PokemonType.FLYING,
	"payapaberry":PokemonType.PSYCHIC,
	"tangaberry":PokemonType.BUG,
	"chartiberry":PokemonType.ROCK,
	"kasibberry":PokemonType.GHOST,
	"habanberry":PokemonType.DRAGON,
	"colburberry":PokemonType.DARK,
	"babiriberry":PokemonType.STEEL,
	"chilanberry":PokemonType.NORMAL,
	"roseliberry":PokemonType.FAIRY
	}
typeboostitem = {
	"charcoal":PokemonType.FIRE,
	"mysticwater":PokemonType.WATER,
	"magnet":PokemonType.ELECTRIC,
	"miracleseed":PokemonType.GRASS,
	"nevermeltice":PokemonType.ICE,
	"blackbelt":PokemonType.FIGHTING,
	"poisonbarb":PokemonType.POISON,
	"softsand":PokemonType.GROUND,
	"sharpbeak":PokemonType.FLYING,
	"twistedspoon":PokemonType.PSYCHIC,
	"silverpowder":PokemonType.BUG,
	"hardstone":PokemonType.ROCK,
	"spelltag":PokemonType.GHOST,
	"dragonfang":PokemonType.DRAGON,
	"blackglasses":PokemonType.DARK,
	"metalcoat":PokemonType.STEEL,
	"silkscarf":PokemonType.NORMAL,
	"waveincense":PokemonType.WATER,
	"seaincense":PokemonType.WATER,
	"oddincense":PokemonType.PSYCHIC,
	"roseincense":PokemonType.GRASS,
	"rockincense":PokemonType.ROCK,
	"flameplate":PokemonType.FIRE,
	"splashslate":PokemonType.WATER,	
	"zapplate":PokemonType.ELECTRIC,
	"meadowplate":PokemonType.GRASS,
	"icicleplate":PokemonType.ICE,
	"fistplate":PokemonType.FIGHTING,
	"toxicplate":PokemonType.POISON,
	"earthplate":PokemonType.GROUND,
	"skyplate":PokemonType.FLYING,
	"mindplate":PokemonType.PSYCHIC,
	"insectplate":PokemonType.BUG,
	"stoneplate":PokemonType.ROCK,
	"spookyplate":PokemonType.GHOST,
	"dracoplate":PokemonType.DRAGON,
	"dreadplate":PokemonType.DARK,
	"ironplate":PokemonType.STEEL,
	"pixieplate":PokemonType.FAIRY
}
giantberry = ("aguavberry","figyberry","iapapaberry","magoberry","wikiberry")
brokenability = ("battlearmor","clearbody","damp","flashfire","hypercutter","innerfocus","keeneye",
	"levitate","marvelscale","sandveil","shielddust","soundproof","stickyhold","sturdy","suctioncups",
	"thickfat","voltabsorb","waterabsorb","whitesmoke","wonderguard","lightningrod","dryskin","filter",
	"heatproof","leafguard","motordrive","simple","snowcloak","solidrock","tangledfeet","unaware",
	"stormdrain","magicguard","bigpecks","contrary","friendguard","heavymetal","lightmetal","magicbounce",
	"multiscale","sapsipper","telepathy","wonderskin","bulletproof","furcoat","overcoat","dazzling",
	"disguise","queenlymajesty","fluffy","mirrorarmor","punkrock","icescales","iceface",
	"flowergift","aromaveil","sweetveil","flowerveil")
# veils work differently in double!
crushmove = ("stomp","bodyslam","dragonrush","heatcrash","heavyslam","steamroller","flyingpress","maliciousmoonsault")

class Switch:
	def __init__(self):
		self._id = "switch"
		self.priority = 7
		self.type = None
		self.entry = {"flags":{},"accuracy": 100,"basePower": 0,"category":None,"pp": 999,"priority": 7,"target": "switch"}




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
		_counts_oppo_item = True,
		_crit = False):

	v = np.zeros(100)
	vclear = np.zeros(100)
	vclear[0] = 1
	vclear[4] = 1


	#p1. modifies ability


	if _counts_ability is True and mon._mon._ability:
		ability = mon._mon._ability		
	else:
		if isinstance(_counts_ability,str):							
			ability = _counts_ability
		else:
			ability = ""
	if _counts_oppo_ability is True and oppo._mon._ability:
		oppo_ability = oppo._mon._ability
	else:
		if isinstance(_counts_oppo_ability,str):
			oppo_ability = _counts_oppo_ability
		else:
			oppo_ability = ""
	if "neutralizinggas" in (ability,oppo_ability):
		if ability not in ("comatose","asoneglastrier","asonespectrier"):
			ability = ""
		if oppo_ability not in ("comatose","asoneglastrier","asonespectrier"):
			oppo_ability = ""
	if ability == "trace" and oppo_ability not in ("flowergift","comatose","asoneglastrier","asonespectrier"):
		ability = oppo_ability
	if oppo_ability == "trace":
		oppo_ability = ability
	if ability in ("moldbreaker","turboblaze","teravolt") or move._id in ("sunsteelstrike","moongeistbeam","photongeyser"):
		if oppo_ability in brokenability:
			oppo_ability = ""

	#p2. modifies item
	if _counts_item is True and mon._mon._item:
		item = mon._mon._item		
	else:
		if isinstance(_counts_item,str): 
			item = _counts_item
		else:
			item = ""
	if _counts_oppo_item is True and oppo._mon._item:
		oppo_item = oppo._mon._item
	else:
		if isinstance(_counts_oppo_item,str): 
			oppo_item = _counts_oppo_item
		else:
			oppo_item = ""


	if ability == "klutz" or Effect.EMBARGO in mon._mon._effects:
		item = ""
	if oppo_ability == "klutz" or Effect.EMBARGO in oppo._mon._effects:
		oppo_item = ""
	if ability in ("unnerve","asoneglastrier","asonespectrier") and oppo_item.endswith("berry"):
		oppo_item = ""
	if oppo_ability in ("unnerve","asoneglastrier","asonespectrier") and item.endswith("berry"):
		item = ""


	if Field.WONDER_ROOM in _field: 
		item = ""
		oppo_item = ""
		





	#p3.modifies weathers.etc, move types, pokemontype
	weather = copy.deepcopy(_weather)
	oppo_weather = copy.deepcopy(_weather)
	field = copy.deepcopy(_field)
	oppo_field = copy.deepcopy(_field)
	side = copy.deepcopy(_side)
	oppo_side = copy.deepcopy(_oppo_side)
	movetype = copy.deepcopy(move.type)
	types = []
	if mon._mon.type_1:
		types = types + [mon._mon.type_1]
	if mon._mon.type_2:
		types = types + [mon._mon.type_2]
	oppo_types = []
	if oppo._mon.type_1:
		oppo_types = oppo_types + [oppo._mon.type_1]
	if oppo._mon.type_2:
		oppo_types = oppo_types + [oppo._mon.type_2]
	effects = copy.deepcopy(mon._mon._effects)
	oppo_effects = copy.deepcopy(oppo._mon._effects)
	weight = mon._mon._weightkg
	oppo_weight = oppo._mon._weightkg




	pdmg = 0
	heal = 0
	selfattact = 0

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

	if _is_grounded(mon,_field) == False:
		for f in _field:
			if f.name.endswith("_TERRAIN"):
				field.pop(f)
	if _is_grounded(oppo,_field) == False:
		for f in _field:
			if f.name.endswith("_TERRAIN"):
				oppo_field.pop(f)								

	if ability == "infiltrator":
		if SideCondition.REFLECT in oppo_side:
			oppo_side.pop(SideCondition.REFLECT)
		if SideCondition.LIGHT_SCREEN in oppo_side:
			oppo_side.pop(SideCondition.LIGHT_SCREEN)
		if SideCondition.AURORA_VEIL in oppo_side:
			oppo_side.pop(SideCondition.AURORA_VEIL)
		if SideCondition.MIST in oppo_side:
			oppo_side.pop(SideCondition.MIST)
		if SideCondition.SAFEGUARD in oppo_side:
			oppo_side.pop(SideCondition.SAFEGUARD)				



	if ability == "heavymetal":
		weight *= 2
	if ability == "lightmetal":
		weight *= 0.5
	if oppo_ability == "heavymetal":
		oppo_weight *= 2
	if oppo_ability == "lightmetal":
		oppo_weight *= 0.5

	if Effect.AUTOTOMIZE in effects:
		weight = max( 0.1 , weight - 100 )
	if Effect.AUTOTOMIZE in oppo_effects:
		oppo_weight = max( 0.1 , weight - 100 )




	#p4. modifies stats
	v_mon = np.zeros(25)
	v_mon = pokemon_vectorize(mon,weather,field,ability,item)
	v_oppo = np.zeros(25)
	v_oppo = pokemon_vectorize(oppo,oppo_weather,oppo_field,oppo_ability,oppo_item)
	m_stats = np.zeros(7)
	m_stats[0:5] = v_mon[17:22]
	m_stats[5] = v_mon[0]
	m_stats[6] = mon._stats[1]
	o_stats = np.zeros(7)
	o_stats[0:5] = v_oppo[17:22]
	o_stats[5] = v_oppo[0]
	o_stats[6] = oppo._stats[1]

	boosts = list(mon._mon._boosts.values())
	acc = boosts.pop(0)
	eva = boosts.pop(2)
	boosts.append(acc)
	boosts.append(eva)
	oppo_boosts = list(oppo._mon._boosts.values())
	o_acc = oppo_boosts.pop(0)
	o_eva = oppo_boosts.pop(2)
	oppo_boosts.append(o_acc)
	oppo_boosts.append(o_eva)
	if _crit:
		for i in (0,2):
			if boosts[i] < 0:
				m_stats[i] /= boosts_to_multi(boosts[i])
	if _crit or move._id in ("psychick","psystrike","secretsword"):
		for i in (1,3):
			if oppo_boosts[i] > 0:
				o_stats[i] /= boosts_to_multi(oppo_boosts[i])
	if ability == "unaware":
		for i in (1,3):
			o_stats[i] /= boosts_to_multi(oppo_boosts[i])
	if oppo_ability == "unaware":
		for i in (0,2):
			m_stats[i] /= boosts_to_multi(boosts[i])

	if move._id == "spectralthief":
		stealboosts = [0,0,0,0,0]
		for i in range(0,5):
			if oppo_boosts[i] > 0:
				stealboosts[i] = oppo_boosts[i]
				oppo_boosts[i] = 0
				boosts[i] += stealboosts[i]



	speed_ratio = (m_stats[4]+0.01) / (o_stats[4]+0.01)

	if speed_ratio >1:
		speed_ratio = ( 1 - 1 / speed_ratio ) /2
	else:
		speed_ratio = ( speed_ratio - 1 ) /2
	if Field.TRICK_ROOM in _field:
		speed_ratio *= -1 

	#p5 modifies if this is a switch
	if move._id == "switch":
		v[0] = 7
		if ability == "intimidate":
			if oppo_ability not in ("scrappy","owntempo","innerfocus","oblivious",):
				v[13] -= 1
				if oppo_ability == "rattled":
					v[17] += 1
				if oppo_item == "adrenalineorb":
					v[17] += 1
					v[99] = 1	
		if oppo_ability == "shadowtag" and ability != "shadowtag" and PokemonType.GHOST not in types:
			v[41] = 1	
		if ability == "shadowtag" and oppo_ability != "shadowtag":	
			v[42] = 2
		if oppo_ability == "magnetpull" and PokemonType.STEEL in types and PokemonType.GHOST not in types:
			v[41] = 1			
		if ability == "magnetpull" and PokemonType.STEEL in oppo_types:
			v[42] = 2
		if oppo_ability == "arenatrap" and _is_grounded(mon,field):
			v[41] = 1		
		if ability == "arenatrap" and _is_grounded(oppo,field):
			v[42] = 2
		if ability == "download":
			pd = pokemon_vectorize(oppo,{},{},False,False)[18]
			sd = pokemon_vectorize(oppo,{},{},False,False)[20]		#test it
			if sd < pd:
				v[8] = 1
			else:
				v[6] = 1
		if ability == "intrepidsword":
			v[6] = 1
		if ability == "dauntlessshield":
			v[7] = 1		
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
				pdmg += PokemonType.ROCK.damage_multiplier(*types) / 8
			if _is_grounded(mon,field):
				if SideCondition.SPIKES in side:
					pdmg += 1 / ( 10- 2 * side[SideCondition.SPIKES] )
				if SideCondition.TOXIC_SPIKES in side:
					if PokemonType.POISON in types:
						v[78] = side[SideCondition.TOXIC_SPIKES]
					else:
						if PokemonType.STEEL not in types:
							v[96] = side[SideCondition.TOXIC_SPIKES]
				if SideCondition.STICKY_WEB in side:
					if ability not in ("clearbody","whitesmoke","fullmetalbody") and SideCondition.MIST not in side:
						if ability == "mirrorarmor":		# regard as by self move, not by target
							v[17] -= 1
						else:
							v[10] -= 1
							if ability == "defiant":
								v[6] += 2	
							if ability == "competitive":
								v[8] += 2							
	
	if move._id != "switch":
		v = move_vectorize(move)
		if v[26] > 0 :
			heal += v[26]
		else:
			pdmg -= v[26]	

	#p6. modifies type and priority
	if move._id == "weatherball" and weather:
		v[2] *= 2
		if Weather.SUNNYDAY in weather:
			movetype = PokemonType.FIRE
		if Weather.RAINDANCE in weather:
			movetype = PokemonType.WATER
		if Weather.SANDSTORM in weather:
			movetype = PokemonType.ROCK
		if Weather.HAIL in weather:
			movetype = PokemonType.ICE

	if move._id == "terrainpulse":
		if Field.ELECTRIC_TERRAIN in _field:
			v[2] *= 2
			movetype = PokemonType.ELECTRIC
		if Field.GRASSY_TERRAIN in _field:
			v[2] *= 2
			movetype = PokemonType.GRASS
		if Field.MISTY_TERRAIN in _field:
			v[2] *= 2
			movetype = PokemonType.FAIRY
		if Field.PSYCHIC_TERRAIN in _field:
			v[2] *= 2
			movetype = PokemonType.PSYCHIC

	if movetype == PokemonType.NORMAL:
		if ability == "refrigerate":
			v[1:3] *= 1.2
			movetype = PokemonType.ICE
		if ability == "pixilate":
			v[1:3] *= 1.2
			movetype = PokemonType.FAIRY	
		if ability == "aerilate":
			v[1:3] *= 1.2
			movetype = PokemonType.FLYING
		if ability == "galvanize":
			v[1:3] *= 1.2
			movetype = PokemonType.ELECTRIC	

	if ability == "liquidvoice" and v[32]:
		movetype = PokemonType.WATER



	if ability == "normalize" and movetype != PokemonType.NORMAL:
		movetype = PokemonType.NORMAL
		v[1:3] *= 1.2

	if ability in ("protean","libero"):
		types = list([movetype])								#test this

	if ability == "prankster" and move.entry["category"] == "Status":
		v[0] += 1
	if ability == "galewings" and movetype == PokemonType.FLYING and m_stats[5] == 1:
		v[0] += 1
	if ability == "triage" and (heal > 0 or v[27] > 0):
		v[0] += 3

	if item == "custapberry" and m_stats[6] < 1/4:
		speed_ratio = 0.499
		v[98] = 0


	#p7. modiefies if has no effect and accurancy

	
	if item == "protectivepads" or ability == "longreach":
		v[31] = 0
	if move._id in ("solarbeam","solarblade") and Weather.SUNNYDAY in weather:
		v[35] = 0

	if item == "powerherb" and v[35]:
		v[35] = 0
		v[98] = 1

	if ability == "truant":
		v[37] = 1
	if ability == "unseenfist" and v[31]:
		v[47] = 1
	
	if "defrost" in move.entry["flags"] and mon._mon._status and mon._mon._status.name == "FRZ":
		v[80] = 1	

	if "damp" in (ability,oppo_ability):
		if move._id in ("selfdestruct","explosion","mindblown","mistyexplosion"):
			v[1:] *= 0
	if Effect.THROAT_CHOP in effects and v[32]:
		v[1:] *= 0

	if move.entry.get("target",{}) in ("normal","allAdjacent","allAdjacentFoes","randomNormal","any"):
		if oppo_ability == "soundproof" and v[32]:
			v[1:] *= 0
		if (oppo_ability == "overcoat" or oppo_item == "safetygoggles" or PokemonType.GRASS in oppo_types) and v[33]:
			v[1:] *= 0
		if ability == "prankster" and move.entry["category"] == "Status" and PokemonType.DARK in oppo_types:
			v[1:] *= 0
		if v[0] > 0 and Field.PSYCHIC_TERRAIN in oppo_field or oppo_ability in ("queenlymajesty","dazzling"):
			v[1:] *= 0
	
	if oppo_ability == "bulletproof" and "bullet" in move.entry["flags"]:
		v[1:] *= 0
	if Field.GRAVITY in _field and "gravity" in move.entry["flags"]:
		v[1:] *= 0

	if item == "assaultvest" or Effect.TAUNT in effects:
		if move.entry["category"] == "Status":
			v[1:] *= 0

	if mon._mon._first_turn == False:
 		if v[40] == 1:
 			v[1:] *= 0

	if move._id == "rest":
		if ability in ("insomnia","vitalspirit","sweetveil","comatose"):
			v[1:] *= 0
		if Field.ELECTRIC_TERRAIN in field or Field.MISTY_TERRAIN in field:
			v[1:] *= 0
	if move._id in ("sleeptalk","snore") and mon._mon._status and mon._mon._status.name != "SLP" and ability != "comatose":
		v[1:] *= 0
	if move._id in ("dreameater","nightmare") and oppo._mon._status.name != "SLP" and oppo_ability != "comatose":
		v[1:] *= 0
	if move._id == "steelroller":
		if Field.ELECTRIC_TERRAIN not in _field:
			if Field.GRASSY_TERRAIN not in _field:
				if Field.MISTY_TERRAIN not in _field:
					if Field.PSYCHIC_TERRAIN not in _field:
						v[1:] *= 0.01
	if move._id == "auroraveil":
		if Weather.HAIL not in weather:
			v[1:] *= 0
	if move._id == "futuresight":
		if Effect.FUTURE_SIGHT in oppo_effects:
			v[1:] *= 0
	if move._id == "noretreat":
		if Effect.NO_RETREAT in effects:
			v[1:] *= 0
	if mon._last_move == "wish" and move._id == "wish":
		v[1:] *= 0
	if mon._last_move == "destinybond" and move._id == "destinybond":
		v[1:] *= 0


	if oppo_ability == "wonderguard":
		if v[1] or v[2] or v[53]:
			if movetype.damage_multiplier(*oppo_types) < 1.1:
				v[1:] *= 0
	if oppo_ability == "sturdy" and "ohko" in move.entry:
		v[1:] *= 0




	v[44:47] *= 0.3 ** mon._mon._protect_counter





	#if opponent can change weather, weather = ...
	#!! if already ingrain, ingrain is not useful, etc


	







	#p8. modiefies power and acc and 
	v[0] += speed_ratio


	v[53] /= o_stats[6]														#turn to %

	if move._id == "shellsidearm":
		pd = pokemon_vectorize(oppo,{},{},False,False)[18]
		sd = pokemon_vectorize(oppo,{},{},False,False)[20]
		pa = pokemon_vectorize(mon,{},{},False,False)[17]
		sa = pokemon_vectorize(mon,{},{},False,False)[19]
		if pa / pd > sa / sd:
			v[1] = move.base_power
			v[31] = 1
		else:
			v[2] = move.base_power

	if move._id == "photongeyser":
		pa = pokemon_vectorize(mon,{},{},False,False)[17]
		sa = pokemon_vectorize(mon,{},{},False,False)[19]
		if pa > sa:
			v[1] = move.base_power
		else:
			v[2] = move.base_power

	if move._id == "acrobatics":			#test this
		if item in ("lost",""):
			v[1] *= 2
	
	if move._id in ("boltbeak","fishiousrend"):				#not correct but nvm
		if v[0] > 0:
			v[1] *= 2
	if ability == "analytic":				#not correct but nvm
		if v[0] < 0:
			v[1:3] *= 1.3


	if move._id == "grassknot":
		v[2] = grassknotpower(oppo_weight)
	if move._id == "lowkick":
		v[1] = grassknotpower(oppo_weight)
	if move._id in ("heatcrash","heavyslam"):
		v[1] = heatcrashpower(weight,oppo_weight)
	if move._id == "gyroball":
		v[1] = min( 25 * o_stats[4] / m_stats[4], 150 )
	if move._id == "electroball":
		v[2] = electroballpower(m_stats[4],o_stats[4])
	if move._id == "wringout":
		v[2] = 1 + 120 * o_stats[5]
	if move._id == "crushgrip":
		v[1] = 1 + 100 * o_stats[5]
	if move._id in ("waterspout","eruption","dragonenergy"):
		v[2] = 150 * m_stats[6]
	if move._id in ("reversal","flail"):
		v[1] = reversalpower(mon)
	if move._id == "punishment":
		b = 0
		for i in range(0,5):
			b += max(0, oppo_boosts[i])
		v[1] = min(200,60+b*20)
	if move._id == "powertrip":
		b = 0
		for i in range(0,7):
			b += max(0, boosts[i])
		v[1] = 20+b*20
	if move._id == "storedpower":
		b = 0
		for i in range(0,7):
			b += max(0, boosts[i])
		v[2] = 20+b*20

	if move._id == "hex":
		if mon._mon._status:
			v[2] *= 2

	if move._id == "facade":
		if mon._mon._status and mon._mon._status.name in ("BRN","PAR","TOX","PSN"):
			v[1] *= 2

	if move._id == "brine":
		if o_stats[5] < 0.5:
			v[2] *= 2

	if ability == "technician":
		if v[1] <= 60:
			v[1] *= 1.5
		if v[2] <= 60:
			v[2] *= 1.5





	if move._id in ("naturesmadness","superfang"):
		v[53] = o_stats[5] / 2
	if move._id == "endeavor":
		v[53] = max( 0, o_stats[5] - m_stats[6]*m_stats[6]/o_stats[6] )
	if move._id == "finalgambit":
		v[53] = m_stats[6] * m_stats[6] / m_stats[6]
	if move.entry.get("volatileStatus","") == "partiallytrapped":
		v[53] = o_stats[5] / 8

	if mon._mon._status and mon._mon._status.name == "BRN" and ability != "guts" and move._id != "facade":
		v[1] /= 2





	if Weather.RAINDANCE in weather and move._id in ("thunder","hurricane"):
		v[4] = 10
	if Weather.HAIL in weather and move._id == "blizzard":
		v[4] = 10
	if "noguard" in (ability,oppo_ability):
		v[4] = 10
	if PokemonType.POISON in types and move._id == "toxic":
		v[4] = 10
#	if Effect.MINIMIZE in oppo_effects and move._id in crushmove:
#		v[4] = 10
#		v[1:3] *= 2


	

	if move.entry.get("target",{}) in ("normal","allAdjacent","allAdjacentFoes","randomNormal","any"):
		if v[4] == 10:
			v[4] = 1
		else:
			if "ohko" in move.entry:
				v[4] = 0.3
				if move._id == "sheercold":
					if PokemonType.ICE not in types:
						v[4] = 0.2
			else:	
				acc_rate = acc
				if move._id not in ("psychick","psystrike","secretsword"):
					acc_rate -= o_eva
				if acc_rate > 0:
					acc_rate = ( acc_rate + 3 ) / 3
				else:
					acc_rate = 3 / ( acc_rate + 3 )



				v[4] *= acc_rate
				if Field.GRAVITY in field:
					v[4] *= 5/3
				if ability == "compoundeyes":
					v[4] *= 1.3
				if ability == "hustle" and v[1]:
					v[4] *= 0.8
				if ability == "victorystar":
					v[4] *= 1.1
				if item == "widelens":
					v[4] *= 1.1

				if oppo_ability == "tangledfeet" and Effect.CONFUSION in oppo_effects:
					v[4] /= 1.5
				if oppo_ability == "snowcloak" and Weather.HAIL in weather:
					v[4] /= 1.2
				if oppo_ability == "sandveil" and Weather.SANDSTORM in weather:
					v[4] /= 1.2
				if oppo_ability == "wonderskin" and move.entry["category"] == "Status":
					v[4] /= 2
				if oppo_item in ("brightpowder","laxincense"):
					v[4] *= 0.9
				if item == "blunderpolicy":
					v[10] += 2 * (1 - v[4])
					v[98] = 1
	v[4] = min(v[4],1)


	
	if v[1] or v[2]:
		if oppo_ability in ("battlearmor","shellarmor") or SideCondition.LUCKY_CHANT in oppo_side:
			v[5] = 0
		else:
			if ability == "merciless" and oppo._mon._status.name in ("TOX","PSN"):
				v[5] = 3
			if ability == "superluck":
				v[5] += 1
			if item in ("scopelens","razorclaw"):
				v[5] += 1
			if Effect.FOCUS_ENERGY in effects:
				v[5] += 2
			if mon._mon._species in ("farfetchd","farfetchdgalar","sirfetchd") and item == "leek":
				v[5] += 2
			if mon._mon._species == "chansey" and item == "luckypunch":
				v[5] += 2

			if v[5] == 0:
				v[5] = 1/24
			else:
				if v[5] == 1:
					v[5] = 1/8
				else:
					if v[5] == 2:
						v[5] = 1/2
					else:
						v[5] = 1
	if _crit:
		v[5] = 0




	if mon._mon._status and mon._mon._status.name == "FRZ" and "defrost" not in move.entry["flags"]:
		v[4] *= 0.25
	if mon._mon._status and mon._mon._status.name == "PAR":
		v[4] *= 0.75
	if (mon._mon._status and mon._mon._status.name == "SLP" or ability == "comatose") and  move._id not in ("sleeptalk","snore"):
		v[4] *= 0

	if Effect.CONFUSION in effects:
		v[4] *= 2 / 3
		selfattact += 40* ( 2 * mon._mon._level + 10) / 250 * m_stats[0] / m_stats[1] / 3 / m_stats[6]
	if Effect.ATTRACT in effects:
		v[4] *= 0.5

	if move.entry.get("target",{}) in ("normal","allAdjacent","allAdjacentFoes","randomNormal","any"):

		if "ohko" in move.entry:
			v[1] = 10
			if move._id == "sheercold":
				if PokemonType.ICE in oppo_types:
					v[1] = 0
			else:
				if movetype.damage_multiplier(*oppo_types) == 0:
					v[1] = 0
		else:	
			damage_multiplier = 1		
			if PokemonType.FLYING in oppo_types and (move._id == "thousandarrows" or oppo_item == "ironball"):
				damage_multiplier *= 1
			else:
				if _is_grounded(oppo,field) and movetype == PokemonType.GROUND:		
					for _type in oppo_types:
						if _type != PokemonType.FLYING:
							damage_multiplier *= movetype.damage_multiplier(_type)
				else:			
					if ability == "scrappy" and movetype in (PokemonType.NORMAL,PokemonType.FIGHTING):
						for _type in oppo_types:
							if _type != PokemonType.GHOST:
								damage_multiplier *= movetype.damage_multiplier(_type)
					else:
						for _type in oppo_types:
							damage_multiplier *= movetype.damage_multiplier(_type)
			if v[1] or v[2] or v[53] or move._id == "thunderwave":
				if damage_multiplier == 0:
					if v[28]:
						pdmg += 1/2
					v = v * vclear 
			
			if move._id == "flyingpress":
				damage_multiplier *= PokemonType.FLYING.damage_multiplier(*oppo_types)


			if oppo_item == "weaknesspolicy" and damage_multiplier > 1.5:
				v[13] += 2
				v[15] += 2
				v[99] = 1

			if ability == "tintedlens" and damage_multiplier < 0.9:
				damage_multiplier *= 2
			if oppo_ability in ("filter","solidrock","prismarmor") and damage_multiplier > 1.1:
				damage_multiplier *= 0.75

			if ability == "neuroforce" and damage_multiplier > 1.1:
				damage_multiplier *= 1.25
			if item == "expertbelt" and damage_multiplier > 1.4:
				damage_multiplier *= 1.20





			if ability == "parentalbond":
				v[30] = 1 + v[30] * 2
				damage_multiplier *= 1.25
				v[53] *= 1.25
			if ability == "skilllink" and v[30] > 2.1:
				damage_multiplier = 4
			if move._id in ("tripleaxel","triplekick"):
				damage_multiplier *= 5.23
			else:
				damage_multiplier *= 1 + v[30]
			
			if move._id == "knockoff":
				if oppo._mon._item and oppo._mon._item != "lost":
					damage_multiplier *= 1.5

			if move._id in ("solarbeam","solarblade") and Weather.RAINDANCE in weather:
				damage_multiplier *= 0.5

			if move._id == "risingvoltage" and Field.ELECTRIC_TERRAIN in oppo_field:
				damage_multiplier *= 2
			if move._id in ("earthquake","magnitude","bulldoze") and Field.GRASSY_TERRAIN in _field:
				damage_multiplier *= 1.5
			if move._id == "mistyexplosion" and Field.MISTY_TERRAIN in field:
				damage_multiplier *= 1.5
			if move._id == "expandingforce" and Field.PSYCHIC_TERRAIN in field:
				damage_multiplier *= 1.5





			if m_stats[6] < 1/3:
				if movetype == PokemonType.GRASS and ability == "overgrow":
					damage_multiplier *= 1.5
				if movetype == PokemonType.FIRE and ability == "blaze":
					damage_multiplier *= 1.5		
				if movetype == PokemonType.WATER and ability == "torrent":
					damage_multiplier *= 1.5
				if movetype == PokemonType.BUG and ability == "swarm":
					damage_multiplier *= 1.5


			if item in typeboostitem:
				if typeboostitem[item] == movetype:
					damage_multiplier *= 1.2
			if oppo_item in antitypeberry:
				if antitypeberry[oppo_item] == movetype:
					damage_multiplier *= 0.5
					v[99] = 1	
					if oppo_ability == "cheekpouch":
						v[53] -= 1/3
			if movetype == PokemonType.DARK:
				if "darkdura" in (ability,oppo_ability):
					if "aurabreak" in (ability,oppo_ability):
						damage_multiplier *= 0.75
					else:
						damage_multiplier *= 4/3			
			if movetype == PokemonType.DRAGON:
				if Field.MISTY_TERRAIN in oppo_field:
					damage_multiplier *= 0.5
				if ability == "dragonsmaw":
					damage_multiplier *= 1.5
			if movetype == PokemonType.ELECTRIC:
				if Field.ELECTRIC_TERRAIN in field:
					damage_multiplier *= 1.3
				if ability == "transistor":
					damage_multiplier *= 1.5
				if oppo_ability == "voltabsorb":
					v = v * vclear 
					v[53] = -1/2
				if oppo_ability == "lightningrod":
					v = v * vclear 
					v[15] = 1
				if oppo_ability == "motordrive":
					v = v * vclear 
					v[17] = 1	
			if movetype == PokemonType.FAIRY:
				if "fairydura" in (ability,oppo_ability):
					if "aurabreak" in (ability,oppo_ability):
						damage_multiplier *= 0.75
					else:
						damage_multiplier *= 4/3
			if movetype == PokemonType.FIRE:
				if Weather.SUNNYDAY in oppo_weather:
					damage_multiplier *= 1.5
				if Weather.RAINDANCE in oppo_weather:
					damage_multiplier *= 0.5
				if oppo_ability in ("thickfat","heatproof"):
					damage_multiplier *= 0.5
				if oppo_ability == "dryskin":
					damage_multiplier *= 1.25
				if oppo_ability == "fluffy":
					damage_multiplier *= 2
				if Effect.FLASH_FIRE in effects:
					damage_multiplier *= 1.5
				if oppo_ability == "flashfire":
					v = v * vclear 
					v[13] = 0.5
					v[15] = 0.5
			if movetype == PokemonType.GRASS:
				if Field.GRASSY_TERRAIN in field:
					damage_multiplier *= 1.3
				if oppo_ability == "sapsipper":
					v = v * vclear
					v[13] = 1			
			if movetype == PokemonType.GROUND:
				if oppo_ability == "levitate" and _is_grounded(oppo,field) == False:
					v = v * vclear 		
			if movetype == PokemonType.ICE:
				if oppo_ability == "thickfat":
					damage_multiplier *= 0.5
			if movetype == PokemonType.PSYCHIC:
				if Field.PSYCHIC_TERRAIN in field:
					damage_multiplier *= 1.3	
			if movetype == PokemonType.STEEL:
				if ability in ("steelworker","steelyspirit"): 		#"steelyspirit" work for team in double
					damage_multiplier *= 1.5			
			if movetype == PokemonType.WATER:
				if Weather.SUNNYDAY in oppo_weather:
					damage_multiplier *= 0.5
				if Weather.RAINDANCE in oppo_weather:
					damage_multiplier *= 1.5				
				if ability == "waterbubble":
					damage_multiplier *= 2
				if oppo_ability == "waterbubble":
					damage_multiplier *= 0.5
				if oppo_ability == "waterabsorb":
					v = v * vclear 
					v[53] = -1/2
				if oppo_ability == "dryskin":
					v = v * vclear 
					v[53] = -1/4
				if oppo_ability == "stormdrain":
					v = v * vclear 
					v[15] = 1


		




			if ability == "sheerforce":
				if np.linalg.norm(v[13:25]) or v[55]:
					damage_multiplier *= 1.3
				if oppo_item in ("redcard","ejectbutton","keeberry","marangaberry"):
					oppo_item == ""
				if oppo_ability in ("berserk","wimpout","emergencyexit"):
					oppo_ability == ""

			if ability == "ironfist":
				if "punch" in move.entry["flags"]:
					damage_multiplier *= 1.2
			if ability == "strongjaw":
				if "bite" in move.entry["flags"]:
					damage_multiplier *= 1.5
			if ability == "megalauncher":
				if "pulse" in move.entry["flags"]:
					damage_multiplier *= 1.5
					v[53] *= 1.5
			if v[31]:
				if ability == "toughclaws":
					damage_multiplier *= 1.3
				if oppo_ability == "fluffy":
					damage_multiplier *= 0.5
			if v[32]:
				if ability == "punkrock":
					damage_multiplier *= 1.3				
				if oppo_ability == "punkrock":
					damage_multiplier *= 0.5

			if ability == "reckless":
				if "recoil" in move.entry or "hasCrashDamage" in move.entry:
					damage_multiplier *= 1.2
			if oppo_ability in ("multiscale","shadowshield"):
				if o_stats[5] == 1:
					damage_multiplier *= 0.5
			if oppo_ability == "furcoat" and move.entry["category"] == "Physical":
				damage_multiplier *= 0.5
				v[53] /= 2
			if oppo_ability == "icescales" and move.entry["category"] == "Special":
				damage_multiplier *= 0.5
				v[53] /= 2

			if ability == "rivalry":
				if mon._mon._gender == PokemonGender.MALE:
					if oppo._mon._gender == PokemonGender.MALE:
						damage_multiplier *= 1.25
					else:
						if oppo._mon._gender == PokemonGender.FEMALE:
							damage_multiplier *= 0.75
				if mon._mon._gender == PokemonGender.FEMALE:
					if oppo._mon._gender == PokemonGender.FEMALE:
						damage_multiplier *= 1.25
					else:
						if oppo._mon._gender == PokemonGender.MALE:
							damage_multiplier *= 0.75

			if ability == "sandforce" and Weather.SANDSTORM in weather:
				if movetype in (PokemonType.GROUND,PokemonType.ROCK,PokemonType.STEEL):
					damage_multiplier *= 1.3


			if item == "lifeorb":
				damage_multiplier *= 1.3

			#is stab
			if movetype in types:
				if ability == "adaptability":
					damage_multiplier *= 2
				else:
					damage_multiplier *= 1.5
			#crit
			if  _crit:
				damage_multiplier *= 1.5
				if ability == "sniper":
					damage_multiplier *= 1.5

			if v[5] == 1:
				return modified_move_vector(
					move,
					mon,
					oppo,
					_weather,
					_field,
					_side,_oppo_side,
					ability, 
					item,
					oppo_ability, 
					oppo_item,
					_crit = True)



			if move._id == "bodypress":
				damage_multiplier *= pokemon_vectorize(mon,weather,field,ability,item)[17] / pokemon_vectorize(mon,weather,field,False,False)[17]
				m_stats[0] = pokemon_vectorize(mon,weather,field,False,False)[18]
			if move._id == "foulplay":
				damage_multiplier *= pokemon_vectorize(mon,weather,field,ability,item)[17] / pokemon_vectorize(mon,weather,field,False,False)[17]
				m_stats[0] = pokemon_vectorize(oppo,weather,field,False,False)[17]		
			if move._id in ("psychick","psystrike","secretsword"):
				o_stats[3] = o_stats[1]

			if ability != "infiltrator":
				if SideCondition.REFLECT in oppo_side or SideCondition.AURORA_VEIL in oppo_side:
					if move.entry["category"] == "Physical":
						damage_multiplier *= 0.5
						v[53] /= 2
				if SideCondition.LIGHT_SCREEN in oppo_side or SideCondition.AURORA_VEIL in oppo_side:
					if move.entry["category"] == "Special":
						damage_multiplier *= 0.5
						v[53] /= 2					




			damage_multiplier *= 0.925 # randomness

			v[1] *=  ( 2 * mon._mon._level + 10) / 250 * m_stats[0] / o_stats[1] / o_stats[6] * damage_multiplier
			v[2] *= ( 2 * mon._mon._level + 10) / 250 * m_stats[2] / o_stats[3] / o_stats[6] * damage_multiplier

			if o_stats[5] == 1:
				if oppo_item == "focussash":
					if v[1] > 1:
						v[1] = 0.999
						v[99] = 1
					if v[2] > 1:
						v[2] = 0.999
						v[99] = 1
				if oppo_ability == "sturdy":
					if v[1] > 1:
						v[1] = 0.999
					if v[2] > 1:
						v[2] = 0.999

			if oppo._mon._species == "shedinja":
				v[1] = min(v[1],4)
				v[2] = min(v[2],4)
				v[53] = min(v[53],4)



		if pokemon_vectorize(oppo,oppo_weather,oppo_field,oppo_ability,oppo_item)[14]:
			sub_damage =  v[1]+v[2]+v[53]
			if Effect.SUBSTITUTE in oppo_effects and ability != "infiltrator" and v[32] != 1:
				if v[1]+v[2]+v[53] > 1/4:
					v[54] = 1
					if v[30]:
						v[1] -= 1/4
					else:
						v[1:3] *= 0.001
						v[53] = 0.001
				else:
					v[54] = v[1]+v[2]+v[53]
					v[1:3] *= 0.001
					v[53] = 0.001
				if move.entry["category"] == "Status":
					v = v * vclear
			else: 
				if oppo._mon._species == "mimikyu":
					if v[1]+v[2]+v[53]:
						v[1:3] *= v[30] / ( 1.001 + v[30] )
						v[53] = 1/8
						v[54] = 1
				if oppo._mon._species == "eiscue":
					if move.entry["category"] == "Physical":
						v[1] *= v[30] / ( 1.001 + v[30] )
						v[54] = 1
		


	#p9. modifies side effect
	v[6:20] *= 1 + v[30]
	for i in range(0,5):
		v[20+i] = 1 - ( 1 - v[20+i] ) ** ( 1 + v[30] )

	if oppo_ability == "magicbounce":
		if "reflectable" in move.entry["flags"]:
			v[93:98] = v[20:25]
			v[6:13] = v[13:20]
			v[20:25] *= 0
			v[13:20] *= 0
			v[56:63] *= -1
			v[68:70] *= -1
			v[72:76] *= -1
	if oppo_ability == "steadfast":
		v[17] += v[55]

	if item == "throatspray" and v[32]:
		v[8] += 1
		v[98] = 1

		

	if oppo_ability == "baddreams":								#Nightmare
		if mon._mon._status and mon._mon._status.name == "SLP" or ability == "comatose":
			pdmg += 1/8
	if Effect.SUBSTITUTE in effects or m_stats[6] < 1/4:
		v[92] *= 0.5







	
#	if deal damage
	if v[1] or v[2] or v[53]:
		if item == "lifeorb" and ability != "sheerforce":
			pdmg += 1/10
		if item == "shellbell" and Effect.HEAL_BLOCK not in effects:
			v[27] += 1/8
		if item == "bigroot" and v[27] > 0:
			v[27] *= 1.3

		if ability == "stench" or item in ("kingsrock","razorfang"):
			v[55] += 1 - 0.9 ** ( 1 + v[30] )
		if ability == "serenegrace":
			v[13:25] *= 2 							#test this
			v[55] *= 2		
		if oppo_ability == "shielddust" or ability == "sheerforce":
			v[13:25] *= 0
			v[55] *= 0
		if oppo_ability == "cursedbody":				# not exactly but nvm...
			v[59] = -1 + 0.7 ** ( 1 + v[30] )
		if oppo_ability == "angerpoint":
			v[13] += 12 * v[5] * ( 1 + v[30] )
		if oppo_ability == "justified" and movetype == PokemonType.DARK:
			v[13] += 1 * ( 1 + v[30] )
		if oppo_ability == "rattled" and movetype in (PokemonType.DARK,PokemonType.GHOST,PokemonType.BUG):
			v[13] += 1 * ( 1 + v[30] )
		if oppo_ability == "stamina":
			v[14] += 1 * ( 1 + v[30] )
		if oppo_ability == "watercompaction" and movetype == PokemonType.WATER:
			v[14] += 2 * ( 1 + v[30] )
		if oppo_ability == "steamengine" and movetype in (PokemonType.FIRE,PokemonType.WATER):
			v[17] += 12
		if oppo_ability == "cottondown":
			v[10] -= 1 * ( 1 + v[30] )	
		if ability == "analytic":
			v[25] -= 0.3
		if oppo_ability == "sandspit":
			v[85] = 1

		if move._id == "spectralthief":							
			for i in range(0,5):
				if stealboosts[i] > 0:
					v[6+i] += 0.01 + stealboosts[i]
					v[13+i] += - 0.01 - stealboosts[i]
		if move._id == "clearsmog":							
			for i in range(0,5):
				v[13+i] = -stealboosts[i]

		#contact
		if v[31]:
			if oppo_ability in ("roughskin","ironbarbs"):
				pdmg += 1/8 * ( 1 + v[30] )
			if oppo_item ==  "rockyhelmet":
				pdmg += 1/6 * ( 1 + v[30] )

			if oppo_ability == "flamebody":
				v[93] = 1 - ( 1 - v[93] ) * 0.7 ** ( 1 + v[30] )
			if oppo_ability == "static":
				v[95] = 1 - ( 1 - v[93] ) * 0.7 ** ( 1 + v[30] )
			if oppo_ability == "effectspore":
				if item != "safetygoggles" and ability != "overcoat" and PokemonType.GRASS not in types:
					v[93] = 1 - ( 1 - v[93] ) * 0.9 ** ( 1 + v[30] )
					v[95] = 1 - ( 1 - v[95] ) * 0.9 ** ( 1 + v[30] )
					v[96] = 1 - ( 1 - v[95] ) * 0.9 ** ( 1 + v[30] )
			if oppo_ability in ("gooey","tanglinghair"):
				v[10] -= 1 * ( 1 + v[30] )		
			if oppo_ability == "aftermath" and ability != "damp":
				if v[1]+v[2]+v[53] > o_stats[5]:
					pdmg += 1/4
			if ability == "poisontouch":
				v[23] += 1 - 0.7 ** ( 1 + v[30] )
			if oppo_ability in ("mummy","wanderingspirit"):
				v[82] = 1
			if oppo_ability == "perishbody":
				v[50] = 2

		if move.entry["category"] == "Physical":
			if oppo_ability == "weakarmor":
				v[14] -= ( 1 + v[30] )
				v[17] += 2 * ( 1 + v[30] )
			if oppo_item == "keeberry":
				v[14] += 1
				v[99] = 1
				if oppo_ability == "cheekpouch":
					v[53] -= 1/3
		if move.entry["category"] == "Special":
			if oppo_item == "marangaberry":
				v[16] += 1
				v[99] = 1
				if oppo_ability == "cheekpouch":
					v[53] -= 1/3



	if move._id == "strengthsap":
		heal += o_stats[0]/m_stats[6]
	if move._id in ("synthesis","morningsun","moonlight"):
		if Weather.SUNNYDAY in weather:
			heal += 1/6
		if Weather.RAINDANCE in weather or Weather.SANDSTORM in weather or Weather.HAIL in weather:
			heal -= 1/4
	if move._id == "shoreup":
		if Weather.SANDSTORM in weather:
			heal += 1/6


	if v[1]+v[2]+v[53] > o_stats[5]:
		if ability in ("moxie","chillingneigh","asoneglastrier"):
			v[6] += 1
		if ability in ("grimneigh","asonespectrier"):
			v[7] += 1
		if ability == "beastboost":									#test this
			tempstats = list(pokemon_vectorize(mon,{},{},False,False)[17:22])
			i = tempstats.index(max(tempstats))
			v[6+i] += 1 
		if move._id == "fellstinger":
			v[6] += 3
		if oppo_ability == "innardsout":
			pdmg += o_stats[5] * o_stats[6] / m_stats[6]


	if v[1]+v[2]+v[53]-v_oppo[8] > o_stats[5]:
		if ability == "soulheart":
			v[7] += 1

	
	if oppo_ability == "synchronize":
		v[93] += v[20]
		v[95] += v[22]
		v[96] += v[23]





	#p10 modifies one-time effect (berry,beserker, Fell Stinger, asone, etc)

	# use item slot98 use oppo_item slot99 
	if v[1] or v[2] or v[53]:
		if oppo_item == "redcard" and ability != "suctioncups":
			v[38] = 1
			v[99] = 1
		if oppo_item == "ejectbutton":
			v[39] = 1
			v[38] = 0
			v[99] = 1

	if v[1]+v[2]+v[53] > o_stats[5] - 1/4 and v[1]+v[2]+v[53] < 1:
		if oppo_item in giantberry:
			v[53] -= 1/3
			v[99] = 1
			if oppo_ability == "cheekpouch":
				v[53] -= 1/3
	else:
		if v[1]+v[2]+v[53] > o_stats[5] - 1/2:
			if oppo_ability in ("wimpout","emergencyexit"):
				v[39] = 1
				v[38] = 0
			if oppo_ability == "berserk":
				v[15] += 1
			if oppo_ability == "gluttony" and oppo_item in giantberry:
				v[53] -= 1/3
				v[99] = 1
			if oppo_item == "sitrusberry":
				v[53] -= 1/4
				v[99] = 1
				if oppo_ability == "cheekpouch":
					v[53] -= 1/3


	if item == "ejectpack":
		for i in range(0,7):
			if v[6+i]<0:
				v[38] = 1
				v[98] = 1
	if oppo_item == "ejectpack":
		for i in range(0,7):
			if v[13+i]<0:
				v[39] = 1
				v[99] = 1
	
	#Gluttony, Cheek Pouch, berry

	# happens at end of turn
	if ability == "speedboost":
		v[10] += 1
	if ability == "moody":
		for i in range (0,5):
			v[6+i] += 0.2
	if ability == "shedskin":
		v[80] += 1/3


	#side-effect-inmune
	if Weather.SUNNYDAY in oppo_weather:
		if oppo_ability == "leafguard":
			v[20:25] *= 0
			v[56] = 0
			v[69] = 0			
	if Weather.SUNNYDAY in weather:
		if ability == "leafguard":
			v[93:98] *= 0
	if Weather.SUNNYDAY in _weather:
			v[83] /= 10
	if Weather.RAINDANCE in oppo_weather:
		if oppo_ability == "hydration":
			v[20:25] *= 0.1
			v[56] *= 0.1
			v[69] *= 0.1	
	if Weather.RAINDANCE in weather:
		if ability == "hydration":
			v[80] += 1
	if Weather.RAINDANCE in _weather:
		v[84] /= 10
	if Weather.SANDSTORM in _weather:
		v[85] /= 10
	if Weather.HAIL in _weather:
		v[86] /= 10

	if Field.ELECTRIC_TERRAIN in field:
		v[97] = 0					
	if Field.ELECTRIC_TERRAIN in oppo_field:
		v[24] = 0
		v[69] = 0
	if Field.ELECTRIC_TERRAIN in _field:
		v[87] /= 10
	if Field.GRASSY_TERRAIN in _field:
		v[88] /= 10	
	if Field.MISTY_TERRAIN in field:
		v[93:98] *= 0
	if Field.MISTY_TERRAIN in oppo_field:		
		v[20:25] *= 0
		v[56] = 0
		v[69] = 0
	if Field.MISTY_TERRAIN in _field:
		v[89] /= 10
	if Field.PSYCHIC_TERRAIN in _field:
		v[90] /= 10	


	if oppo_ability == "hypercutter":
		if v[13] < 0:
			v[13] = 0
	if oppo_ability == "bigpecks":
		if v[14] < 0:
			v[14] = 0
	if oppo_ability == "keeneye":
		if v[18] < 0:
			v[18] = 0
	if oppo_ability in ("clearbody","whitesmoke","fullmetalbody") or SideCondition.MIST in side:
		for i in range(0,7):
			if v[13+i] < 0:
				v[13+i] = 0
	if ability == "unaware":
		for i in range(0,4):
			if v[13+i] > 0:
				v[13+i] *=0.3
	if oppo_ability == "unaware":								#nvm
		for i in range(0,4):
			if v[6+i] > 0:
				v[6+i] = 0.1

	if ability == "contrary":
		v[6:13] *= -1		
	if oppo_ability == "contrary":
		v[13:20] *= -1			
	if oppo_ability == "mirrorarmor":
		for i in range(0,7):
			if v[13+i] < 0:
				v[6+i] = v[13+i]
				v[13+i] = 0
				if ability == "defiant":
					v[6] += 2	
				if ability == "competitive":
					v[8] += 2
	if oppo_item == "whiteherb":
		for i in range(0,7):
			if v[13+i] < 0:
				v[13+i] = 0
				v[99] = 1
	if item == "whiteherb":
		for i in range(0,7):
			if v[6+i] < 0:
				v[6+i] = 0
				v[98] = 1
	if oppo_ability == "defiant":
		for i in range(0,7):
			if v[13+i] < 0:
				v[13] += 2		
	if oppo_ability == "competitive":
		for i in range(0,7):
			if v[13+i] < 0:
				v[15] += 2	

	if ability == "simple":
		v[6:13] *= 2
	if oppo_ability == "simple":
		v[13:20] *= 2


	if Effect.LEECH_SEED in oppo_effects:
		if oppo_ability != "magicguard":
			if oppo_ability == "liquidooze":
				pdmg += o_stats[6] / m_stats[6] / 8
			else:
				heal +=  o_stats[6] / m_stats[6] / 8
				if item == "bigroot" and v[27] > 0:
					heal +=  0.3 * o_stats[6] / m_stats[6] / 8

	if Effect.HEAL_BLOCK in effects:
		heal = 0		
		if v[27] > 0:
			v[27] = 0
	if oppo_ability == "rockhead":
		if v[27] < 0:
			v[27] = 0
	if oppo_ability == "liquidooze":
		if v[27] > 0:
			v[27] *= -1
	if ability == "magicguard":
		pdmg = 0
		v[28] = 0
		if v[27] < 0:
			v[27] = 0
	v[26] = heal - pdmg - selfattact + v[28] * ( 1 - v[4])
	v[27] *= (v[1]+v[2]+v[53]) * o_stats[6] / m_stats[6]
	v[26] += pokemon_vectorize(mon,weather,field,ability,item)[8]

	if move._id == "painsplit": 
		v[53] = (o_stats[5] - m_stats[6] * m_stats[6]) / 2
		v[27] = (o_stats[5] * o_stats[6] - m_stats[6]) / 2

	if oppo_ability == "suctioncups":
		v[39] = 0
	if PokemonType.GHOST in oppo_types or oppo_item == "shedshell" or pokemon_vectorize(oppo,oppo_weather,oppo_field,oppo_ability,oppo_item)[15]:
		v[42] = 0
	if Effect.INGRAIN in effects and move._id == "ingrain":
		v[43] = 0
	if Effect.AQUA_RING in effects and move._id == "aquaring":
		v[43] = 0		
	if oppo_ability == "innerfocus":
		v[55] = 0
	if oppo_ability == "owntempo" or Effect.CONFUSION in oppo_effects:
		v[56] = 0
	if Effect.CURSE in oppo_effects:
		v[57] = 0
	if Effect.DISABLE in oppo_effects and move._id == "disable":
		v[59] = 0
	if Effect.TORMENT in oppo_effects and move._id == "torment":
		v[59] = 0
	if Effect.IMPRISON in oppo_effects and move._id == "imprison":
		v[59] = 0
	if Effect.ENCORE in oppo_effects:
		v[60] = 0
	if Effect.FOCUS_ENERGY in effects:
		v[61] = 0
	if Effect.LEECH_SEED in oppo_effects or PokemonType.GRASS in oppo_types:
		v[62] = 0
	if Effect.MAGNET_RISE in effects:
		v[65] = 0
	if Effect.SUBSTITUTE in effects:
		v[67] = 0		
	if oppo_ability == "oblivious" or Effect.TAUNT in oppo_effects:
		v[68] = 0
	if oppo_ability == "aromaveil":
		v[59] = 0
		v[60] = 0
		v[68] = 0
	if oppo_item == "mentalherb":
		v[59] = 0
		v[60] = 0
		v[68] = 0
		v[99] = 1

	if SideCondition.REFLECT in side or SideCondition.AURORA_VEIL in side:
		v[70] = 0
	if SideCondition.LIGHT_SCREEN in side or SideCondition.AURORA_VEIL in side:
		v[71] = 0
	if SideCondition.SPIKES in oppo_side and oppo_side[SideCondition.SPIKES] == 3:
		v[72] *= 0.1
	if SideCondition.STEALTH_ROCK in oppo_side:
		v[73] *= 0.1
	if SideCondition.STICKY_WEB in oppo_side:
		v[74] *= 0.1	
	if SideCondition.TOXIC_SPIKES in oppo_side and oppo_side[SideCondition.TOXIC_SPIKES] == 2:
		v[75] *= 0.1
	if SideCondition.TAILWIND in side:
		v[76] = 0
	if Field.TRICK_ROOM in _field:
		v[77] *= -1
		v[76] *= -1
	if Field.GRAVITY in _field:
		v[66] = 0

	if v[78]:
		if move._id == "defog":
			v[78] *= (2 * side_condition_vectorize(side,0)[8] - side_condition_vectorize(oppo_side,0)[8])
		if move._id == "rapidspin":
			v[78] *= side_condition_vectorize(side,0)[7]



	if oppo_ability in ("waterveil","waterbubble") or PokemonType.FIRE in oppo_types:
		v[20] = 0
	if ability in ("waterveil","waterbubble") or PokemonType.FIRE in types:
		v[93] = 0
	if oppo_ability == "magmaarmor":
		v[21] = 0
	if ability == "magmaarmor":
		v[94] = 0
	if oppo_ability == "limber" or PokemonType.ELECTRIC in oppo_types:
		v[22] = 0
	if ability == "limber" or PokemonType.ELECTRIC in types:
		v[95] = 0
	if oppo_ability in ("immunity","pastelveil"): 				#"pastelveil" not same in double
		v[23] = 0
	if PokemonType.POISON in oppo_types or PokemonType.STEEL in oppo_types:
		if ability != "corrosion":
			v[23] = 0
	if ability in ("immunity","pastelveil"):
		v[96] = 0
	if PokemonType.POISON in types or PokemonType.STEEL in types:
		v[96] = 0
	if oppo_ability in ("insomnia","vitalspirit","sweetveil"):
		v[24] = 0
		v[69] = 0
	if ability in ("insomnia","vitalspirit","sweetveil"):
		v[97] = 0	
	if Effect.YAWN in oppo_effects:
		v[24] = 1
	if Effect.YAWN in oppo_effects:
		v[69] = 0
	if Effect.YAWN in effects:
		v[97] = 1
	if oppo._mon._status:
		v[20:25] *= 0
	if mon._mon._status:
		v[93:98] *= 0

	if Effect.SAFEGUARD in oppo_effects or oppo_ability == "comatose":
		v[20:25] *= 0
		v[56] = 0
		v[69] = 0
	if Effect.SAFEGUARD in effects or ability == "comatose":
		v[93:98] *= 0

	if move._id == "rest":
		v[97] = 1

	if "cloudnine" in (ability,oppo_ability):
		v[83:87] /= 10	

	if move._id == "haze" and item != "assaultvest" and Effect.TAUNT not in effects:
		for i in range(0,7):
			v[6+i] = 0.01 - boosts[i]
			v[13+i] = - 0.01 - oppo_boosts[i]
	
	for i in range(0,7):
		v[6+i] = min(v[6+i],6-boosts[i])
		v[6+i] = max(v[6+i],-6-boosts[i])
		v[13+i] = min(v[13+i],6-oppo_boosts[i])
		v[13+i] = max(v[13+i],-6-oppo_boosts[i])
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
		Switch(),mon,oppo,_weather,_field,_side,_oppo_side,
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
	v1 = modified_switch_vectorize(mon,oppo,_weather,_field,_side,_oppo_side,_gets_ability,True)
	v2 = modified_switch_vectorize(mon,oppo,_weather,_field,_side,_oppo_side,False,1 - _oppo_gets_ability)
	return v1-v2


	


def pokemon_vectorize(mon:PokemonSet,weather,field, _counts_ability = True, _counts_item = True):
	v = np.zeros(30)
	if _counts_ability is True and mon._mon._ability:
		ability = mon._mon._ability		
	else:
		if isinstance(_counts_ability,str):
			ability = _counts_ability
		else:
			ability = ""

	
	if _counts_item is True and mon._mon._item:
		item = mon._mon._item		
	else:
		if isinstance(_counts_item,str): 
			item = _counts_item
		else:
			item = ""
	if ability == "klutz" or Effect.EMBARGO in mon._mon._effects:
		item = ""
	if Field.WONDER_ROOM in field: 
		item = ""

	types = mon._mon.types
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
			v[1] *= 1.5 							#test this
		if ability == "marvelscale":
			v[2] *= 1.5
		if ability == "quickfeet":
			v[5] *= 1.5			
		_status = mon._mon._status.name
		v[6] = 1
		if _status == "BRN":
			v[10] = 1
			if ability == "heatproof":
				dpt += 1/2
			else:
				dpt += 1
			if ability == "flareboost":
				v[3] *= 1.5
		if _status == "FRZ":
			v[9] = 4
		if _status == "PAR":			
			v[9] = 1/4
			v[11] = 1
			if ability != "quickfeet":
				v[5] *= 0.5
		if _status == "PSN":
			if ability == "poisonheal":
				hpt += 2
			else:
				dpt = 2
			if ability == "toxicboost":
				v[1] *= 1.5			
		if _status == "SLP":
			v[9] = 3 - mon._mon._status_counter
		if _status == "TOX":
			if ability == "poisonheal":
				hpt += 2
			else:
				dpt += ( 1 + mon._mon._status_counter )
			if ability == "toxicboost":
				v[1] *= 1.5

	if item in ("leftover","blacksludge"):
		hpt += 1	
	if item == "stickybarb":
		dpt += 2	
	if item == "choiceband" or ability == "gorillatactics":
		v[1] *= 1.5
		v[12] = 10
	if item == "choicespecs":
		v[3] *= 1.5
		v[12] = 10
	if item == "choicescarf":
		v[5] *= 1.5
		v[12] = 10
	if item == "assaultvest":
		v[4] *= 1.5
	if item == "eviolite":
		v[2] *= 1.5
		v[4] *= 1.5
	if item == "focussash" or ability == "sturdy":
		v[13] = 1
	if mon._mon._species in ("mimikyu","eiscue") and ability in ("disguise","iceface"): #test it
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
			if ability == "icebody":
				hpt += 1

	if Weather.SUNNYDAY in weather:
		if ability == "chlorophyll":
			v[5] *= 2
		if ability == "dryskin":
			dpt += 2
		if ability == "solarpower":
			v[3] *= 1.5
			dpt += 2
		if ability == "flowergift":
			v[1] *= 1.5
			v[4] *= 1.5
	if Weather.RAINDANCE in weather:
		if ability == "swiftswim":
			v[5] *= 2
		if ability == "raindish":
			hpt += 1
		if ability == "dryskin":
			hpt += 2
	if Weather.SANDSTORM in weather:
		if ability == "sandrush":
			v[5] *= 2
		if PokemonType.ROCK in types:
			v[20] *= 1.5
	if Weather.HAIL in weather:
		if ability == "slushrush":
			v[5] *= 2
	if Field.GRASSY_TERRAIN in field:
		hpt += 1
		if ability == "grasspelt":
			v[2] *= 1.5
	if Field.ELECTRIC_TERRAIN in field:
		if ability == "surgesurfer":
			v[5] *= 2
	if ability in ("hugepower","purepower"):
		v[1] *= 2
	if ability == "hustle":
		v[1] *= 1.5
	if ability == "unburden" and item == "lost":
		v[5] *= 2
	if ability == "slowstart":
		v[1] *= 0.5
		v[5] *= 0.5
	if ability == "defeatist" and v[0] < 0.5 :
		v[1] *= 0.5
		v[3] *= 0.5
	if item == "ironball":
		v[5] *= 0.5


	if item == "thickclub" and mon._mon._species in ("cubone","marowak","marowakalola"):
		v[1] *= 2
	if item == "lightball" and mon._mon._species == "pikachu":
		v[1] *= 2
		v[3] *= 2
	if item == "deepseatooth" and mon._mon._species == "clamperl":
		v[3] *= 2

	if item in ("laggingtail","fullincense") or ability == "stall":
		if Field.TRICK_ROOM in field:
			v[5] = 2000
		else:
			v[5] = 1

	effects = mon._mon._effects 
	if mon._mon.active:
		if Effect.AQUA_RING in effects:
			hpt += 1
			if item == "bigroot" :
				hpt += 0.3
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
			if item == "bigroot" :
				hpt += 0.3
		if Effect.LEECH_SEED in effects:
			dpt += 2
		if Effect.MAGMA_STORM in effects:
			dpt += 2
			v[15] = 5 - effects[Effect.MAGMA_STORM]
		if Effect.NIGHTMARE in effects:
			dpt += 4
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
		for i in range(0,4):
			v[17+i] = v[1+i]*boosts_to_multi(boosts[i])
		if item not in ("laggingtail","fullincense") and ability != "stall":
			v[21] = v[5]

	if Effect.HEAL_BLOCK not in effects:
		v[8] += hpt / 16
	if ability != "magicguard":
		v[8] -= dpt / 16




	v[24] = mon._mon._protect_counter
	
	if Effect.PERISH2 in effects:					#test whether PERISH2 or PERISH3
		v[8] -= 1

	return(v[:25])






















def move_vectorize(move:Move):
	v = np.zeros(100)
	v[0] = move.priority
	basepower = move.base_power

	if not basepower and "basePowerCallback" in move.entry:
		basepower = 60

	if move.entry["category"] == "Physical":
		v[1] = basepower
	if move.entry["category"] == "Special":
		v[2] = basepower

	if move._id == "fling":
		v[1] = 130
	if move._id in ("return","frustration"):
		v[1] = 102
	if move._id == "beatup":
		v[1] = 13
		v[30] = 4
			
	#v[3] for pp when pp<5

	v[4] = move.accuracy
	if move.entry["accuracy"] is True:
		v[4] = 10
	
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
		if move.entry.get("target",{}) in ("normal","allAdjacent","allAdjacentFoes","randomNormal","any"):
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
		v[23] = 4 * _chance
	

	if move._id == "triattack":								#these things are not correct but nvm
		v[20] = 1/15
		v[21] = 1/15
		v[22] = 1/15
	if move._id == "banefulbunker":
		v[23] = 0.3
	if move._id == "burningjealousy":
		v[20] = 0.3


	if move._id in ("boltbeak","fishiousrend"):				
		v[25] = 1
	if move._id == "payback":
		v[25] = -1

	# heal, absorb and recoil            ! pollenpuff / healpulse / floralhealing
	#self%

	if "heal" in move.entry and move.entry.get("target",{}) in ("self","allies"):
		v[26] = move.entry["heal"][0]/move.entry["heal"][1]
	if move._id in ("synthesis","morningsun","moonlight","shoreup"):
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
	if "recoil" in move.entry:
		v[27] = -move.entry["recoil"][0]/move.entry["recoil"][1]
	# highjumpkick
	if "hasCrashDamage" in move.entry:
		v[28] = -1/2
	# strengthsap
	if move._id in ("strengthsap","foulplay"):
		v[29] = 1

	#flags 30: "multihit"
	if "contact" in move.entry["flags"]:
		v[31] = 1
	if "sound" in move.entry["flags"]:
		v[32] = 1
	if "powder" in move.entry["flags"]:						
		v[33] = 1		
	if move._id == "pursuit":
		v[34] = 1
	if "charge" in move.entry["flags"]:
		v[35] = 1
		if "condition" in move.entry:
			v[36] = 1
	if "recharge" in move.entry["flags"]:						#when simulating, next turn v = 0
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
	if move._id in ("shellsidearm","photongeyser"):
		v[49] = 0.5
	if "isFutureMove" in move.entry:
		v[50] = 1
	if move._id == "perishsong":
		v[50] = 2
	if move._id == "counter":
		v[51] = 2
	if move._id == "mirrorcoat":
		v[52] = 2
	if move._id == "metalburst":
		v[51] = 1.5
		v[52] = 1.5
	if move._id == "sucherpunch":				#nvm
		v[51] = 0.2
		v[52] = 0.2
	if "damage" in move.entry:
		if move.entry["damage"] == "level":
			v[53] = level
		else:
			v[53] = move.entry["damage"]
	if move._id == "finalgambit":
		v[53] = 2*level
	if move._id in ("naturesmadness","superfang"):
		v[53] = 1.2*level

# this slot53 for passive damage side effects	slot54 for break substitute







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

											#slot 63 empty
	if _volatilestatus == "lockedmove":
		v[64] = _chance
	if _volatilestatus == "roost":
		v[65] = _chance
	if _volatilestatus == "magnetrise":
		v[65] = -1 * _chance
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
		v[66] = 2


	if move._id in ("rapidspin","defog"):
		v[78] = 1
	if move._id == "lashout":
		v[79] = 1
	if move._id == "burningjealousy":
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
	if move._id in ("waterspout","eruption","dragonenergy"):
		v[92] = 1
	if move._id == "focuspunch":
		v[92] = 5
	if move._id == "beakblast":
		v[92] = -0.5
	if move._id in ("avalanche","revenge"):
		v[92] = -1
	if move._id == "shelltrap":
		v[92] = -5

#93"brn":#94"frz":#95"par":#96"psn":#97"slp":

	if move._id == "rest":
		v[97] = 1
	
#98 use item #99 use oppo_item	


	return v



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
	return v[:10]

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
		v[7] = v[2]+v[3]+v[4]+v[5]
		v[8] = v[7] - min(v[0],1) - min(v[1],1)


	return v[:9]


def _is_grounded(mon:PokemonSet,field:Optional[Dict]):
	if field:
		if Field.GRAVITY in field:
			return True
	if Effect.INGRAIN in mon._mon._effects:
		return True
	if Effect.SMACK_DOWN in mon._mon._effects:
		return True
	if field and Field.WONDER_ROOM not in field and mon._mon._item == "ironball" and mon._mon._ability != "klutz":
		return True
	if PokemonType.FLYING in mon._mon.types:
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

def grassknotpower(w):
	if w < 0:
		return 0
	if w < 10:
		return 20
	if w < 25:
		return 40
	if w < 50:
		return 60
	if w < 100:
		return 80
	if w < 200:
		return 100
	else:
		return 120

def heatcrashpower(mw,ow):
	r = mw / ow
	if r < 0:
		return 0
	if r < 2:
		return 40
	if r < 3:
		return 60
	if r < 4:
		return 80
	if r < 5:
		return 100
	else:
		return 120

def electroballpower(mon:PokemonSet):
	r = mon._stats[0] / mon._stats[1]
	if r < 2/48:
		return 200
	if r < 5/48:
		return 150
	if r < 10/48:
		return 100
	if r < 17/48:
		return 80
	if r < 33/48:
		return 40		
	else:
		return 20

def reversalpower(ms,os):
	r = ms / o_stats
	if r < 0:
		return 0
	if r < 1:
		return 40
	if r < 2:
		return 60
	if r < 3:
		return 80
	if r < 4:
		return 120
	else:
		return 150



def vectordebug(v):
	for i in range (0,len(v)):
		if v[i] != 0:
			print("v[%d] ="%i,v[i])





def vector_dict(battle,battle2,alive_mon,alive_oppo):
	vector_dict = {}

	m = np.zeros((len(alive_mon),len(alive_oppo)))
	for _mon in alive_mon:
		mon = PokemonSet(battle._team[_mon])
		vector_dict[_mon] = {}
		for _oppo in alive_oppo:
			oppo = PokemonSet(battle2._team[_oppo])
			vector_dict[_mon][_oppo] = {}
			for move in mon._mon.moves:
				move_vector = modified_move_vector(Move(move),mon,oppo,battle._weather,battle._fields,battle._side_conditions,battle._opponent_side_conditions)
				vector_dict[_mon][_oppo][move] = move_vector
	return vector_dict

def switch_dict(battle,battle2,alive_mon,alive_oppo):
	switch_dict = {}

	m = np.zeros((len(alive_mon),len(alive_oppo)))
	for _mon in alive_mon:
		mon = PokemonSet(battle._team[_mon])
		switch_dict[_mon] = {}
		for _oppo in alive_oppo:
			oppo = PokemonSet(battle2._team[_oppo])
			switch_dict[_mon][_oppo] = modified_move_vector(Switch(),mon,oppo,battle._weather,battle._fields,battle._side_conditions,battle._opponent_side_conditions)
	return switch_dict


def threating_rate_dict(mon_vector_dict,oppo_vector_dict,alive_mon,alive_oppo):
	def priority(v):
		return v[0]
	def prioried_damage(v):
		if v[1] + v[2] +v[53]:
			return v[1] + v[2] +v[53] +v[0]*10
		else:
			return 0
	def damage(v):
		return v[1] + v[2] +v[53]
	def heal(v):
		return v[26] + v[27]
	def simplify(v):
		return [v[0],v[1] + v[2] +v[53],v[26] + v[27]]
	def threating_rate(remain_hp,oppo_remain_hp,mq,mt,mh,oq,ot,oh):
		if oh[2] > mt[1]:
			if oppo_remain_hp > mq[1] or oh[0] > mq[0]:
				if oppo_remain_hp > mt[1] or oh[0] > mt[0]:
					if mh[2] > ot[1]:
						if remain_hp > oq[1] or mh[0] > oq[0]:
							if remain_hp > ot[1] or mh[0] > ot[0]:
								return max(0.2,min(5,(mt[1]+0.001)/(ot[1]+0.001)))
					else:
						return max(0.2,min(5,(mt[1]+0.001)))
		else:
			if mh[2] > ot[1]:
				if remain_hp > oq[1] or mh[0] > oq[0]:
					if remain_hp > ot[1] or mh[0] > ot[0]:
						return max(0.2,min(5,(1/(ot[1]+0.001))))
		konumber = int(oppo_remain_hp/(mt[1]-ot[2]+0.001))
		oppo_konumber = int(remain_hp/(ot[1]-mt[2]+0.001))
		number = min(konumber,oppo_konumber)	
		remain_hp -= (ot[1]-mt[2]) * number
		oppo_remain_hp -= (mt[1]-ot[2]) * number
		if mq[0] >= oq[0] and mq[1] > oppo_remain_hp:
			oppo_remain_hp = 0
		if oq[0] >= mq[0] and oq[1] > remain_hp:
			remain_hp = 0
		if remain_hp and oppo_remain_hp:
			if mt[0] > ot[0]:
				if mt[1] > oppo_remain_hp:
					oppo_remain_hp = 0
					if oq[0] > mt[0]:
						remain_hp -= oq[1]
				else:
					remain_hp = 0
					oppo_remain_hp -= mt[1]	
			if mt[0] < ot[0]:
				if ot[1] > remain_hp:
					remain_hp = 0
					if mq[0] > ot[0]:
						oppo_remain_hp -= mq[1]	
				else:
					oppo_remain_hp = 0
					remain_hp -= ot[1]
			if mt[0] == ot[0]:
				if mt[1] > oppo_remain_hp:
					oppo_remain_hp = 0
					if oq[0] > mt[0]:
						remain_hp -= oq[1]
				if ot[1] > remain_hp:
					remain_hp = 0
					if mq[0] > ot[0]:
						oppo_remain_hp -= mq[1]	
		if remain_hp == 0 and oppo_remain_hp == 0:
			return 1
		if remain_hp == 0:
			return max(0.2,min(5,(1-oppo_remain_hp)))
		if oppo_remain_hp == 0:
			return max(0.2,min(5,1/(1.001-remain_hp)))
		return 1

	trm = {}

	for _mon in mon_vector_dict: 
		trm[_mon] = {}
		remain_hp = alive_mon[_mon]
		for _oppo in mon_vector_dict[_mon]:
			oppo_remain_hp = alive_oppo[_oppo]
			moveset = mon_vector_dict[_mon][_oppo]
			oppo_moveset = oppo_vector_dict[_oppo][_mon]
			most_threating_quick_move = max(moveset, key=lambda move: prioried_damage(moveset[move]))
			most_threating_move = max(moveset, key=lambda move: damage(moveset[move]))
			heal_move = max(moveset, key=lambda move: heal(moveset[move]))
			oppo_most_threating_quick_move = max(oppo_moveset, key=lambda move: prioried_damage(oppo_moveset[move]))
			oppo_most_threating_move = max(oppo_moveset, key=lambda move: damage(oppo_moveset[move]))
			oppo_heal_move = max(oppo_moveset, key=lambda move: heal(oppo_moveset[move]))

			mq = simplify(moveset[most_threating_quick_move])
			mt = simplify(moveset[most_threating_move])
			mh = simplify(moveset[heal_move])
			oq = simplify(oppo_moveset[oppo_most_threating_quick_move])
			ot = simplify(oppo_moveset[oppo_most_threating_move])
			oh = simplify(oppo_moveset[oppo_heal_move])


			trm[_mon][_oppo] = threating_rate(remain_hp,oppo_remain_hp,mq,mt,mh,oq,ot,oh)
			
	return trm
'''
	#other special things when simulating : 
	xx swap, magicmirror, etc 
	rapid spin (leechseed off), knockoff,switch, steadfast
	unfreeze self move
	regenirator
	weather grabbing
	Fishious Rend,Bolt Beak
	imposter
	illusion
	substitute hp%
	mummy
	destinybond
	Burning Jealousy
	Stakeout
	when switch, check if will get hit
	Screen Cleaner
	Quick Draw, Quick Claw
	Unseen fist
	mirrorcoat,etc
	sucker punch
	Ditto
'''

