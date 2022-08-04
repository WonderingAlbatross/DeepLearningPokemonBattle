import orjson
import numpy as np
import vector_converter as vc
from poke_env.environment.move import Move

with open("moves.json") as movedata:
	MOVEDICT = orjson.loads(movedata.read())



uselessmove = []
with open("uselessmove.txt","w") as new_learnset:
	for move in MOVEDICT:
		if "isZ" in MOVEDICT[move]:
			continue
		if "ismax" in MOVEDICT[move]:
			continue
		v = vc.move_vectorize(Move(move))
		w = np.zeros(100)
		w[0] = 0.7*(v[1]+v[2])
		w[1] = 0.02*(1+v[30])
		w[2] = 0.02*(1+v[30])
		w[3] = 0.05                      
		w[6:13] = np.ones(7)*0.5
		w[13:20] = -np.ones(7)*0.5
		w[20:25] =  np.ones(5)
		w[25] = 0.2
		w[26] = 2
		w[27] = 0.2
		w[28] = (1-v[4])*0.5
		w[35] = -0.1
		w[36] = 0.1
		w[37] = -0.1
		w[41] = -0.05
		w[42] = 0.05
		w[43] = 0.05
		w[44] = 0.1
		w[45] = 0.05
		w[46] = 0.05
		w[47] = 0.1
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
		w[70:78] = np.ones(8)*1
		w[78] = 1
		w[81] = 1
		w[82] = 1
		w[83:91] = np.ones(8)
		w[93:98] = np.ones(5)
		w[98] = -0.1
		w[99] = 0.1
		if w.dot(v) < 1 :
			print(move,w.dot(v))
			new_learnset.write("\""+move+"\",")


