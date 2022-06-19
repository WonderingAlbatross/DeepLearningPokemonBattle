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

	v[3] = np.amax(v[1:2]) * 0.04 #std error
	v[30] = 1
	if isinstance(move.entry.get("multihit",{}),list):
		v[3] = np.amax(v[1:2]) * 1.07
		v[1:3] *= 19/6
		v[30] = 3
	else:
		if move.entry.get("multihit",{}) == 2:
			v[3] = np.amax(v[1:2]) * 0.06
			v[1:3] *= 2
			v[30] = 2
		else:
			if move.entry.get("multihit",{}) == 3:
				if move._id == "surgingstrikes":
					v[3] = np.amax(v[1:2]) * 0.07
					v[1:3] *= 3
					v[30] = 3
				else:
					v[3] = np.amax(v[1:2]) * 1.67
					v[1:3] *= 5.23
					v[30] = 3

	v[4] = move.accuracy
	if move.entry["accuracy"] is True:
		v[4] = 10
	
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
	if _status == "frz":
		v[21] = _chance
	if _status == "par":
		v[22] = _chance
	if _status == "psn":
		v[23] = _chance
	if _status == "slp":
		v[24] = _chance
	if _status == "tox":
		v[25] = _chance

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
	if move._id in ("synthesis","morningsun","moonlight","shoreup"):
		v[26] = 1/2
	if "mindBlownRecoil" in move.entry or move._id == "bellydrum":
		v[26] = -1/2
	if move._id == "substitute":
		v[26] = -1/4
	if move._id == "clangoroussoul":
		v[26] = -1/3
	
	#damage%
	if "drain" in move.entry:
		v[27] = move.entry["drain"][0]/move.entry["drain"][1]
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
	if move._id in ("protect","detect","spikyshield","banefulbunker"):
		v[46] = 1
	if "breaksProtect" in move.entry:
		v[47] = 1
	if "selfdestruct" in move.entry:
		v[48] = 1
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
			v[54] = move.entry["damage"]


	#volatile status


	#weather, room, field, and side

	#weather/field correction (type, synthesis, etc)



	return v[:52]