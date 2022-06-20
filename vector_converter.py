from poke_env.environment.move import Move
import numpy as np

level = 80
def vectorize(m):
	v = np.zeros(100)
	if isinstance(m, Move):
		move = m
	else:
		if isinstance(m, str):
			move = Move(m)             #only for testing!
		else:
			return v

	v[0] = move.priority
	
	if move.entry.get("category",{}) == "Physical":
		v[1] = move.base_power
	if move.entry.get("category",{}) == "Special":
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
	if move._id == "facade"
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

	
	#selfboosts
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
		v[89] = -_chance
	if _status == "frz":
		v[21] = _chance
		v[89] = -_chance
	if _status == "par":
		v[22] = _chance
		v[89] = -_chance
	if _status == "psn":
		v[23] = _chance
		v[89] = -_chance
	if _status == "slp":
		v[24] = _chance
		v[89] = -1
		v[87] = -1
	if _status == "tox":
		v[25] = _chance
		v[89] = -_chance

	if move._id == "triattack":
		v[20] = 1/15
		v[21] = 1/15
		v[22] = 1/15
	if move._id == "banefulbunker":
		v[23] = 0.3

	# heal, absorb and recoil            ! pollenpuff / healpulse / floralhealing
	#self%
	if "heal" in move.entry and move.entry.get("target",{}) in ("self","allies"):
		v[26] = move.entry["heal"][0]/move.entry["heal"][1]
	if move._id in ("synthesis","morningsun","moonlight"):
		v[26] = 1/2
		v[83] = 1
		v[84] = -1
		v[85] = -1
		v[86] = -1
	if move._id == "shoreup":
		v[26] = 1/2
		v[85] = 1
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
	if move._id == "strengthsap":
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
		v[42] = 1	
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
		v[54] = _chance
	if _volatilestatus == "partiallytrapped":
		v[55] = _chance
	if _volatilestatus == "confusion":
		v[56] = _chance
		v[89] = -_chance
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
		v[87] = -1

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
		v[79] = 1
	if "onModifyType" in move.entry:
		v[80] = 1

	if move._id in ("knockoff","trick","switcheroo"):
		v[81] = 1
	if move._id in ("gastroacid","coreenforcer","worryseed","simplebeam","entrainment","skillswap"):
		v[82] = 1


	if "weather" in move.entry:
		v[83:87] = np.ones(4)*0.5
	if "field" in move.entry:
		v[87:91] = np.ones(4)*0.5

	#weather and field adjustment
	if move.entry.get("type","") == "Fire":
		v[83] = 1
		v[84] = -1
		if move._id == "sunnyday":
			v[83] == -2
	if move.entry.get("type","") == "Water":
		v[83] = -1
		v[84] = 1
		if move._id == "raindance":
			v[84] == -2
	if move._id == "sandstorm":
		v[85] == -2
	if move._id == "hail":
		v[86] == -2
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

	if move.entry.get("type","") == "Electric":
		v[87] = 1
		if move._id == "risingvoltage": 
			v[87] = 2
		if move._id == "electricterrain": 
			v[87] = -2			
	if move.entry.get("type","") == "Grass":
		v[88] = 1
		if move._id == "grassyglide": 
			v[88] = 3
		if move._id == "grassyterrain": 
			v[88] = -2		
	if move._id in ("bulldoze","earthquake"): 
		v[88] = -1		
	if move.entry.get("type","") == "Dragon":
		v[89] = -1
	if move._id == "mistyexplosion":
		v[89] = 1
	if move._id == "mistyterrain": 
		v[89] = -2
	if move.entry.get("type","") == "Psychic":
		v[90] = 1
		if move._id == "expandingforce": 
			v[90] = 2
		if move._id == "psychicterrain": 
			v[90] = -2
	if v[0] > 0 and move.entry.get("target",{}) in ("normal","allAdjacent","allAdjacentFoes","any"):
		v[90] = -1
	if move._id == "terrainpulse":
		v[87:91] = np.ones(4)*2



	return v[:91]