from poke_env.environment.move import Move
import numpy as np


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
	
	v[3] = np.amax(v[1:2]) * 0.04 #std error
	v[50] = 1
	if isinstance(move.entry.get("multihit",{}),list):
		v[3] = np.amax(v[1:2]) * 1.07
		v[1:3] *= 19/6
		v[50] = 3
	else:
		if move.entry.get("multihit",{}) == 2:
			v[3] = np.amax(v[1:2]) * 0.06
			v[1:3] *= 2
			v[50] = 2
		else:
			if move.entry.get("multihit",{}) == 3:
				if move._id == "surgingstrikes":
					v[3] = np.amax(v[1:2]) * 0.07
					v[1:3] *= 3
					v[50] = 3
				else:
					v[3] = np.amax(v[1:2]) * 1.67
					v[1:3] *= 5.23
					v[50] = 3

	v[4] = move.accuracy
	if move.entry["accuracy"] is True:
		v[4] = 10
	
	v[5] = move.crit_ratio
	if move.entry.get("willCrit",{}):
		v[5] = 10
	
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

	#enemyboosts
	_chance = 1
	_boosts = {}
	if move.entry.get("boosts",{}):
		if move.entry.get("target",{}) in ("normal","allAdjacent","allAdjacentFoes"):
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

	# heal, absorb and recoil
	
	#volatile status

	#flags

	#weather, room, field, and side

	return v[20:30]