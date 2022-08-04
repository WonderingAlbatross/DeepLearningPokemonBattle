import orjson
import numpy as np
import vector_converter as vc
from poke_env.environment.move import Move

uselessmove = ("absorb","acid","afteryou","allyswitch","armthrust","aromaticmist","assist","astonish","attract","barrage","batonpass","beakblast","bestow","bide","block","branchpoke","bubble","camouflage","celebrate","charge","coaching","confide","confuseray","constrict","conversion","conversion2","copycat","corrosivegas","courtchange","craftyshield","defensecurl","doubleslap","doubleteam","echoedvoice","electrify","embargo","ember","endure","fairylock","fairywind","falseswipe","flash","flatter","floralhealing","flowershield","focusenergy","followme","forestscurse","furyattack","furycutter","gearup","gravity","growl","grudge","guardsplit","guardswap","gust","happyhour","harden","healblock","healingwish","healpulse","heartswap","helpinghand","holdback","holdhands","howl","iceball","instruct","iondeluge","kinesis","laserfocus","leafage","leer","lick","lockon","luckychant","magiccoat","magicpowder","magicroom","magneticflux","magnetrise","magnitude","matblock","meanlook","meditate","mefirst","megadrain","metronome","mimic","mindreader","miracleeye","mirrorcoat","mirrormove","mist","mudslap","mudsport","naturalgift","naturepower","nightmare","odorsleuth","payday","peck","playnice","poisonsting","pound","powder","powdersnow","powersplit","powerswap","powertrick","powertrip","present","psychup","psychoshift","psywave","purify","quash","quickguard","rage","ragepowder","recycle","reflecttype","revenge","roleplay","rollout","rototiller","round","safeguard","sandattack","scratch","sharpen","sheercold","shelltrap","sketch","skillswap","sleeptalk","smokescreen","snatch","snore","soak","speedswap","spiderweb","spikyshield","spite","splash","spotlight","stockpile","storedpower","struggle","stuffcheeks","supersonic","swallow","sweetkiss","tackle","tailwhip","tarshot","teatime","teeterdance","telekinesis","thundershock","torment","transform","trickortreat","twister","venomdrench","vinewhip","vitalthrow","watergun","watersport","wideguard","withdraw","wonderroom","sheercold","fissure","guillotine","horndrill")

with open("learnset.json") as learnset:
	LEARNSET = orjson.loads(learnset.read())


S_LEARNSET = {}

for pokemon in LEARNSET:
	if pokemon == "tomohawk":
		break
	S_LEARNSET[pokemon] = []
	if "learnset" in LEARNSET[pokemon]:
		for move in LEARNSET[pokemon]["learnset"]:
			if move not in uselessmove:
				for m in LEARNSET[pokemon]["learnset"][move]:
					if m.startswith("8"):
						S_LEARNSET[pokemon] += [move]
						break
	if "eventData" in LEARNSET[pokemon]:
		for event in LEARNSET[pokemon]["eventData"]:
			if event["generation"] == 8:
				for move in event["moves"]:
					if move not in S_LEARNSET[pokemon] and move not in uselessmove:
						S_LEARNSET[pokemon] += [move]

T_LEARNSET = {}
for pokemon in S_LEARNSET:
	T_LEARNSET[pokemon] = {}
	T_LEARNSET[pokemon]["physical"] = []
	T_LEARNSET[pokemon]["special"] = []
	T_LEARNSET[pokemon]["protect"] = []
	T_LEARNSET[pokemon]["boost"] = []
	T_LEARNSET[pokemon]["disturb"] = []
	T_LEARNSET[pokemon]["switch"] = []
	T_LEARNSET[pokemon]["recover"] = []
	T_LEARNSET[pokemon]["other"] = []
	for move in S_LEARNSET[pokemon]:
		v = vc.move_vectorize(Move(move))
		if v[38]:
			T_LEARNSET[pokemon]["switch"] += [move]
			print(pokemon,move,"switch")
		elif v[44]+v[45]+v[46]:
			T_LEARNSET[pokemon]["protect"] += [move]
			print(pokemon,move,"protect")
		elif sum(v[6:13]) > 0.9:
			T_LEARNSET[pokemon]["boost"] += [move]
			print(pokemon,move,"boost")
		elif sum(v[13:20]) < -0.9 or v[3]+sum(v[20:25])+v[39]+v[50]+v[51]+v[52]+sum(v[56:63])+sum(v[68:82]) > 0.9 or move in ("haze","endeavor","finalgambit"):
			T_LEARNSET[pokemon]["disturb"] += [move]
			print(pokemon,move,"disturb")
		elif v[26] > 0.2 or v[43] or move in ("painsplit","strengthsap"):
			T_LEARNSET[pokemon]["recover"] += [move]
			print(pokemon,move,"recover")
		elif v[1]:
			T_LEARNSET[pokemon]["physical"] += [move]
			print(pokemon,move,"physical")
		elif v[2]:
			T_LEARNSET[pokemon]["special"] += [move]
			print(pokemon,move,"special")
		else:
			T_LEARNSET[pokemon]["other"] += [move]
			print(pokemon,move,"other")

with open("new_learnset.json","wb") as new_learnset:
	new_learnset.write(orjson.dumps(T_LEARNSET))